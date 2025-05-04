'use client';

import { Card } from '@/components/ui/card';

export default function MediaPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-8">Media</h1>
      
      <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white p-8 text-center">
        <div className="w-24 h-24 rounded-full bg-white/10 flex items-center justify-center mx-auto mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-12 h-12 text-white/70">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <polyline points="21 15 16 10 5 21" />
          </svg>
        </div>
        <h2 className="text-2xl font-semibold mb-2">Media Sharing</h2>
        <p className="text-white/70 mb-6 max-w-md mx-auto">
          Share photos and memories with your matches. This feature is coming soon.
        </p>
        <div className="grid grid-cols-3 gap-4 max-w-md mx-auto">
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <div 
              key={item}
              className="aspect-square bg-white/5 rounded-lg flex items-center justify-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-8 h-8 text-white/30">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
} 