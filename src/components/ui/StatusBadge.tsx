import React from 'react';

type BadgeVariant = 
  | 'success' 
  | 'warning' 
  | 'danger' 
  | 'info' 
  | 'neutral';

interface StatusBadgeProps {
  status: string;
  variant?: BadgeVariant;
  className?: string;
}

export function StatusBadge({ status, variant, className = '' }: StatusBadgeProps) {
  let computedVariant: BadgeVariant = variant || 'neutral';

  if (!variant) {
    const s = status.toUpperCase();
    if (['HEALTHY', 'ACTIVE', 'IN_STOCK', 'PASSED', 'GOLD', 'PLATINUM'].includes(s)) {
      computedVariant = 'success';
    } else if (['WARNING', 'LOW_STOCK', 'UPCOMING', 'DEGRADED', 'SILVER'].includes(s)) {
      computedVariant = 'warning';
    } else if (['FAILED', 'OUT_OF_STOCK', 'EXPIRED', 'CRITICAL', 'DISCONTINUED'].includes(s)) {
      computedVariant = 'danger';
    } else if (['INFO', 'BRONZE', 'DRAFT'].includes(s)) {
      computedVariant = 'info';
    }
  }

  const styles: Record<BadgeVariant, string> = {
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200',
    info: 'bg-sky-50 text-sky-700 border-sky-200',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
  };

  const dotStyles: Record<BadgeVariant, string> = {
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-rose-500',
    info: 'bg-sky-500',
    neutral: 'bg-slate-400',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[computedVariant]} ${className}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${dotStyles[computedVariant]}`} />
      {status.replace(/_/g, ' ')}
    </span>
  );
}
