'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { matches } from '@/lib/api';
import { toast } from 'react-hot-toast';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { calculateAge } from '@/lib/utils';

interface PendingMatch {
  id: string;
  full_name: string;
  profile_photo?: string;
  bio?: string;
  interests?: string[];
  birth_date: string;
  match_score: number;
  liked_at: string;
}

export default function MatchesPage() {
  const [pendingMatches, setPendingMatches] = useState<PendingMatch[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPendingMatches();
  }, []);

  const fetchPendingMatches = async () => {
    setLoading(true);
    try {
      const data = await matches.getPendingLikes();
      setPendingMatches(data);
      if (data.length === 0) {
        toast.info('You haven\'t liked anyone yet or all your likes have been responded to.');
      }
    } catch (error) {
      console.error('Error fetching pending matches:', error);
      toast.error('Failed to load your likes');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-6rem)]">
        <div className="p-8 rounded-xl bg-white/10 backdrop-blur-md border border-white/20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
          <p className="text-white mt-4 text-center">Loading your likes...</p>
        </div>
      </div>
    );
  }

  if (pendingMatches.length === 0) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-6rem)]">
        <div className="p-8 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 text-center">
          <div className="text-5xl mb-4">💔</div>
          <h2 className="text-2xl font-bold text-white mb-2">No Pending Matches</h2>
          <p className="text-white/70 mb-6">
            You haven't liked anyone yet or all your likes have been responded to.
            <br />
            Visit the Discover page to find people you might be interested in!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-4">People You've Liked</h1>
      <p className="text-white/70 mb-6">
        These are people you've liked from the Discover page. They haven't responded yet.
      </p>
      
      <div className="mb-6">
        <button
          onClick={fetchPendingMatches}
          className="bg-white/10 hover:bg-white/20 text-white rounded-md px-4 py-2 flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 2v6h-6"></path><path d="M3 12a9 9 0 0 1 15-6.7l3-3"></path>
            <path d="M3 22v-6h6"></path><path d="M21 12a9 9 0 0 1-15 6.7l-3 3"></path>
          </svg>
          Refresh
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pendingMatches.map((match) => (
          <motion.div
            key={match.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="overflow-hidden bg-white/10 backdrop-blur-md border-white/20 h-full flex flex-col">
              <div className="h-60 bg-gradient-to-b from-rose-400/20 to-indigo-500/20 relative">
                {match.profile_photo ? (
                  <img
                    src={match.profile_photo}
                    alt={match.full_name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = "https://via.placeholder.com/300x200?text=No+Photo";
                    }}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <span className="text-6xl">👤</span>
                  </div>
                )}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                  <h2 className="text-xl font-bold text-white">
                    {match.full_name}, {calculateAge(match.birth_date)}
                  </h2>
                  <div className="flex items-center mt-1">
                    <Badge variant="secondary" className="bg-rose-500 text-white border-none">
                      {Math.round(match.match_score * 100)}% Match
                    </Badge>
                    <Badge variant="outline" className="ml-2 bg-amber-500/20 text-amber-300 border-amber-500/50">
                      Pending
                    </Badge>
                  </div>
                </div>
              </div>
              
              <CardContent className="p-4 text-white flex-grow">
                {match.bio && (
                  <p className="mb-4 text-white/80 line-clamp-3">{match.bio}</p>
                )}
                
                {match.interests && match.interests.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold uppercase tracking-wider mb-2 text-white/60">
                      Interests
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {match.interests.slice(0, 4).map((interest, index) => (
                        <span
                          key={index}
                          className="bg-white/10 text-white text-xs rounded-full px-3 py-1"
                        >
                          {interest}
                        </span>
                      ))}
                      {match.interests.length > 4 && (
                        <span className="bg-white/10 text-white text-xs rounded-full px-3 py-1">
                          +{match.interests.length - 4} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
                
                <div className="mt-4 text-sm text-white/50">
                  Liked on {new Date(match.liked_at).toLocaleDateString()}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
} 