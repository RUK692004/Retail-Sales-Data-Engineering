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
import { TopProduct } from '@/types';

interface TopProductsChartProps {
  data: TopProduct[];
}

export function TopProductsChart({ data }: TopProductsChartProps) {
  const formattedData = data.map((item) => ({
    ...item,
    shortName: item.productName.length > 22 ? item.productName.substring(0, 22) + '...' : item.productName,
  }));

  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-slate-900">Top Selling Products by Revenue</h3>
        <p className="text-xs text-slate-500">Highest grossing SKUs in current reporting cycle</p>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={formattedData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
            <XAxis
              type="number"
              tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 11, fill: '#64748b' }}
            />
            <YAxis
              type="category"
              dataKey="shortName"
              width={140}
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 11, fill: '#334155' }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const item = payload[0].payload as TopProduct & { shortName: string };
                  return (
                    <div className="bg-slate-900 text-white p-3 rounded-lg text-xs shadow-lg border border-slate-800">
                      <p className="font-semibold text-slate-200 mb-1">{item.productName}</p>
                      <p className="text-slate-400 font-mono">SKU: {item.skuId}</p>
                      <p className="text-emerald-400 font-medium mt-1">
                        Revenue: ${item.totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </p>
                      <p className="text-blue-300">Units Sold: {item.unitsSold}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="totalRevenue" fill="#0d9488" radius={[0, 6, 6, 0]} barSize={20} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
