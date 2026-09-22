'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ColumnDef } from '@tanstack/react-table';
import { Users, Eye, Filter } from 'lucide-react';
import { customersApi } from '@/lib/api';
import { Customer, CustomerQueryParams } from '@/types';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/PageHeader';
import { DataTable } from '@/components/ui/DataTable';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { CustomerDetailModal } from '@/components/ui/CustomerDetailModal';
import { ErrorState } from '@/components/ui/ErrorState';

export default function CustomersPage() {
  const [params, setParams] = useState<CustomerQueryParams>({
    page: 1,
    pageSize: 10,
    search: '',
    loyaltyTier: 'ALL',
  });

  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);

  const { data: custRes, isLoading, isError, refetch } = useQuery({
    queryKey: ['customers-list', params],
    queryFn: () => customersApi.getCustomers(params),
  });

  const columns: ColumnDef<Customer>[] = [
    {
      accessorKey: 'customerId',
      header: 'Customer ID',
      cell: ({ row }) => (
        <span className="font-mono font-semibold text-blue-600">{row.original.customerId}</span>
      ),
    },
    {
      accessorKey: 'fullName',
      header: 'Full Name',
      cell: ({ row }) => (
        <div>
          <div className="font-semibold text-slate-900">{row.original.fullName}</div>
          <div className="text-[11px] text-slate-400 font-mono">{row.original.email}</div>
        </div>
      ),
    },
    {
      accessorKey: 'location',
      header: 'Location',
      cell: ({ row }) => (
        <span className="text-slate-700 text-xs font-medium">
          {row.original.city}, {row.original.state}
        </span>
      ),
    },
    {
      accessorKey: 'loyaltyTier',
      header: 'Loyalty Tier',
      cell: ({ row }) => <StatusBadge status={row.original.loyaltyTier} />,
    },
    {
      accessorKey: 'totalOrders',
      header: 'Total Orders',
      cell: ({ row }) => (
        <span className="font-semibold text-slate-900">{row.original.totalOrders}</span>
      ),
    },
    {
      accessorKey: 'totalPurchases',
      header: 'Lifetime Purchases',
      cell: ({ row }) => (
        <span className="font-mono font-bold text-slate-900">
          ${row.original.totalPurchases.toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </span>
      ),
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <button
          onClick={() => setSelectedCustomer(row.original)}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded text-xs font-medium transition-colors"
        >
          <Eye className="w-3.5 h-3.5 text-slate-500" />
          View Profile
        </button>
      ),
    },
  ];

  return (
    <DashboardLayout>
      <PageHeader
        title="Customer Profiles & LTV Analytics"
        subtitle="Aggregated customer metrics, purchasing frequency, and loyalty tier distribution"
      />

      {isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : (
        <div className="space-y-4">
          <DataTable
            columns={columns}
            data={custRes?.data || []}
            isLoading={isLoading}
            totalCount={custRes?.meta?.total || 0}
            page={params.page || 1}
            pageSize={params.pageSize || 10}
            onPageChange={(page) => setParams((prev) => ({ ...prev, page }))}
            onPageSizeChange={(pageSize) => setParams((prev) => ({ ...prev, pageSize, page: 1 }))}
            searchValue={params.search}
            onSearchChange={(search) => setParams((prev) => ({ ...prev, search, page: 1 }))}
            searchPlaceholder="Search customer name, ID, email, city..."
            filtersSlot={
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  <Filter className="w-3.5 h-3.5" />
                  <span>Loyalty Tier:</span>
                </div>
                <select
                  value={params.loyaltyTier}
                  onChange={(e) => setParams((prev) => ({ ...prev, loyaltyTier: e.target.value, page: 1 }))}
                  className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="ALL">All Tiers</option>
                  <option value="PLATINUM">Platinum</option>
                  <option value="GOLD">Gold</option>
                  <option value="SILVER">Silver</option>
                  <option value="BRONZE">Bronze</option>
                </select>
              </div>
            }
          />

          {/* Customer Detail Modal */}
          <CustomerDetailModal
            customer={selectedCustomer}
            onClose={() => setSelectedCustomer(null)}
          />
        </div>
      )}
    </DashboardLayout>
  );
}
