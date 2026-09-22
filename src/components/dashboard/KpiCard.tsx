import React from 'react';
import { LucideIcon, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  changePercentage?: number;
  icon: LucideIcon;
  variant?: 'default' | 'warning' | 'danger' | 'success';
}

export function KpiCard({
  title,
  value,
  subtitle,
  changePercentage,
  icon: Icon,
  variant = 'default',
}: KpiCardProps) {
  const iconBgStyles = {
    default: 'bg-blue-50 text-blue-600 border-blue-100',
    success: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    warning: 'bg-amber-50 text-amber-600 border-amber-100',
    danger: 'bg-rose-50 text-rose-600 border-rose-100',
  };

  const isPositive = changePercentage !== undefined && changePercentage >= 0;

  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
        <div className={`p-2.5 rounded-lg border ${iconBgStyles[variant]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-2">
        <div className="text-2xl font-bold text-slate-900 tracking-tight">{value}</div>
        {(subtitle || changePercentage !== undefined) && (
          <div className="mt-2 flex items-center gap-2 text-xs">
            {changePercentage !== undefined && (
              <span
                className={`inline-flex items-center font-medium px-1.5 py-0.5 rounded ${
                  isPositive ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                }`}
              >
                {isPositive ? (
                  <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
                ) : (
                  <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
                )}
                {Math.abs(changePercentage)}%
              </span>
            )}
            {subtitle && <span className="text-slate-500">{subtitle}</span>}
          </div>
        )}
      </div>
    </div>
  );
}
