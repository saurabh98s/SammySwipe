'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';
import { motion } from 'framer-motion';
import { io, Socket } from 'socket.io-client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { matches, chat } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { formatDate } from '@/lib/utils';

interface Message {
  id: string;
  sender_id: string;
  receiver_id: string;
  content: string;
  sent_at: string;
}

interface Match {
  id: string;
  full_name: string;
  profile_photo?: string;
  last_message?: Message;
}

export default function ChatPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const [myMatches, setMyMatches] = useState<Match[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<Socket | null>(null);
  
  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    
    fetchMatches();
    
    // Connect to WebSocket
    socketRef.current = io(`${process.env.NEXT_PUBLIC_WS_URL}/chat`, {
      query: { user_id: user.id },
    });
    
    socketRef.current.on('message', (message: Message) => {
      setMessages((prev) => [...prev, message]);
    });
    
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [user, router]);
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const fetchMatches = async () => {
    try {
      const data = await matches.getMyMatches();
      setMyMatches(data);
    } catch (error: any) {
      toast.error('Failed to load matches');
    } finally {
      setIsLoading(false);
    }
  };
  
  const fetchMessages = async (matchId: string) => {
    try {
      const data = await chat.getHistory(matchId);
      setMessages(data);
    } catch (error: any) {
      toast.error('Failed to load messages');
    }
  };
  
  const handleSelectMatch = async (match: Match) => {
    setSelectedMatch(match);
    await fetchMessages(match.id);
  };
  
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMatch || !newMessage.trim()) return;
    
    try {
      await chat.sendMessage(selectedMatch.id, newMessage);
      setNewMessage('');
    } catch (error: any) {
      toast.error('Failed to send message');
    }
  };
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-primary-50 to-secondary-50">
        <div className="text-xl font-semibold">Loading chats...</div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-secondary-50 p-4">
      <div className="container mx-auto max-w-6xl">
        <Card className="grid grid-cols-1 md:grid-cols-3 h-[calc(100vh-2rem)]">
          {/* Matches List */}
          <div className="border-r">
            <CardHeader>
              <h2 className="text-xl font-semibold">Messages</h2>
            </CardHeader>
            <div className="overflow-y-auto h-[calc(100vh-10rem)]">
              {myMatches.length === 0 ? (
                <div className="p-4 text-center text-gray-500">
                  No matches yet. Start swiping to find matches!
                </div>
              ) : (
                myMatches.map((match) => (
                  <motion.button
                    key={match.id}
                    whileHover={{ backgroundColor: 'rgba(0,0,0,0.05)' }}
                    onClick={() => handleSelectMatch(match)}
                    className={`w-full p-4 flex items-center gap-4 border-b ${
                      selectedMatch?.id === match.id ? 'bg-primary-50' : ''
                    }`}
                  >
                    <div className="relative w-12 h-12">
                      {match.profile_photo ? (
                        <img
                          src={match.profile_photo}
                          alt={match.full_name}
                          className="w-full h-full rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-semibold">
                          {match.full_name[0]}
                        </div>
                      )}
                    </div>
                    <div className="flex-1 text-left">
                      <div className="font-semibold">{match.full_name}</div>
                      {match.last_message && (
                        <div className="text-sm text-gray-500 truncate">
                          {match.last_message.content}
                        </div>
                      )}
                    </div>
                  </motion.button>
                ))
              )}
            </div>
          </div>
          
          {/* Chat Area */}
          <div className="col-span-2 flex flex-col">
            {selectedMatch ? (
              <>
                <CardHeader className="border-b">
                  <div className="flex items-center gap-4">
                    <div className="relative w-10 h-10">
                      {selectedMatch.profile_photo ? (
                        <img
                          src={selectedMatch.profile_photo}
                          alt={selectedMatch.full_name}
                          className="w-full h-full rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-semibold">
                          {selectedMatch.full_name[0]}
                        </div>
                      )}
                    </div>
                    <div>
                      <h3 className="font-semibold">{selectedMatch.full_name}</h3>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto p-4">
                  <div className="space-y-4">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${
                          message.sender_id === user?.id ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        <div
                          className={`max-w-[70%] rounded-lg p-3 ${
                            message.sender_id === user?.id
                              ? 'bg-primary text-white'
                              : 'bg-gray-100'
                          }`}
                        >
                          <p>{message.content}</p>
                          <div
                            className={`text-xs mt-1 ${
                              message.sender_id === user?.id
                                ? 'text-white/70'
                                : 'text-gray-500'
                            }`}
                          >
                            {formatDate(message.sent_at)}
                          </div>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                </CardContent>
                <CardFooter className="border-t p-4">
                  <form onSubmit={handleSendMessage} className="flex gap-2 w-full">
                    <Input
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Type a message..."
                      className="flex-1"
                    />
                    <Button type="submit" disabled={!newMessage.trim()}>
                      Send
                    </Button>
                  </form>
                </CardFooter>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                Select a match to start chatting
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
} 