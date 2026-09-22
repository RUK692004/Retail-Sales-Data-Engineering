'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  TrendingUp,
  Boxes,
  Package,
  Users,
  Tag,
  ShieldCheck,
  ChevronRight,
  Database,
  Layers,
} from 'lucide-react';

export const NAVIGATION_ITEMS = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Sales Analytics', href: '/sales', icon: TrendingUp },
  { name: 'Inventory Monitoring', href: '/inventory', icon: Boxes },
  { name: 'Products & SKUs', href: '/products', icon: Package },
  { name: 'Customers', href: '/customers', icon: Users },
  { name: 'Promotions', href: '/promotions', icon: Tag },
  { name: 'Data Quality & Pipeline', href: '/data-quality', icon: ShieldCheck },
];

export function Sidebar({ className = '' }: { className?: string }) {
  const pathname = usePathname();
  // Same condition MSWProvider actually uses to decide whether to start the
  // mock worker — this badge used to be hardcoded text that never checked
  // anything, so it always said "MSW Mock API — Active" regardless of mode.
  const mswEnabled = process.env.NEXT_PUBLIC_ENABLE_MSW !== 'false';
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api';

  return (
    <aside
      className={`w-64 bg-slate-900 text-slate-300 flex flex-col h-screen border-r border-slate-800 shrink-0 select-none ${className}`}
    >
      {/* Brand & App Title */}
      <div className="h-16 px-6 flex items-center justify-between border-b border-slate-800 bg-slate-950/40">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600/20 text-blue-400 rounded-lg border border-blue-500/30">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-wide">Retail Engineering</h2>
            <p className="text-[10px] text-slate-400 font-mono uppercase tracking-wider">Data Pipeline v1.0</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Core Analytics
        </div>
        {NAVIGATION_ITEMS.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-900/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/70'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.name}</span>
              </div>
              {isActive && <ChevronRight className="w-4 h-4 text-blue-200" />}
            </Link>
          );
        })}
      </div>

      {/* Environment & Backend Connection Info Footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/50 text-xs">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="flex items-center gap-1.5 font-mono text-[11px]">
            <Database className={`w-3.5 h-3.5 ${mswEnabled ? 'text-emerald-400' : 'text-blue-400'}`} />
            Mode: {mswEnabled ? 'MSW Mock API' : 'FastAPI Backend'}
          </span>
          <span
            className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold border ${
              mswEnabled
                ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                : 'bg-blue-950 text-blue-300 border-blue-800'
            }`}
          >
            Active
          </span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          {mswEnabled ? (
            <>
              Ready for FastAPI backend integration via{' '}
              <code className="text-slate-300 bg-slate-800 px-1 py-0.5 rounded">NEXT_PUBLIC_API_URL</code>.
            </>
          ) : (
            <>
              Connected to <code className="text-slate-300 bg-slate-800 px-1 py-0.5 rounded">{apiUrl}</code>.
            </>
          )}
        </p>
      </div>
    </aside>
  );
}
