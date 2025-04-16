'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { matches } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { calculateAge } from '@/lib/utils';

interface Match {
  id: string;
  full_name: string;
  bio: string;
  interests: string[];
  location: string;
  birth_date: string;
  profile_photo?: string;
  match_score: number;
}

export default function MatchesPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const [recommendations, setRecommendations] = useState<Match[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [direction, setDirection] = useState<'left' | 'right' | null>(null);
  
  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    
    fetchRecommendations();
  }, [user, router]);
  
  const fetchRecommendations = async () => {
    try {
      const data = await matches.getRecommendations();
      setRecommendations(data);
    } catch (error: any) {
      toast.error('Failed to load matches');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSwipe = async (liked: boolean) => {
    if (currentIndex >= recommendations.length) return;
    
    const match = recommendations[currentIndex];
    setDirection(liked ? 'right' : 'left');
    
    try {
      if (liked) {
        await matches.like(match.id);
        toast.success('Match created!');
      } else {
        await matches.reject(match.id);
      }
    } catch (error: any) {
      toast.error('Failed to process match');
    }
    
    // Wait for animation to complete
    setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
      setDirection(null);
    }, 300);
  };
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-primary-50 to-secondary-50">
        <div className="text-xl font-semibold">Loading matches...</div>
      </div>
    );
  }
  
  if (recommendations.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-primary-50 to-secondary-50">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="text-center py-12">
            <h2 className="text-2xl font-semibold mb-4">No matches found</h2>
            <p className="text-muted-foreground mb-6">
              We're working on finding your perfect match. Check back soon!
            </p>
            <Button onClick={() => router.push('/settings')}>
              Update Preferences
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  const currentMatch = recommendations[currentIndex];
  
  if (!currentMatch) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-primary-50 to-secondary-50">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="text-center py-12">
            <h2 className="text-2xl font-semibold mb-4">No more matches</h2>
            <p className="text-muted-foreground mb-6">
              You've seen all potential matches. Check back later for more!
            </p>
            <Button onClick={fetchRecommendations}>
              Refresh Matches
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-primary-50 to-secondary-50 p-4">
      <div className="w-full max-w-lg">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentMatch.id}
            initial={{ opacity: 0, x: direction === 'left' ? -300 : direction === 'right' ? 300 : 0 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: direction === 'left' ? 300 : -300 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            <Card className="overflow-hidden">
              {currentMatch.profile_photo && (
                <div className="relative h-96">
                  <img
                    src={currentMatch.profile_photo}
                    alt={currentMatch.full_name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-6">
                    <h2 className="text-2xl font-semibold text-white">
                      {currentMatch.full_name}, {calculateAge(currentMatch.birth_date)}
                    </h2>
                    <p className="text-white/90">{currentMatch.location}</p>
                  </div>
                </div>
              )}
              <CardContent className="p-6">
                <div className="mb-4">
                  <h3 className="font-semibold mb-2">About Me</h3>
                  <p className="text-gray-600">{currentMatch.bio}</p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Interests</h3>
                  <div className="flex flex-wrap gap-2">
                    {currentMatch.interests.map((interest) => (
                      <span
                        key={interest}
                        className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                      >
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="mt-4">
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>Match Score</span>
                    <span>{Math.round(currentMatch.match_score * 100)}%</span>
                  </div>
                  <div className="w-full h-2 bg-gray-200 rounded-full mt-1">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{ width: `${currentMatch.match_score * 100}%` }}
                    />
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-center gap-4 p-6 pt-0">
                <Button
                  size="lg"
                  variant="outline"
                  className="w-32"
                  onClick={() => handleSwipe(false)}
                >
                  Pass
                </Button>
                <Button
                  size="lg"
                  className="w-32"
                  onClick={() => handleSwipe(true)}
                >
                  Like
                </Button>
              </CardFooter>
            </Card>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
} 