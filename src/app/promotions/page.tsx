'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ColumnDef } from '@tanstack/react-table';
import { Tag, Filter, Percent, Calendar } from 'lucide-react';
import { promotionsApi } from '@/lib/api';
import { Promotion, PromotionQueryParams } from '@/types';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/PageHeader';
import { DataTable } from '@/components/ui/DataTable';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ErrorState } from '@/components/ui/ErrorState';

export default function PromotionsPage() {
  const [params, setParams] = useState<PromotionQueryParams>({
    page: 1,
    pageSize: 10,
    search: '',
    status: 'ALL',
  });

  const { data: promRes, isLoading, isError, refetch } = useQuery({
    queryKey: ['promotions-list', params],
    queryFn: () => promotionsApi.getPromotions(params),
  });

  const columns: ColumnDef<Promotion>[] = [
    {
      accessorKey: 'promotionId',
      header: 'Promo ID',
      cell: ({ row }) => (
        <span className="font-mono font-semibold text-blue-600">{row.original.promotionId}</span>
      ),
    },
    {
      accessorKey: 'promotionName',
      header: 'Campaign Name',
      cell: ({ row }) => (
        <div>
          <div className="font-semibold text-slate-900">{row.original.promotionName}</div>
          <div className="text-[10px] text-slate-400">
            Target: <span className="font-semibold text-slate-700">{row.original.targetType}</span> ({row.original.targetValue})
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'discountPercentage',
      header: 'Discount %',
      cell: ({ row }) => (
        <span className="inline-flex items-center gap-1 font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
          <Percent className="w-3 h-3" />
          {row.original.discountPercentage}% OFF
        </span>
      ),
    },
    {
      accessorKey: 'startDate',
      header: 'Campaign Duration',
      cell: ({ row }) => (
        <div className="text-xs text-slate-600 flex items-center gap-1 font-mono">
          <Calendar className="w-3.5 h-3.5 text-slate-400" />
          {row.original.startDate} to {row.original.endDate}
        </div>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => <StatusBadge status={row.original.status} />,
    },
    {
      accessorKey: 'redemptionCount',
      header: 'Redemptions',
      cell: ({ row }) => (
        <span className="font-semibold text-slate-900">{row.original.redemptionCount}</span>
      ),
    },
    {
      accessorKey: 'revenueGenerated',
      header: 'Revenue Impact',
      cell: ({ row }) => (
        <span className="font-mono font-bold text-slate-900">
          ${row.original.revenueGenerated.toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </span>
      ),
    },
  ];

  return (
    <DashboardLayout>
      <PageHeader
        title="Promotions & Marketing Rules"
        subtitle="Active, upcoming, and historical promotional discount rules applied across SKUs and categories"
      />

      {isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : (
        <div className="space-y-4">
          <DataTable
            columns={columns}
            data={promRes?.data || []}
            isLoading={isLoading}
            totalCount={promRes?.meta?.total || 0}
            page={params.page || 1}
            pageSize={params.pageSize || 10}
            onPageChange={(page) => setParams((prev) => ({ ...prev, page }))}
            onPageSizeChange={(pageSize) => setParams((prev) => ({ ...prev, pageSize, page: 1 }))}
            searchValue={params.search}
            onSearchChange={(search) => setParams((prev) => ({ ...prev, search, page: 1 }))}
            searchPlaceholder="Search promotion campaign, ID, SKU..."
            filtersSlot={
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  <Filter className="w-3.5 h-3.5" />
                  <span>Status:</span>
                </div>
                <select
                  value={params.status}
                  onChange={(e) =>
                    setParams((prev) => ({
                      ...prev,
                      status: e.target.value as PromotionQueryParams['status'],
                      page: 1,
                    }))
                  }
                  className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="ALL">All Statuses</option>
                  <option value="ACTIVE">Active</option>
                  <option value="UPCOMING">Upcoming</option>
                  <option value="EXPIRED">Expired</option>
                </select>
              </div>
            }
          />
        </div>
      )}
    </DashboardLayout>
  );
}
