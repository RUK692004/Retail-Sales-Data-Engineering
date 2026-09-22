import type { Metadata } from 'next';
import './globals.css';
import { QueryProvider } from '@/components/providers/QueryProvider';
import { MSWProvider } from '@/components/providers/MSWProvider';

export const metadata: Metadata = {
  title: 'Retail Sales Data Engineering Pipeline',
  description: 'Enterprise Retail Analytics & Pipeline Intelligence Dashboard',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>
          <MSWProvider>{children}</MSWProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
