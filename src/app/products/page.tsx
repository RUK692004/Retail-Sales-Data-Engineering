'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ColumnDef } from '@tanstack/react-table';
import { Package, Eye, Filter } from 'lucide-react';
import { productsApi } from '@/lib/api';
import { Product, ProductQueryParams } from '@/types';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PageHeader } from '@/components/ui/PageHeader';
import { DataTable } from '@/components/ui/DataTable';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ProductDetailModal } from '@/components/ui/ProductDetailModal';
import { ErrorState } from '@/components/ui/ErrorState';

export default function ProductsPage() {
  const [params, setParams] = useState<ProductQueryParams>({
    page: 1,
    pageSize: 10,
    search: '',
    category: 'ALL',
    status: 'ALL',
  });

  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const { data: prodRes, isLoading, isError, refetch } = useQuery({
    queryKey: ['products-list', params],
    queryFn: () => productsApi.getProducts(params),
  });

  const columns: ColumnDef<Product>[] = [
    {
      accessorKey: 'skuId',
      header: 'SKU ID',
      cell: ({ row }) => (
        <span className="font-mono font-semibold text-blue-600">{row.original.skuId}</span>
      ),
    },
    {
      accessorKey: 'productName',
      header: 'Product Name',
      cell: ({ row }) => (
        <div>
          <div className="font-semibold text-slate-900">{row.original.productName}</div>
          {row.original.description && (
            <div className="text-[11px] text-slate-400 truncate max-w-xs">
              {row.original.description}
            </div>
          )}
        </div>
      ),
    },
    {
      accessorKey: 'category',
      header: 'Category',
      cell: ({ row }) => (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700">
          {row.original.category}
        </span>
      ),
    },
    {
      accessorKey: 'brand',
      header: 'Brand',
      cell: ({ row }) => <span className="text-slate-700 font-medium">{row.original.brand}</span>,
    },
    {
      accessorKey: 'price',
      header: 'Retail Price',
      cell: ({ row }) => (
        <span className="font-mono font-bold text-slate-900">${row.original.price.toFixed(2)}</span>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Catalog Status',
      cell: ({ row }) => <StatusBadge status={row.original.status} />,
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <button
          onClick={() => setSelectedProduct(row.original)}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded text-xs font-medium transition-colors"
        >
          <Eye className="w-3.5 h-3.5 text-slate-500" />
          View Details
        </button>
      ),
    },
  ];

  return (
    <DashboardLayout>
      <PageHeader
        title="Products & Master SKUs"
        subtitle="Master retail product catalog, brand indexing, price lists, and item classifications"
      />

      {isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : (
        <div className="space-y-4">
          <DataTable
            columns={columns}
            data={prodRes?.data || []}
            isLoading={isLoading}
            totalCount={prodRes?.meta?.total || 0}
            page={params.page || 1}
            pageSize={params.pageSize || 10}
            onPageChange={(page) => setParams((prev) => ({ ...prev, page }))}
            onPageSizeChange={(pageSize) => setParams((prev) => ({ ...prev, pageSize, page: 1 }))}
            searchValue={params.search}
            onSearchChange={(search) => setParams((prev) => ({ ...prev, search, page: 1 }))}
            searchPlaceholder="Search product name, SKU ID, brand..."
            filtersSlot={
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  <Filter className="w-3.5 h-3.5" />
                  <span>Category:</span>
                </div>
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

                <select
                  value={params.status}
                  onChange={(e) =>
                    setParams((prev) => ({
                      ...prev,
                      status: e.target.value as ProductQueryParams['status'],
                      page: 1,
                    }))
                  }
                  className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="ALL">All Statuses</option>
                  <option value="ACTIVE">Active</option>
                  <option value="DISCONTINUED">Discontinued</option>
                  <option value="DRAFT">Draft</option>
                </select>
              </div>
            }
          />

          {/* Product Detail Modal */}
          <ProductDetailModal
            product={selectedProduct}
            onClose={() => setSelectedProduct(null)}
          />
        </div>
      )}
    </DashboardLayout>
  );
}
