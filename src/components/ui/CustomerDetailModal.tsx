'use client';

import React from 'react';
import { X, User, Mail, MapPin, ShoppingBag, DollarSign, Calendar, Award } from 'lucide-react';
import { Customer } from '@/types';
import { StatusBadge } from './StatusBadge';

interface CustomerDetailModalProps {
  customer: Customer | null;
  onClose: () => void;
}

export function CustomerDetailModal({ customer, onClose }: CustomerDetailModalProps) {
  if (!customer) return null;

  const avgOrderVal = customer.totalOrders > 0 ? (customer.totalPurchases / customer.totalOrders).toFixed(2) : '0';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white w-full max-w-lg rounded-2xl shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600/30 text-blue-400 rounded-lg">
              <User className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold">{customer.fullName}</h3>
              <p className="text-xs text-slate-400 font-mono">{customer.customerId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 text-slate-700">
          {/* Tier & LTV Highlights */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                Loyalty Tier
              </span>
              <StatusBadge status={customer.loyaltyTier} />
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                Lifetime Value
              </span>
              <span className="text-base font-bold text-slate-900">
                ${customer.totalPurchases.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>

          {/* Properties Grid */}
          <div className="grid grid-cols-2 gap-y-4 gap-x-6 text-sm">
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                <Mail className="w-3.5 h-3.5 text-slate-400" /> Email Address
              </span>
              <span className="font-semibold text-slate-900 truncate block">{customer.email}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" /> Primary Location
              </span>
              <span className="font-semibold text-slate-900">
                {customer.city}, {customer.state} ({customer.country})
              </span>
            </div>
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                <ShoppingBag className="w-3.5 h-3.5 text-slate-400" /> Completed Orders
              </span>
              <span className="font-bold text-slate-900">{customer.totalOrders} Orders</span>
            </div>
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                <DollarSign className="w-3.5 h-3.5 text-slate-400" /> Avg Order Value
              </span>
              <span className="font-bold text-emerald-600">${avgOrderVal}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                <Calendar className="w-3.5 h-3.5 text-slate-400" /> First Purchase
              </span>
              <span className="font-medium text-slate-700">{customer.firstPurchasedAt}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                <Calendar className="w-3.5 h-3.5 text-slate-400" /> Last Active
              </span>
              <span className="font-medium text-slate-700">{customer.lastPurchasedAt}</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 text-white text-xs font-medium rounded-lg hover:bg-slate-800 transition-colors"
          >
            Close Profile
          </button>
        </div>
      </div>
    </div>
  );
}
