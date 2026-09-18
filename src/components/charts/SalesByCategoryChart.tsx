'use client';

import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';
import { SalesByCategory } from '@/types';

interface SalesByCategoryChartProps {
  data: SalesByCategory[];
}

const COLORS = ['#2563eb', '#0284c7', '#0d9488', '#16a34a', '#d97706', '#dc2626'];

export function SalesByCategoryChart({ data }: SalesByCategoryChartProps) {
  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-slate-900">Sales by Product Category</h3>
        <p className="text-xs text-slate-500">Distribution of revenue across retail categories</p>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={4}
              dataKey="revenue"
              nameKey="category"
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const item = payload[0].payload as SalesByCategory;
                  return (
                    <div className="bg-slate-900 text-white p-3 rounded-lg text-xs shadow-lg border border-slate-800">
                      <p className="font-semibold text-slate-200 mb-1">{item.category}</p>
                      <p className="text-emerald-400 font-medium">
                        ${item.revenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </p>
                      <p className="text-slate-400">{item.percentage}% of total sales</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend
              layout="vertical"
              verticalAlign="middle"
              align="right"
              wrapperStyle={{ fontSize: '12px' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
