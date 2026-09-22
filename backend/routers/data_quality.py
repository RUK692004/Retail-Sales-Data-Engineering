"""
GET /api/data-quality/summary
GET /api/data-quality/issues

See quality_checks.py for what's actually being checked and why. Two
honesty notes specific to these endpoints:
  - lastRunTimestamp is always null — there's no persisted pipeline run
    history to read (run_quality_checks in the Airflow DAG only logs to
    Airflow's own logs). These checks run live, on request.
  - Each issue's `timestamp` is when this check ran, not when the bad
    record was originally written — fact_sales has no created_at column,
    so there's no way to know that.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Query

from db import query_one
from quality_checks import run_all_checks

router = APIRouter()


@router.get("/data-quality/summary")
def data_quality_summary():
    checks = run_all_checks()

    categories = [{k: v for k, v in c.items() if k != "issues"} for c in checks]
    total_issues = sum(len(c["issues"]) for c in checks)

    duplicate_check = next(c for c in checks if c["category"] == "DUPLICATE")
    total_processed = query_one("SELECT COUNT(*) AS n FROM fact_sales")["n"]
    total_invalid = duplicate_check["failedCount"]  # only real per-row defects in fact_sales itself
    total_valid = total_processed - total_invalid

    return {
        "data": {
            "pipelineStatus": "HEALTHY" if all(c["status"] == "PASSED" for c in checks) else "DEGRADED",
            "lastRunTimestamp": None,
            "totalRecordsProcessed": total_processed,
            "totalValidRecords": total_valid,
            "totalInvalidRecords": total_invalid,
            "overallPassRate": round(total_valid / total_processed * 100, 2) if total_processed else 100.0,
            "categories": categories,
            "issuesCountBySeverity": {
                "critical": total_issues,
                "warning": 0,
                "info": 0,
            },
        }
    }


@router.get("/data-quality/issues")
def data_quality_issues(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    search: str | None = None,
    category: str | None = Query(None, pattern="^(SCHEMA|NULL_CHECK|DUPLICATE|CUSTOMER_FK|SKU_FK|DATA_TYPE)$"),
    severity: str | None = Query(None, pattern="^(CRITICAL|WARNING|INFO)$"),
):
    checks = run_all_checks()
    now = datetime.now(timezone.utc).isoformat()

    all_issues = []
    for check in checks:
        for issue in check["issues"]:
            all_issues.append({**issue, "timestamp": now})

    if category:
        all_issues = [i for i in all_issues if i["category"] == category]
    if severity:
        all_issues = [i for i in all_issues if i["severity"] == severity]
    if search:
        needle = search.lower()
        all_issues = [
            i for i in all_issues
            if needle in i["recordIdentifier"].lower() or needle in str(i["invalidValue"]).lower()
        ]

    total = len(all_issues)
    start = (page - 1) * pageSize
    page_issues = all_issues[start:start + pageSize]

    data = [{
        "issueId": f"DQ-ERR-{start + idx + 1}",
        "timestamp": issue["timestamp"],
        "category": issue["category"],
        "ruleViolated": issue["ruleViolated"],
        "targetTable": issue["targetTable"],
        "targetColumn": issue["targetColumn"],
        "recordIdentifier": issue["recordIdentifier"],
        "severity": issue["severity"],
        "invalidValue": issue["invalidValue"],
        "recommendation": issue["recommendation"],
    } for idx, issue in enumerate(page_issues)]

    return {
        "data": data,
        "meta": {
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "totalPages": (total + pageSize - 1) // pageSize if total else 1,
        },
    }
