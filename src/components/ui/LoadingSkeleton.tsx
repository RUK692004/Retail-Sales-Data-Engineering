import React from 'react';

export function CardSkeleton() {
  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm animate-pulse space-y-3">
      <div className="h-4 bg-slate-200 rounded w-1/3"></div>
      <div className="h-8 bg-slate-200 rounded w-2/3"></div>
      <div className="h-3 bg-slate-100 rounded w-1/2"></div>
    </div>
  );
}

export function TableSkeleton({ rows = 5, cols = 6 }: { rows?: number; cols?: number }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 animate-pulse space-y-4">
      <div className="h-8 bg-slate-100 rounded w-full"></div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          {Array.from({ length: cols }).map((_, j) => (
            <div key={j} className="h-6 bg-slate-100 rounded flex-1"></div>
          ))}
        </div>
      ))}
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm animate-pulse space-y-4 h-80 flex flex-col justify-between">
      <div className="h-5 bg-slate-200 rounded w-1/4"></div>
      <div className="h-48 bg-slate-100 rounded w-full"></div>
      <div className="h-4 bg-slate-200 rounded w-1/3"></div>
    </div>
  );
}
