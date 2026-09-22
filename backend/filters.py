"""
The frontend's "no filter" sentinel for every dropdown (storeId, category,
status, loyaltyTier, severity, ...) is the literal string "ALL" — see
src/mocks/handlers.ts's `!== 'ALL'` checks, which every filter dropdown in
src/app/*/page.tsx relies on. Routers must treat "ALL" the same as the
param not being passed at all, or it gets used as a real filter value
(e.g. `WHERE store_id = 'ALL'`, a Postgres integer-cast error).
"""


def clean_filter(value: str | None) -> str | None:
    return None if value in (None, "", "ALL") else value
