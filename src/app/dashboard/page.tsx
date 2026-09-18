'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  DollarSign,
  ShoppingBag,
  Users,
  Package,
  Boxes,
  AlertTriangle,
  Activity,
  CheckCircle2,
  RefreshCw,
  Clock,
} from 'lucide-react';
import { dashboardApi } from '@/lib/api';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/PageHeader';
import { KpiCard } from '@/components/dashboard/KpiCard';
import { SalesTrendChart } from '@/components/charts/SalesTrendChart';
import { SalesByStoreChart } from '@/components/charts/SalesByStoreChart';
import { SalesByCategoryChart } from '@/components/charts/SalesByCategoryChart';
import { TopProductsChart } from '@/components/charts/TopProductsChart';
import { CardSkeleton, ChartSkeleton } from '@/components/ui/LoadingSkeleton';
import { ErrorState } from '@/components/ui/ErrorState';
import { StatusBadge } from '@/components/ui/StatusBadge';

export default function DashboardPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => dashboardApi.getSummary(),
  });

  return (
    <DashboardLayout>
      <PageHeader
        title="Pipeline Overview Dashboard"
        subtitle="Real-time retail metrics, sales velocity, inventory state, and ingestion health"
        action={
          <button
            onClick={() => refetch()}
            className="inline-flex items-center gap-2 px-3 py-2 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-medium rounded-lg shadow-xs transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Pipeline Metrics
          </button>
        }
      />

      {isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : isLoading || !data ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChartSkeleton />
            <ChartSkeleton />
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Pipeline Status Header Widget */}
          <div className="bg-slate-900 text-white p-4 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-md">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-emerald-500/20 text-emerald-400 rounded-lg border border-emerald-500/30">
                <Activity className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-bold text-white">Ingestion Pipeline Status</h3>
                  <StatusBadge status={data.pipelineStatus.status} />
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Today processed:{' '}
                  <span className="font-semibold text-slate-200">
                    {data.pipelineStatus.recordsProcessedToday.toLocaleString()} records
                  </span>{' '}
                  • Error rate:{' '}
                  <span className="font-semibold text-emerald-400">
                    {data.pipelineStatus.errorRatePercentage}%
                  </span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 text-xs text-slate-400 border-t md:border-t-0 md:border-l border-slate-800 pt-3 md:pt-0 md:pl-4">
              <Clock className="w-4 h-4 text-slate-500" />
              <span>
                Last ETL Batch:{' '}
                <span className="font-mono text-slate-200">
                  {new Date(data.pipelineStatus.lastRunAt).toLocaleTimeString()}
                </span>
              </span>
            </div>
          </div>

          {/* KPI Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            <KpiCard
              title="Total Revenue"
              value={`$${data.totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
              changePercentage={data.revenueGrowthPercentage}
              subtitle="vs previous cycle"
              icon={DollarSign}
            />
            <KpiCard
              title="Total Orders"
              value={data.totalOrders.toLocaleString()}
              changePercentage={data.ordersGrowthPercentage}
              subtitle="vs previous cycle"
              icon={ShoppingBag}
            />
            <KpiCard
              title="Total Customers"
              value={data.totalCustomers.toLocaleString()}
              subtitle="Registered profiles"
              icon={Users}
            />
            <KpiCard
              title="Active SKUs"
              value={data.totalSkus.toLocaleString()}
              subtitle="Catalog items"
              icon={Package}
            />
            <KpiCard
              title="Inventory Units"
              value={data.totalInventoryUnits.toLocaleString()}
              subtitle="Across 5 stores"
              icon={Boxes}
            />
            <KpiCard
              title="Low Stock Items"
              value={data.lowStockItemsCount}
              subtitle="Requires reorder"
              icon={AlertTriangle}
              variant={data.lowStockItemsCount > 10 ? 'danger' : 'warning'}
            />
          </div>

          {/* Charts Row 1: Sales Trend & Store Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SalesTrendChart data={data.salesTrend} />
            <SalesByStoreChart data={data.salesByStore} />
          </div>

          {/* Charts Row 2: Top Products & Category Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TopProductsChart data={data.topProducts} />
            <SalesByCategoryChart data={data.salesByCategory} />
          </div>

          {/* Tables & Alerts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Sales Table (2 cols) */}
            <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-900">Recent Stream Transactions</h3>
                  <span className="text-xs text-slate-500 font-mono">Live Sync</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                        <th className="py-2.5 px-3">Sale ID</th>
                        <th className="py-2.5 px-3">Customer</th>
                        <th className="py-2.5 px-3">Product</th>
                        <th className="py-2.5 px-3">Store</th>
                        <th className="py-2.5 px-3 text-right">Amount</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {data.recentSales.map((sale) => (
                        <tr key={sale.saleId} className="hover:bg-slate-50/80">
                          <td className="py-2.5 px-3 font-mono font-medium text-blue-600">{sale.saleId}</td>
                          <td className="py-2.5 px-3 font-medium text-slate-900">{sale.customerName}</td>
                          <td className="py-2.5 px-3 truncate max-w-[160px]">{sale.productName}</td>
                          <td className="py-2.5 px-3 text-slate-500">{sale.storeName}</td>
                          <td className="py-2.5 px-3 text-right font-bold text-slate-900">
                            ${sale.totalAmount.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Low Stock Alerts Widget (1 col) */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-slate-900">Low Stock Reorder Alerts</h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                  {data.lowStockAlerts.length} Critical
                </span>
              </div>

              <div className="space-y-3">
                {data.lowStockAlerts.map((alert) => (
                  <div
                    key={`${alert.skuId}-${alert.storeName}`}
                    className="p-3 bg-amber-50/50 rounded-lg border border-amber-200 flex items-center justify-between text-xs"
                  >
                    <div>
                      <p className="font-semibold text-slate-900">{alert.productName}</p>
                      <p className="text-slate-500 font-mono text-[10px]">
                        {alert.skuId} • {alert.storeName}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-rose-600">{alert.stockOnHand} left</span>
                      <p className="text-[10px] text-slate-400">Reorder at {alert.reorderPoint}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
