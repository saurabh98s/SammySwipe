'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { matches } from '@/lib/api';
import { toast } from 'react-hot-toast';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface MatchUser {
  id: string;
  full_name: string;
  profile_photo?: string;
  bio?: string;
  common_topics: string[];
  match_score: number;
}

export default function DiscoverPage() {
  const [matchUsers, setMatchUsers] = useState<MatchUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
    setLoading(true);
    try {
      const data = await matches.getRecommendations();
      setMatchUsers(data);
    } catch (error) {
      console.error('Error fetching matches:', error);
      toast.error('Failed to load potential matches');
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (userId: string) => {
    try {
      await matches.like(userId);
      removeCard();
      toast.success('You liked this person! View them in your Matches tab.', {
        duration: 3000,
        icon: '❤️'
      });
    } catch (error) {
      console.error('Error liking user:', error);
      toast.error('Failed to like this person');
    }
  };

  const handleSkip = () => {
    removeCard();
  };

  const removeCard = () => {
    setMatchUsers((prev) => prev.filter((_, index) => index !== currentIndex));
  };

  const currentUser = matchUsers[currentIndex];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-6rem)]">
        <div className="p-8 rounded-xl bg-white/10 backdrop-blur-md border border-white/20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
          <p className="text-white mt-4 text-center">Finding your matches...</p>
        </div>
      </div>
    );
  }

  if (matchUsers.length === 0) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-6rem)]">
        <div className="p-8 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 text-center">
          <div className="text-5xl mb-4">🔍</div>
          <h2 className="text-2xl font-bold text-white mb-2">No More Matches</h2>
          <p className="text-white/70 mb-6">We've run out of potential matches for you.</p>
          <Button 
            onClick={fetchMatches}
            className="bg-white text-rose-500 hover:bg-white/90"
          >
            Refresh Matches
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-3xl font-bold text-white mb-8 text-center">Discover</h1>
      
      <AnimatePresence>
        {currentUser && (
          <motion.div
            key={currentUser.id}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0, x: -300 }}
            transition={{ duration: 0.3 }}
            className="relative"
          >
            <Card className="overflow-hidden bg-white/10 backdrop-blur-md border-white/20">
              <div className="h-80 bg-gradient-to-b from-rose-400/20 to-indigo-500/20 relative">
                {currentUser.profile_photo ? (
                  <img
                    src={currentUser.profile_photo}
                    alt={currentUser.full_name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = "https://via.placeholder.com/400x320?text=No+Photo";
                    }}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <span className="text-6xl">👤</span>
                  </div>
                )}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                  <h2 className="text-2xl font-bold text-white">{currentUser.full_name}</h2>
                  <div className="flex items-center">
                    <div className="bg-rose-500 text-white text-sm rounded-full px-2 py-0.5 font-medium">
                      {Math.round(currentUser.match_score * 100)}% Match
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="p-6 text-white">
                {currentUser.bio && (
                  <p className="mb-4 text-white/80">{currentUser.bio}</p>
                )}
                
                <div className="mb-4">
                  <h3 className="text-sm font-semibold uppercase tracking-wider mb-2 text-white/60">
                    Common Interests
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {currentUser.common_topics && currentUser.common_topics.length > 0 ? (
                      currentUser.common_topics.map((topic, index) => (
                        <span
                          key={index}
                          className="bg-white/10 text-white text-xs rounded-full px-3 py-1"
                        >
                          {topic}
                        </span>
                      ))
                    ) : (
                      <span className="text-white/60 text-sm">
                        Discover new interests together!
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex justify-between gap-4 mt-6">
                  <Button
                    onClick={handleSkip}
                    className="flex-1 bg-white/5 hover:bg-white/10 border border-white/10 text-white"
                  >
                    <span className="text-xl mr-2">⏭️</span> Skip
                  </Button>
                  <Button
                    onClick={() => handleLike(currentUser.id)}
                    className="flex-1 bg-rose-500 hover:bg-rose-600 text-white"
                  >
                    <span className="text-xl mr-2">❤️</span> Like
                  </Button>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
} 