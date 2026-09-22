'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ColumnDef } from '@tanstack/react-table';
import { DollarSign, ShoppingBag, ShoppingCart, Hash, Filter, Download } from 'lucide-react';
import { salesApi, dashboardApi } from '@/lib/api';
import { Sale, SalesQueryParams } from '@/types';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/PageHeader';
import { KpiCard } from '@/components/dashboard/KpiCard';
import { DataTable } from '@/components/ui/DataTable';
import { SalesTrendChart } from '@/components/charts/SalesTrendChart';
import { SalesByStoreChart } from '@/components/charts/SalesByStoreChart';
import { SalesByCategoryChart } from '@/components/charts/SalesByCategoryChart';
import { CardSkeleton, ChartSkeleton } from '@/components/ui/LoadingSkeleton';
import { ErrorState } from '@/components/ui/ErrorState';
import { STORES } from '@/mocks/mock-data';

export default function SalesPage() {
  const [params, setParams] = useState<SalesQueryParams>({
    page: 1,
    pageSize: 10,
    search: '',
    storeId: 'ALL',
    category: 'ALL',
  });

  // Query sales table records
  const { data: salesRes, isLoading: salesLoading, isError: salesError, refetch } = useQuery({
    queryKey: ['sales-list', params],
    queryFn: () => salesApi.getSales(params),
  });

  // Query aggregated metrics
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['sales-metrics'],
    queryFn: () => salesApi.getMetrics(),
  });

  // Query summary charts
  const { data: summary } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => dashboardApi.getSummary(),
  });

  const columns: ColumnDef<Sale>[] = [
    {
      accessorKey: 'saleId',
      header: 'Sale ID',
      cell: ({ row }) => (
        <span className="font-mono font-semibold text-blue-600">{row.original.saleId}</span>
      ),
    },
    {
      accessorKey: 'saleDate',
      header: 'Sale Date',
      cell: ({ row }) => (
        <span className="text-slate-600 font-mono text-xs">
          {new Date(row.original.saleDate).toLocaleString()}
        </span>
      ),
    },
    {
      accessorKey: 'customerName',
      header: 'Customer ID / Name',
      cell: ({ row }) => (
        <div>
          <div className="font-medium text-slate-900">{row.original.customerName}</div>
          <div className="text-[10px] text-slate-400 font-mono">{row.original.customerId}</div>
        </div>
      ),
    },
    {
      accessorKey: 'productName',
      header: 'Product / SKU',
      cell: ({ row }) => (
        <div>
          <div className="font-medium text-slate-900">{row.original.productName}</div>
          <div className="text-[10px] text-slate-400 font-mono">
            {row.original.skuId} • {row.original.category}
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'storeName',
      header: 'Store',
      cell: ({ row }) => (
        <span className="text-slate-600 text-xs font-medium">{row.original.storeName}</span>
      ),
    },
    {
      accessorKey: 'quantity',
      header: 'Quantity',
      cell: ({ row }) => <span className="font-semibold text-slate-900">{row.original.quantity}</span>,
    },
    {
      accessorKey: 'unitPrice',
      header: 'Unit Price',
      cell: ({ row }) => <span>${row.original.unitPrice.toFixed(2)}</span>,
    },
    {
      accessorKey: 'totalAmount',
      header: 'Total Amount',
      cell: ({ row }) => (
        <span className="font-bold text-slate-900">${row.original.totalAmount.toFixed(2)}</span>
      ),
    },
  ];

  return (
    <DashboardLayout>
      <PageHeader
        title="Sales Analytics & Transactions"
        subtitle="Detailed granular order breakdown, store revenue performance, and stream logs"
        action={
          <button
            onClick={() => {
              const csvData = salesRes?.data
                ? JSON.stringify(salesRes.data, null, 2)
                : '';
              const blob = new Blob([csvData], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = 'sales_export.json';
              a.click();
            }}
            className="inline-flex items-center gap-2 px-3 py-2 bg-slate-900 text-white hover:bg-slate-800 text-xs font-medium rounded-lg shadow-xs transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            Export Sales Batch
          </button>
        }
      />

      {salesError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : (
        <div className="space-y-6">
          {/* Sales KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {metricsLoading || !metrics ? (
              Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)
            ) : (
              <>
                <KpiCard
                  title="Total Revenue"
                  value={`$${metrics.totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
                  subtitle="Gross revenue aggregated"
                  icon={DollarSign}
                />
                <KpiCard
                  title="Total Sales Count"
                  value={metrics.totalSalesCount.toLocaleString()}
                  subtitle="Completed transactions"
                  icon={ShoppingBag}
                />
                <KpiCard
                  title="Average Order Value"
                  value={`$${metrics.averageOrderValue.toFixed(2)}`}
                  subtitle="Revenue per transaction"
                  icon={ShoppingCart}
                />
                <KpiCard
                  title="Quantity Sold"
                  value={metrics.totalQuantitySold.toLocaleString()}
                  subtitle="Total units dispatched"
                  icon={Hash}
                />
              </>
            )}
          </div>

          {/* Sales Analytics Charts */}
          {summary && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <SalesTrendChart data={summary.salesTrend} title="Granular Sales Revenue Velocity" />
                <SalesByStoreChart data={summary.salesByStore} />
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <SalesByCategoryChart data={summary.salesByCategory} />
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-900 mb-1">Transaction Stream Note</h3>
                    <p className="text-xs text-slate-500 leading-relaxed">
                      Sales records are automatically transformed by the ingestion pipeline engine.
                      Foreign keys for Customer ID and SKU ID are validated during streaming.
                    </p>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200 text-xs text-blue-900 mt-4">
                    <span className="font-semibold block mb-1">Real-time Fast API contract:</span>
                    Endpoints strictly enforce filter parameters: <code className="bg-blue-100 px-1 py-0.5 rounded text-[11px] font-mono">store_id</code>, <code className="bg-blue-100 px-1 py-0.5 rounded text-[11px] font-mono">category</code>, and <code className="bg-blue-100 px-1 py-0.5 rounded text-[11px] font-mono">page</code>.
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Sales Data Table */}
          <div className="space-y-2">
            <h3 className="text-base font-bold text-slate-900">Sales Transactions Table</h3>
            <DataTable
              columns={columns}
              data={salesRes?.data || []}
              isLoading={salesLoading}
              totalCount={salesRes?.meta?.total || 0}
              page={params.page || 1}
              pageSize={params.pageSize || 10}
              onPageChange={(page) => setParams((prev) => ({ ...prev, page }))}
              onPageSizeChange={(pageSize) => setParams((prev) => ({ ...prev, pageSize, page: 1 }))}
              searchValue={params.search}
              onSearchChange={(search) => setParams((prev) => ({ ...prev, search, page: 1 }))}
              searchPlaceholder="Search by Sale ID, Customer Name, SKU, Product..."
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
                    value={params.category}
                    onChange={(e) => setParams((prev) => ({ ...prev, category: e.target.value, page: 1 }))}
                    className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="ALL">All Categories</option>
                    <option value="Electronics">Electronics</option>
                    <option value="Apparel">Apparel</option>
                    <option value="Home & Kitchen">Home & Kitchen</option>
                    <option value="Grocery">Grocery</option>
                    <option value="Sports & Outdoors">Sports & Outdoors</option>
                    <option value="Health & Beauty">Health & Beauty</option>
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
