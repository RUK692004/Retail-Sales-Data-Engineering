'use client';

import React from 'react';
import { X, Package, Tag, DollarSign, Calendar, Layers, ShieldCheck } from 'lucide-react';
import { Product } from '@/types';
import { StatusBadge } from './StatusBadge';

interface ProductDetailModalProps {
  product: Product | null;
  onClose: () => void;
}

export function ProductDetailModal({ product, onClose }: ProductDetailModalProps) {
  if (!product) return null;

  const grossMargin = product.price > 0 ? (((product.price - product.costPrice) / product.price) * 100).toFixed(1) : '0';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white w-full max-w-lg rounded-2xl shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600/30 text-blue-400 rounded-lg">
              <Package className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold">{product.productName}</h3>
              <p className="text-xs text-slate-400 font-mono">{product.skuId}</p>
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
          {/* Status & Margin Highlights */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                Catalog Status
              </span>
              <StatusBadge status={product.status} />
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                Est. Gross Margin
              </span>
              <span className="text-sm font-bold text-emerald-600">{grossMargin}% Margin</span>
            </div>
          </div>

          {/* Key Properties Grid */}
          <div className="grid grid-cols-2 gap-y-4 gap-x-6 text-sm">
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                <Tag className="w-3.5 h-3.5 text-slate-400" /> Category
              </span>
              <span className="font-semibold text-slate-900">{product.category}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                <Layers className="w-3.5 h-3.5 text-slate-400" /> Brand
              </span>
              <span className="font-semibold text-slate-900">{product.brand}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                <DollarSign className="w-3.5 h-3.5 text-slate-400" /> Retail Price
              </span>
              <span className="font-bold text-slate-900">${product.price.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                <ShieldCheck className="w-3.5 h-3.5 text-slate-400" /> Unit Cost
              </span>
              <span className="font-medium text-slate-600">${product.costPrice.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                <Calendar className="w-3.5 h-3.5 text-slate-400" /> Ingested Date
              </span>
              <span className="font-medium text-slate-700">{product.createdAt}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">Unit</span>
              <span className="font-medium text-slate-700 uppercase">{product.unit}</span>
            </div>
          </div>

          {/* Product Description */}
          {product.description && (
            <div className="pt-4 border-t border-slate-200">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Description</h4>
              <p className="text-xs leading-relaxed text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200">
                {product.description}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 text-white text-xs font-medium rounded-lg hover:bg-slate-800 transition-colors"
          >
            Close Details
          </button>
        </div>
      </div>
    </div>
  );
}
