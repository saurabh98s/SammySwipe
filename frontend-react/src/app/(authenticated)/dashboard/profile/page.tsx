'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/store';
import { users } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'react-hot-toast';

export default function ProfilePage() {
  const { user, fetchUser } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    bio: '',
    profile_photo: '',
    twitter: '',
    instagram: '',
    facebook: '',
  });

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        bio: user.bio || '',
        profile_photo: user.profile_photo || '',
        twitter: user.twitter_handle || '',
        instagram: user.instagram_handle || '',
        facebook: user.facebook_handle || '',
      });
    }
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await users.updateProfile({
        full_name: formData.full_name,
        bio: formData.bio,
        profile_photo: formData.profile_photo,
        social_handles: {
          twitter: formData.twitter,
          instagram: formData.instagram,
          facebook: formData.facebook,
        }
      });
      
      await fetchUser();
      toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-8">Profile Management</h1>
      
      <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white p-6">
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Name</label>
              <Input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                className="bg-white/5 border-white/10 text-white"
                placeholder="Your full name"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Bio</label>
              <textarea
                name="bio"
                value={formData.bio}
                onChange={handleChange}
                className="w-full bg-white/5 border border-white/10 rounded-md px-3 py-2 text-white min-h-[100px]"
                placeholder="Tell us about yourself..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Profile Photo URL</label>
              <Input
                type="url"
                name="profile_photo"
                value={formData.profile_photo}
                onChange={handleChange}
                className="bg-white/5 border-white/10 text-white"
                placeholder="https://example.com/your-photo.jpg"
              />
              
              {formData.profile_photo && (
                <div className="mt-2 w-24 h-24 rounded-full overflow-hidden border border-white/20">
                  <img 
                    src={formData.profile_photo} 
                    alt="Profile Preview" 
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = "https://via.placeholder.com/150?text=Error";
                    }}
                  />
                </div>
              )}
            </div>
            
            <div className="border-t border-white/10 pt-4">
              <h3 className="text-lg font-semibold mb-4">Social Handles</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Twitter</label>
                  <div className="flex">
                    <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-white/10 bg-white/5 text-white">
                      @
                    </span>
                    <Input
                      type="text"
                      name="twitter"
                      value={formData.twitter}
                      onChange={handleChange}
                      className="bg-white/5 border-white/10 text-white rounded-l-none"
                      placeholder="username"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Instagram</label>
                  <div className="flex">
                    <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-white/10 bg-white/5 text-white">
                      @
                    </span>
                    <Input
                      type="text"
                      name="instagram"
                      value={formData.instagram}
                      onChange={handleChange}
                      className="bg-white/5 border-white/10 text-white rounded-l-none"
                      placeholder="username"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Facebook</label>
                  <div className="flex">
                    <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-white/10 bg-white/5 text-white">
                      facebook.com/
                    </span>
                    <Input
                      type="text"
                      name="facebook"
                      value={formData.facebook}
                      onChange={handleChange}
                      className="bg-white/5 border-white/10 text-white rounded-l-none"
                      placeholder="username"
                    />
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex justify-end">
              <Button
                type="submit"
                className="bg-white text-rose-500 hover:bg-white/90"
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-rose-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Saving...
                  </span>
                ) : 'Save Profile'}
              </Button>
            </div>
          </div>
        </form>
      </Card>
    </div>
  );
} 