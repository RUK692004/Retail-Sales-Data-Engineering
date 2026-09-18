'use client';

import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { SalesByStore } from '@/types';

interface SalesByStoreChartProps {
  data: SalesByStore[];
}

export function SalesByStoreChart({ data }: SalesByStoreChartProps) {
  const formatYAxis = (val: number) => `$${(val / 1000).toFixed(0)}k`;

  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Sales by Store Location</h3>
          <p className="text-xs text-slate-500">Revenue performance breakdown across store outlets</p>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis
              dataKey="storeName"
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 11, fill: '#64748b' }}
            />
            <YAxis
              tickFormatter={formatYAxis}
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 11, fill: '#64748b' }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const item = payload[0].payload as SalesByStore;
                  return (
                    <div className="bg-slate-900 text-white p-3 rounded-lg text-xs shadow-lg border border-slate-800">
                      <p className="font-semibold text-slate-200 mb-1">{item.storeName} ({item.storeId})</p>
                      <p className="text-emerald-400 font-medium">
                        Revenue: ${item.revenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </p>
                      <p className="text-blue-300">Total Orders: {item.orders}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="revenue" fill="#3b82f6" radius={[6, 6, 0, 0]} barSize={36} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
