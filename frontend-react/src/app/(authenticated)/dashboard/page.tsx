'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the discover page when accessing the dashboard
    router.push('/dashboard/discover');
  }, [router]);

  return (
    <div className="flex items-center justify-center h-[calc(100vh-6rem)]">
      <div className="p-8 rounded-xl bg-white/10 backdrop-blur-md border border-white/20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
        <p className="text-white mt-4 text-center">Loading...</p>
      </div>
    </div>
  );
} 