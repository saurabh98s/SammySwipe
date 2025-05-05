'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/lib/store';

// Icons
const ProfileIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
    <circle cx="12" cy="8" r="5" />
    <path d="M20 21a8 8 0 0 0-16 0" />
  </svg>
);

const DiscoverIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="16" />
    <line x1="8" y1="12" x2="16" y2="12" />
  </svg>
);

const ChatIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);

const MediaIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    <circle cx="8.5" cy="8.5" r="1.5" />
    <polyline points="21 15 16 10 5 21" />
  </svg>
);

const VideoIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
    <polygon points="23 7 16 12 23 17 23 7" />
    <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
  </svg>
);

const MatchesIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78z"></path>
  </svg>
);

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { user, isSuperUser } = useAuthStore();

  const navigation = [
    { name: 'Profile', href: '/dashboard/profile', icon: ProfileIcon },
    { name: 'Discover', href: '/dashboard/discover', icon: DiscoverIcon },
    { name: 'Matches', href: '/dashboard/matches', icon: MatchesIcon },
    { name: 'Chat', href: '/dashboard/chat', icon: ChatIcon },
    { name: 'Media', href: '/dashboard/media', icon: MediaIcon },
    { name: 'Video Chat', href: '/dashboard/video', icon: VideoIcon },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-400 via-fuchsia-500 to-indigo-500">
      {/* Mesh gradient overlay */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iYSIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVHJhbnNmb3JtPSJyb3RhdGUoNDUpIj48cGF0aCBkPSJNMCAyMGgxMHYxMEgwem0yMCAwaDF2MTBoLTF6IiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNhKSIvPjwvc3ZnPg==')] opacity-20"></div>

      {/* Top Navigation */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <Link href="/" className="text-2xl font-display font-bold text-white">
              SammySwipe
            </Link>
            <div className="flex items-center gap-4">
              {isSuperUser ? (
                <div className="flex items-center gap-2">
                  <span className="bg-amber-500/20 text-amber-200 text-xs px-2 py-1 rounded-full border border-amber-500/50">
                    SUPER ADMIN MODE
                  </span>
                  <span className="text-sm text-white/90">
                    Super Admin
                  </span>
                </div>
              ) : (
                <span className="text-sm text-white/90">
                  {user?.full_name}
                </span>
              )}
              <div className="w-10 h-10 rounded-full bg-white/20 overflow-hidden">
                {user?.profile_photo && !isSuperUser && (
                  <img 
                    src={user.profile_photo} 
                    alt={user?.full_name || 'User'} 
                    className="w-full h-full object-cover"
                  />
                )}
                {isSuperUser && (
                  <div className="w-full h-full flex items-center justify-center bg-amber-500/30 text-amber-200">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6">
                      <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"></path>
                      <path d="M12 16v-4"></path>
                      <path d="M12 8h.01"></path>
                    </svg>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex pt-16">
        {/* Sidebar */}
        <div className="w-64 fixed h-full pt-4 bg-white/10 backdrop-blur-md border-r border-white/20">
          <div className="px-4 py-4">
            {isSuperUser && (
              <div className="px-4 py-3 mb-4 rounded-lg bg-amber-500/20 border border-amber-500/40">
                <p className="text-xs text-amber-200 font-semibold">Super Admin Access</p>
                <p className="text-xs text-amber-200/70">All routes unlocked</p>
              </div>
            )}
            <ul className="space-y-2">
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                        isActive 
                          ? 'bg-white/20 text-white' 
                          : 'text-white/70 hover:bg-white/10 hover:text-white'
                      }`}
                    >
                      <span className="flex-shrink-0">
                        <item.icon />
                      </span>
                      <span>{item.name}</span>
                      {isActive && (
                        <motion.div
                          layoutId="activeSidebar"
                          className="absolute left-0 w-1 h-8 bg-white rounded-r"
                          initial={false}
                          transition={{
                            type: 'spring',
                            stiffness: 500,
                            damping: 30,
                          }}
                        />
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 ml-64">
          <main className="container mx-auto px-8 py-8">{children}</main>
        </div>
      </div>
    </div>
  );
} 