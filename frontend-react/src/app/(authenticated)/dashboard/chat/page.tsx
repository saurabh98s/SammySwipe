'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { matches, chat } from '@/lib/api';

interface Conversation {
  user_id: string;
  full_name: string;
  profile_photo?: string;
  last_message?: string;
  timestamp?: string;
}

interface Message {
  id: string;
  sender_id: string;
  content: string;
  timestamp: string;
  is_read: boolean;
}

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageInput, setMessageInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.user_id);
    }
  }, [selectedConversation]);

  const fetchConversations = async () => {
    setLoading(true);
    try {
      const data = await matches.getMyMatches();
      setConversations(data);
      // Auto-select first conversation if any exists
      if (data.length > 0 && !selectedConversation) {
        setSelectedConversation(data[0]);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (userId: string) => {
    try {
      const data = await chat.getHistory(userId);
      setMessages(data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSelectConversation = (conversation: Conversation) => {
    setSelectedConversation(conversation);
  };

  const handleSendMessage = async () => {
    if (!selectedConversation || !messageInput.trim()) return;

    try {
      const newMessage = await chat.sendMessage(selectedConversation.user_id, messageInput);
      setMessages((prev) => [...prev, newMessage]);
      setMessageInput('');
      setSelectedFile(null);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  return (
    <div className="flex h-[calc(100vh-6rem)]">
      {/* Sidebar */}
      <div className="w-1/3 bg-white/5 backdrop-blur-md border-r border-white/10 overflow-y-auto">
        <div className="p-4 border-b border-white/10">
          <h2 className="text-lg font-semibold text-white">Conversations</h2>
        </div>
        
        {loading ? (
          <div className="flex justify-center items-center h-40">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
          </div>
        ) : conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-center h-40 px-4">
            <div className="text-3xl mb-2">💬</div>
            <p className="text-white/70">No conversations yet</p>
            <p className="text-white/50 text-sm">Match with someone to start chatting</p>
          </div>
        ) : (
          <ul>
            {conversations.map((conv) => (
              <li key={conv.user_id}>
                <button
                  onClick={() => handleSelectConversation(conv)}
                  className={`w-full text-left p-4 hover:bg-white/10 transition-colors ${
                    selectedConversation?.user_id === conv.user_id ? 'bg-white/10' : ''
                  }`}
                >
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-full bg-white/20 overflow-hidden flex-shrink-0">
                      {conv.profile_photo ? (
                        <img
                          src={conv.profile_photo}
                          alt={conv.full_name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="flex items-center justify-center h-full text-white">
                          {conv.full_name.charAt(0)}
                        </div>
                      )}
                    </div>
                    <div className="ml-3 flex-1 overflow-hidden">
                      <div className="font-medium text-white">{conv.full_name}</div>
                      {conv.last_message && (
                        <p className="text-white/60 text-sm truncate">{conv.last_message}</p>
                      )}
                    </div>
                    {conv.timestamp && (
                      <div className="text-xs text-white/50">
                        {new Date(conv.timestamp).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                    )}
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {/* Main Chat Window */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-white/10 bg-white/5 backdrop-blur-md flex items-center">
              <div className="w-10 h-10 rounded-full bg-white/20 overflow-hidden">
                {selectedConversation.profile_photo ? (
                  <img
                    src={selectedConversation.profile_photo}
                    alt={selectedConversation.full_name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-white">
                    {selectedConversation.full_name.charAt(0)}
                  </div>
                )}
              </div>
              <div className="ml-3">
                <h2 className="font-medium text-white">{selectedConversation.full_name}</h2>
              </div>
            </div>
            
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="text-3xl mb-2">👋</div>
                  <p className="text-white/70">No messages yet</p>
                  <p className="text-white/50 text-sm">Say hello to start the conversation</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.sender_id !== selectedConversation.user_id
                        ? 'justify-end'
                        : 'justify-start'
                    }`}
                  >
                    <Card
                      className={`max-w-[70%] p-3 ${
                        message.sender_id !== selectedConversation.user_id
                          ? 'bg-rose-500 text-white'
                          : 'bg-white/10 text-white'
                      }`}
                    >
                      <p>{message.content}</p>
                      <div
                        className={`text-xs mt-1 ${
                          message.sender_id !== selectedConversation.user_id
                            ? 'text-white/70'
                            : 'text-white/50'
                        }`}
                      >
                        {new Date(message.timestamp).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                    </Card>
                  </div>
                ))
              )}
            </div>
            
            {/* Message Input */}
            <div className="p-4 border-t border-white/10 bg-white/5">
              {selectedFile && (
                <div className="mb-2 p-2 bg-white/10 rounded flex items-center justify-between">
                  <span className="text-white text-sm truncate">{selectedFile.name}</span>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="text-white/70 hover:text-white"
                  >
                    ✕
                  </button>
                </div>
              )}
              <div className="flex space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  className="bg-white/5 border-white/10 text-white hover:bg-white/10"
                  onClick={() => document.getElementById('file-upload')?.click()}
                >
                  📎
                  <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                </Button>
                <Input
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 bg-white/5 border-white/10 text-white"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!messageInput.trim()}
                  className="bg-rose-500 hover:bg-rose-600 text-white"
                >
                  Send
                </Button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-5xl mb-4">💬</div>
            <h2 className="text-2xl font-semibold text-white mb-2">No Conversation Selected</h2>
            <p className="text-white/70">
              Select a conversation from the sidebar to start chatting
            </p>
          </div>
        )}
      </div>
    </div>
  );
} 