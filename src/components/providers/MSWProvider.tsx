'use client';

import { useEffect, useState, ReactNode } from 'react';

export function MSWProvider({ children }: { children: ReactNode }) {
  const [mswReady, setMswReady] = useState(false);

  useEffect(() => {
    const initMSW = async () => {
      if (typeof window !== 'undefined' && process.env.NEXT_PUBLIC_ENABLE_MSW !== 'false') {
        const { worker } = await import('@/mocks/browser');
        await worker.start({
          onUnhandledRequest: 'bypass',
        });
      }
      setMswReady(true);
    };

    initMSW().catch((err) => {
      console.error('Failed to initialize MSW:', err);
      setMswReady(true);
    });
  }, []);

  if (!mswReady) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-slate-900 text-slate-100">
        <div className="flex flex-col items-center space-y-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
          <p className="text-sm font-medium text-slate-400">Initializing Mock API Service Worker...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
