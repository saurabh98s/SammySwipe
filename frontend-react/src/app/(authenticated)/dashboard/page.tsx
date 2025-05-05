'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { matches } from '@/lib/api';
import { toast } from 'react-hot-toast';

interface MatchStatistics {
  total_matches_processed: number;
  successful_matches: number;
  success_rate: number;
  quality_distribution: {
    excellent: number;
    good: number;
    average: number;
    low: number;
  };
  average_score: number;
  trends: {
    weekly_matches: number;
    weekly_success_rate: number;
    most_common_interests: string[];
  };
}

export default function DashboardPage() {
  const [statistics, setStatistics] = useState<MatchStatistics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMatchStatistics();
  }, []);

  const fetchMatchStatistics = async () => {
    setLoading(true);
    try {
      const data = await matches.getMatchStatistics();
      setStatistics(data);
    } catch (error) {
      console.error('Error fetching match statistics:', error);
      toast.error('Failed to load match statistics');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Dashboard</h1>
      
      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
        </div>
      ) : statistics ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-lg">Match Success Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-green-400 mb-2">{statistics.success_rate}%</div>
              <p className="text-white/70 text-sm">
                Based on {statistics.total_matches_processed} total matches processed
              </p>
            </CardContent>
          </Card>
          
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-lg">Match Quality</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-1">
                <span className="text-white/70 text-xs">Excellent</span>
                <span className="text-white/70 text-xs">{statistics.quality_distribution.excellent}</span>
              </div>
              <div className="w-full h-2 bg-white/10 rounded-full mb-3">
                <div
                  className="h-full bg-green-500 rounded-full"
                  style={{ width: `${(statistics.quality_distribution.excellent / statistics.total_matches_processed) * 100}%` }}
                />
              </div>
              
              <div className="flex items-center justify-between mb-1">
                <span className="text-white/70 text-xs">Good</span>
                <span className="text-white/70 text-xs">{statistics.quality_distribution.good}</span>
              </div>
              <div className="w-full h-2 bg-white/10 rounded-full mb-3">
                <div
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${(statistics.quality_distribution.good / statistics.total_matches_processed) * 100}%` }}
                />
              </div>
              
              <div className="flex items-center justify-between mb-1">
                <span className="text-white/70 text-xs">Average</span>
                <span className="text-white/70 text-xs">{statistics.quality_distribution.average}</span>
              </div>
              <div className="w-full h-2 bg-white/10 rounded-full mb-3">
                <div
                  className="h-full bg-yellow-500 rounded-full"
                  style={{ width: `${(statistics.quality_distribution.average / statistics.total_matches_processed) * 100}%` }}
                />
              </div>
              
              <div className="flex items-center justify-between mb-1">
                <span className="text-white/70 text-xs">Low</span>
                <span className="text-white/70 text-xs">{statistics.quality_distribution.low}</span>
              </div>
              <div className="w-full h-2 bg-white/10 rounded-full">
                <div
                  className="h-full bg-red-500 rounded-full"
                  style={{ width: `${(statistics.quality_distribution.low / statistics.total_matches_processed) * 100}%` }}
                />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-lg">Weekly Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <div className="text-lg font-semibold text-white mb-1">
                  {statistics.trends.weekly_matches}
                </div>
                <p className="text-white/70 text-sm">Matches this week</p>
              </div>
              
              <div className="mb-4">
                <div className="text-lg font-semibold text-white mb-1">
                  {statistics.trends.weekly_success_rate}%
                </div>
                <p className="text-white/70 text-sm">Success rate this week</p>
              </div>
              
              <div>
                <div className="text-sm font-semibold text-white mb-2">Top Interests</div>
                <div className="flex flex-wrap gap-2">
                  {statistics.trends.most_common_interests.map((interest, index) => (
                    <span
                      key={index}
                      className="bg-white/10 text-white text-xs rounded-full px-3 py-1"
                    >
                      {interest}
                    </span>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="text-center text-white/70">
          No match statistics available
        </div>
      )}
    </div>
  );
} 