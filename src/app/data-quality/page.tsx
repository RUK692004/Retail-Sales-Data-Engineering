'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ColumnDef } from '@tanstack/react-table';
import {
  ShieldCheck,
  CheckCircle,
  AlertOctagon,
  Activity,
  FileCheck,
  Check,
  AlertTriangle,
  Info,
  Filter,
  RefreshCw,
} from 'lucide-react';
import { dataQualityApi } from '@/lib/api';
import {
  DataQualityIssue,
  DataQualityQueryParams,
  ValidationCategoryType,
  IssueSeverity,
} from '@/types';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/PageHeader';
import { KpiCard } from '@/components/dashboard/KpiCard';
import { DataTable } from '@/components/ui/DataTable';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { CardSkeleton } from '@/components/ui/LoadingSkeleton';
import { ErrorState } from '@/components/ui/ErrorState';

export default function DataQualityPage() {
  const [params, setParams] = useState<DataQualityQueryParams>({
    page: 1,
    pageSize: 10,
    search: '',
    category: 'ALL',
    severity: 'ALL',
  });

  const { data: dqSummary, isLoading: summaryLoading, isError: summaryError, refetch: refetchSummary } = useQuery({
    queryKey: ['data-quality-summary'],
    queryFn: () => dataQualityApi.getSummary(),
  });

  const { data: dqIssuesRes, isLoading: issuesLoading } = useQuery({
    queryKey: ['data-quality-issues', params],
    queryFn: () => dataQualityApi.getIssues(params),
  });

  const issueColumns: ColumnDef<DataQualityIssue>[] = [
    {
      accessorKey: 'issueId',
      header: 'Issue ID',
      cell: ({ row }) => (
        <span className="font-mono font-semibold text-rose-600">{row.original.issueId}</span>
      ),
    },
    {
      accessorKey: 'severity',
      header: 'Severity',
      cell: ({ row }) => {
        const sev = row.original.severity;
        return (
          <span
            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold ${
              sev === 'CRITICAL'
                ? 'bg-rose-100 text-rose-800 border border-rose-300'
                : sev === 'WARNING'
                ? 'bg-amber-100 text-amber-800 border border-amber-300'
                : 'bg-sky-100 text-sky-800 border border-sky-300'
            }`}
          >
            {sev === 'CRITICAL' ? (
              <AlertOctagon className="w-3 h-3 text-rose-600" />
            ) : sev === 'WARNING' ? (
              <AlertTriangle className="w-3 h-3 text-amber-600" />
            ) : (
              <Info className="w-3 h-3 text-sky-600" />
            )}
            {sev}
          </span>
        );
      },
    },
    {
      accessorKey: 'category',
      header: 'Category / Rule',
      cell: ({ row }) => (
        <div>
          <div className="font-semibold text-slate-900">{row.original.ruleViolated}</div>
          <div className="text-[10px] text-slate-500 font-mono">{row.original.category}</div>
        </div>
      ),
    },
    {
      accessorKey: 'targetTable',
      header: 'Target Schema & Col',
      cell: ({ row }) => (
        <span className="font-mono text-xs text-slate-700">
          {row.original.targetTable}.{row.original.targetColumn}
        </span>
      ),
    },
    {
      accessorKey: 'recordIdentifier',
      header: 'Record Key',
      cell: ({ row }) => (
        <span className="font-mono text-xs font-semibold text-slate-800">
          {row.original.recordIdentifier}
        </span>
      ),
    },
    {
      accessorKey: 'invalidValue',
      header: 'Invalid Input',
      cell: ({ row }) => (
        <span className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 font-mono text-xs border border-rose-200">
          {row.original.invalidValue}
        </span>
      ),
    },
    {
      accessorKey: 'recommendation',
      header: 'ETL Recommendation',
      cell: ({ row }) => (
        <p className="text-xs text-slate-600 leading-relaxed max-w-sm truncate">
          {row.original.recommendation}
        </p>
      ),
    },
  ];

  return (
    <DashboardLayout>
      <PageHeader
        title="Data Quality & ETL Ingestion Pipeline"
        subtitle="Automated schema checks, foreign key constraint validation, deduplication logs, and quarantine exception rules"
        action={
          <button
            onClick={() => refetchSummary()}
            className="inline-flex items-center gap-2 px-3 py-2 bg-slate-900 text-white hover:bg-slate-800 text-xs font-medium rounded-lg shadow-xs transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Trigger Validation Run
          </button>
        }
      />

      {summaryError ? (
        <ErrorState onRetry={() => refetchSummary()} />
      ) : (
        <div className="space-y-6">
          {/* Top Level Pipeline Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {summaryLoading || !dqSummary ? (
              Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)
            ) : (
              <>
                <KpiCard
                  title="Records Processed"
                  value={dqSummary.totalRecordsProcessed.toLocaleString()}
                  subtitle="Total ingested today"
                  icon={FileCheck}
                />
                <KpiCard
                  title="Valid Records"
                  value={dqSummary.totalValidRecords.toLocaleString()}
                  subtitle={`${dqSummary.overallPassRate}% pass rate`}
                  icon={CheckCircle}
                  variant="success"
                />
                <KpiCard
                  title="Quarantine Invalid Records"
                  value={dqSummary.totalInvalidRecords.toLocaleString()}
                  subtitle="Exceptions routed to DLQ"
                  icon={AlertOctagon}
                  variant="danger"
                />
                <KpiCard
                  title="Pipeline Status"
                  value={dqSummary.pipelineStatus}
                  subtitle={`Last run: ${
                    dqSummary.lastRunTimestamp
                      ? new Date(dqSummary.lastRunTimestamp).toLocaleTimeString()
                      : 'Never run'
                  }`}
                  icon={Activity}
                  variant="default"
                />
              </>
            )}
          </div>

          {/* Validation Rule Categories Cards */}
          {dqSummary && (
            <div className="space-y-3">
              <h3 className="text-base font-bold text-slate-900">Validation Rule Category Matrix</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dqSummary.categories.map((cat) => (
                  <div
                    key={cat.category}
                    className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-colors"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
                          {cat.category}
                        </span>
                        <StatusBadge status={cat.status} />
                      </div>
                      <h4 className="text-sm font-bold text-slate-900">{cat.name}</h4>
                      <p className="text-xs text-slate-500 mt-1 leading-relaxed">{cat.description}</p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Pass Rate</span>
                        <span className="font-bold text-slate-900">{cat.passRatePercentage}%</span>
                      </div>
                      <div className="text-right">
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Evaluated / Failed</span>
                        <span className="font-mono font-medium text-slate-700">
                          {cat.passedCount.toLocaleString()} /{' '}
                          <span className="text-rose-600 font-bold">{cat.failedCount}</span>
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Validation Issues Data Table */}
          <div className="space-y-2">
            <h3 className="text-base font-bold text-slate-900">Recent Validation Exceptions Table</h3>
            <DataTable
              columns={issueColumns}
              data={dqIssuesRes?.data || []}
              isLoading={issuesLoading}
              totalCount={dqIssuesRes?.meta?.total || 0}
              page={params.page || 1}
              pageSize={params.pageSize || 10}
              onPageChange={(page) => setParams((prev) => ({ ...prev, page }))}
              onPageSizeChange={(pageSize) => setParams((prev) => ({ ...prev, pageSize, page: 1 }))}
              searchValue={params.search}
              onSearchChange={(search) => setParams((prev) => ({ ...prev, search, page: 1 }))}
              searchPlaceholder="Search issue ID, table name, record key, or rule..."
              filtersSlot={
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1.5 text-xs text-slate-500">
                    <Filter className="w-3.5 h-3.5" />
                    <span>Severity:</span>
                  </div>
                  <select
                    value={params.severity}
                    onChange={(e) =>
                      setParams((prev) => ({
                        ...prev,
                        severity: e.target.value as IssueSeverity | 'ALL',
                        page: 1,
                      }))
                    }
                    className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="ALL">All Severities</option>
                    <option value="CRITICAL">Critical</option>
                    <option value="WARNING">Warning</option>
                    <option value="INFO">Info</option>
                  </select>

                  <select
                    value={params.category}
                    onChange={(e) =>
                      setParams((prev) => ({
                        ...prev,
                        category: e.target.value as ValidationCategoryType | 'ALL',
                        page: 1,
                      }))
                    }
                    className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="ALL">All Categories</option>
                    <option value="SCHEMA">Schema</option>
                    <option value="NULL_CHECK">Null Check</option>
                    <option value="DUPLICATE">Duplicate</option>
                    <option value="CUSTOMER_FK">Customer FK</option>
                    <option value="SKU_FK">SKU FK</option>
                    <option value="DATA_TYPE">Data Type</option>
                  </select>
                </div>
              }
            />
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
