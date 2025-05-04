'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function VideoPage() {
  const [isCallActive, setIsCallActive] = useState(false);
  
  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-8">Video Chat</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Local Video */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white overflow-hidden">
          <div className="aspect-video bg-black relative flex items-center justify-center">
            <video
              id="localVideo"
              autoPlay
              muted
              className={`w-full h-full object-cover ${isCallActive ? 'block' : 'hidden'}`}
            ></video>
            
            {!isCallActive && (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-white/70">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-16 h-16 mb-4">
                  <path d="M23 7l-7 5 7 5V7z" />
                  <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
                </svg>
                <p>Your camera will appear here</p>
              </div>
            )}
            
            <div className="absolute bottom-4 left-4 bg-black/50 px-3 py-1 rounded-full text-sm">
              You
            </div>
          </div>
        </Card>
        
        {/* Remote Video */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white overflow-hidden">
          <div className="aspect-video bg-black relative flex items-center justify-center">
            <video
              id="remoteVideo"
              autoPlay
              className={`w-full h-full object-cover ${isCallActive ? 'block' : 'hidden'}`}
            ></video>
            
            {!isCallActive && (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-white/70">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-16 h-16 mb-4">
                  <path d="M23 7l-7 5 7 5V7z" />
                  <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
                </svg>
                <p>Remote video will appear here</p>
              </div>
            )}
            
            {isCallActive && (
              <div className="absolute bottom-4 left-4 bg-black/50 px-3 py-1 rounded-full text-sm">
                Match
              </div>
            )}
          </div>
        </Card>
      </div>
      
      {/* Controls */}
      <div className="mt-8 flex justify-center space-x-4">
        <Button
          onClick={() => setIsCallActive(true)}
          disabled={isCallActive}
          className="bg-green-500 hover:bg-green-600 text-white px-6 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 mr-2">
            <path d="M23 7l-7 5 7 5V7z" />
            <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
          </svg>
          Start Call
        </Button>
        
        <Button
          onClick={() => setIsCallActive(false)}
          disabled={!isCallActive}
          className="bg-red-500 hover:bg-red-600 text-white px-6 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 mr-2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
          End Call
        </Button>
      </div>
      
      <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white p-6 mt-8">
        <h3 className="text-lg font-semibold mb-2 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 mr-2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          Video Chat Information
        </h3>
        <p className="text-white/70">
          This is a demonstration of the video chat feature. In a real implementation, you would be able to:
        </p>
        <ul className="list-disc list-inside mt-2 space-y-1 text-white/70">
          <li>Start video calls with your matches</li>
          <li>Adjust camera and microphone settings</li>
          <li>Toggle video and audio during the call</li>
          <li>Share your screen with your match</li>
          <li>Send messages while on the call</li>
        </ul>
      </Card>
    </div>
  );
} 