'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ColumnDef } from '@tanstack/react-table';
import { Boxes, AlertTriangle, AlertCircle, Store, Filter } from 'lucide-react';
import { inventoryApi } from '@/lib/api';
import { InventoryItem, InventoryQueryParams } from '@/types';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/PageHeader';
import { KpiCard } from '@/components/dashboard/KpiCard';
import { DataTable } from '@/components/ui/DataTable';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { CardSkeleton } from '@/components/ui/LoadingSkeleton';
import { ErrorState } from '@/components/ui/ErrorState';
import { STORES } from '@/mocks/mock-data';

export default function InventoryPage() {
  const [params, setParams] = useState<InventoryQueryParams>({
    page: 1,
    pageSize: 10,
    search: '',
    storeId: 'ALL',
    status: 'ALL',
  });

  const { data: invRes, isLoading, isError, refetch } = useQuery({
    queryKey: ['inventory-list', params],
    queryFn: () => inventoryApi.getInventory(params),
  });

  const allItems = invRes?.data || [];
  const totalUnits = allItems.reduce((acc, curr) => acc + curr.stockOnHand, 0);
  const lowStockCount = allItems.filter((i) => i.status === 'LOW_STOCK').length;
  const outOfStockCount = allItems.filter((i) => i.status === 'OUT_OF_STOCK').length;
  const storesWithIssues = new Set(
    allItems.filter((i) => i.status !== 'IN_STOCK').map((i) => i.storeId)
  ).size;

  const columns: ColumnDef<InventoryItem>[] = [
    {
      accessorKey: 'storeName',
      header: 'Store Location',
      cell: ({ row }) => (
        <div>
          <div className="font-semibold text-slate-900">{row.original.storeName}</div>
          <div className="text-[10px] font-mono text-slate-400">{row.original.storeId}</div>
        </div>
      ),
    },
    {
      accessorKey: 'productName',
      header: 'Product / SKU',
      cell: ({ row }) => (
        <div>
          <div className="font-medium text-slate-900">{row.original.productName}</div>
          <div className="text-[10px] font-mono text-slate-400">
            {row.original.skuId} • {row.original.category}
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'stockOnHand',
      header: 'Stock On Hand',
      cell: ({ row }) => {
        const val = row.original.stockOnHand;
        return (
          <span
            className={`font-mono font-bold text-sm ${
              val === 0
                ? 'text-rose-600'
                : val <= row.original.reorderPoint
                ? 'text-amber-600'
                : 'text-slate-900'
            }`}
          >
            {val.toLocaleString()} units
          </span>
        );
      },
    },
    {
      accessorKey: 'reorderPoint',
      header: 'Reorder Threshold',
      cell: ({ row }) => (
        <span className="font-mono text-slate-500 text-xs">
          {row.original.reorderPoint} units
        </span>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Stock Status',
      cell: ({ row }) => <StatusBadge status={row.original.status} />,
    },
    {
      accessorKey: 'lastRestocked',
      header: 'Last Restocked',
      cell: ({ row }) => (
        <span className="text-slate-500 font-mono text-xs">{row.original.lastRestocked}</span>
      ),
    },
  ];

  return (
    <DashboardLayout>
      <PageHeader
        title="Inventory Monitoring"
        subtitle="Real-time stock level tracking, warehouse reorder thresholds, and out-of-stock risk indicators"
      />

      {isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : (
        <div className="space-y-6">
          {/* Inventory KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)
            ) : (
              <>
                <KpiCard
                  title="Total Inventory Units"
                  value={totalUnits.toLocaleString()}
                  subtitle="In stock across retail network"
                  icon={Boxes}
                />
                <KpiCard
                  title="Low Stock SKUs"
                  value={lowStockCount}
                  subtitle="Approaching reorder point"
                  icon={AlertTriangle}
                  variant={lowStockCount > 0 ? 'warning' : 'default'}
                />
                <KpiCard
                  title="Out of Stock SKUs"
                  value={outOfStockCount}
                  subtitle="Zero availability alert"
                  icon={AlertCircle}
                  variant={outOfStockCount > 0 ? 'danger' : 'default'}
                />
                <KpiCard
                  title="Stores with Issues"
                  value={storesWithIssues}
                  subtitle="Store locations needing replenishment"
                  icon={Store}
                  variant={storesWithIssues > 0 ? 'warning' : 'default'}
                />
              </>
            )}
          </div>

          {/* Inventory Table */}
          <div className="space-y-2">
            <h3 className="text-base font-bold text-slate-900">Inventory Status Table</h3>
            <DataTable
              columns={columns}
              data={allItems}
              isLoading={isLoading}
              totalCount={invRes?.meta?.total || 0}
              page={params.page || 1}
              pageSize={params.pageSize || 10}
              onPageChange={(page) => setParams((prev) => ({ ...prev, page }))}
              onPageSizeChange={(pageSize) => setParams((prev) => ({ ...prev, pageSize, page: 1 }))}
              searchValue={params.search}
              onSearchChange={(search) => setParams((prev) => ({ ...prev, search, page: 1 }))}
              searchPlaceholder="Search product name, SKU, or store..."
              filtersSlot={
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1.5 text-xs text-slate-500">
                    <Filter className="w-3.5 h-3.5" />
                    <span>Store:</span>
                  </div>
                  <select
                    value={params.storeId}
                    onChange={(e) => setParams((prev) => ({ ...prev, storeId: e.target.value, page: 1 }))}
                    className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="ALL">All Stores</option>
                    {STORES.map((st) => (
                      <option key={st.id} value={st.id}>
                        {st.name}
                      </option>
                    ))}
                  </select>

                  <select
                    value={params.status}
                    onChange={(e) =>
                      setParams((prev) => ({
                        ...prev,
                        status: e.target.value as InventoryQueryParams['status'],
                        page: 1,
                      }))
                    }
                    className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="ALL">All Statuses</option>
                    <option value="IN_STOCK">In Stock</option>
                    <option value="LOW_STOCK">Low Stock</option>
                    <option value="OUT_OF_STOCK">Out of Stock</option>
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
