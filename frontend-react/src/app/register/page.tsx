'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { useAuthStore } from '@/lib/store';

interface RegisterFormData {
  email: string;
  username: string;
  full_name: string;
  password: string;
  confirm_password: string;
  gender: string;
  birth_date: string;
  bio: string;
  interests: string[];
  location: string;
  profile_photo?: FileList;
}

export default function RegisterPage() {
  const router = useRouter();
  const register = useAuthStore((state) => state.register);
  const [isLoading, setIsLoading] = useState(false);
  
  const {
    register: registerField,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>();
  
  const password = watch('password');
  
  const onSubmit = async (data: RegisterFormData) => {
    if (data.password !== data.confirm_password) {
      toast.error('Passwords do not match');
      return;
    }
    
    setIsLoading(true);
    try {
      const formData = new FormData();
      Object.keys(data).forEach((key) => {
        if (key === 'profile_photo' && data.profile_photo?.[0]) {
          formData.append(key, data.profile_photo[0]);
        } else if (key !== 'confirm_password') {
          formData.append(key, data[key as keyof RegisterFormData] as string);
        }
      });
      
      await register(formData);
      toast.success('Registration successful! Please log in.');
      router.push('/login');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen relative flex items-center justify-center bg-gradient-to-br from-rose-400 via-fuchsia-500 to-indigo-500 py-12 px-4">
      {/* Mesh gradient overlay */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iYSIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVHJhbnNmb3JtPSJyb3RhdGUoNDUpIj48cGF0aCBkPSJNMCAyMGgxMHYxMEgwem0yMCAwaDF2MTBoLTF6IiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNhKSIvPjwvc3ZnPg==')] opacity-20"></div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl relative z-10"
      >
        <Card>
          <CardHeader>
            <Link
              href="/"
              className="text-2xl font-display font-bold text-white text-center block mb-2"
            >
              SammySwipe
            </Link>
            <h1 className="text-2xl font-semibold text-center text-white">Create an Account</h1>
            <p className="text-white/70 text-center">
              Join SammySwipe and find your perfect match
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Input
                  label="Email"
                  type="email"
                  error={errors.email?.message}
                  {...registerField('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address',
                    },
                  })}
                />
                <Input
                  label="Username"
                  error={errors.username?.message}
                  {...registerField('username', {
                    required: 'Username is required',
                    minLength: {
                      value: 3,
                      message: 'Username must be at least 3 characters',
                    },
                  })}
                />
                <Input
                  label="Full Name"
                  error={errors.full_name?.message}
                  {...registerField('full_name', {
                    required: 'Full name is required',
                  })}
                />
                <Input
                  label="Password"
                  type="password"
                  error={errors.password?.message}
                  {...registerField('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 8,
                      message: 'Password must be at least 8 characters',
                    },
                  })}
                />
                <Input
                  label="Confirm Password"
                  type="password"
                  error={errors.confirm_password?.message}
                  {...registerField('confirm_password', {
                    required: 'Please confirm your password',
                    validate: (value) =>
                      value === password || 'Passwords do not match',
                  })}
                />
                <div className="space-y-2">
                  <label className="text-sm font-medium text-white/90 pl-1">
                    Gender
                  </label>
                  <select
                    className="flex h-11 w-full rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-white backdrop-blur-sm transition-all duration-200 hover:border-white/30 focus:outline-none focus:ring-2 focus:ring-rose-500/50"
                    {...registerField('gender', {
                      required: 'Gender is required',
                    })}
                  >
                    <option value="" className="bg-gray-900">Select Gender</option>
                    <option value="male" className="bg-gray-900">Male</option>
                    <option value="female" className="bg-gray-900">Female</option>
                    <option value="non_binary" className="bg-gray-900">Non-binary</option>
                    <option value="other" className="bg-gray-900">Other</option>
                  </select>
                  {errors.gender && (
                    <p className="text-sm text-red-400 pl-1">{errors.gender.message}</p>
                  )}
                </div>
                <Input
                  label="Birth Date"
                  type="date"
                  error={errors.birth_date?.message}
                  {...registerField('birth_date', {
                    required: 'Birth date is required',
                  })}
                />
                <Input
                  label="Location"
                  error={errors.location?.message}
                  placeholder="City, Country"
                  {...registerField('location', {
                    required: 'Location is required',
                  })}
                />
              </div>
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-white/90 pl-1">
                    Bio
                  </label>
                  <textarea
                    className="flex w-full rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-white backdrop-blur-sm transition-all duration-200 hover:border-white/30 focus:outline-none focus:ring-2 focus:ring-rose-500/50 min-h-[100px]"
                    placeholder="Tell us about yourself..."
                    {...registerField('bio', {
                      required: 'Bio is required',
                      minLength: {
                        value: 20,
                        message: 'Bio must be at least 20 characters',
                      },
                    })}
                  />
                  {errors.bio && (
                    <p className="text-sm text-red-400 pl-1">{errors.bio.message}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-white/90 pl-1">
                    Profile Photo
                  </label>
                  <div className="flex items-center space-x-4">
                    <Button
                      type="button"
                      variant="glass"
                      className="relative overflow-hidden"
                      onClick={() => document.getElementById('profile_photo')?.click()}
                    >
                      Choose Photo
                      <input
                        id="profile_photo"
                        type="file"
                        accept="image/*"
                        className="absolute inset-0 opacity-0 cursor-pointer"
                        {...registerField('profile_photo')}
                      />
                    </Button>
                    <span className="text-white/70 text-sm">
                      {watch('profile_photo')?.[0]?.name || 'No file chosen'}
                    </span>
                  </div>
                </div>
              </div>
              <Button
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? 'Creating account...' : 'Create Account'}
              </Button>
            </form>
          </CardContent>
          <CardFooter className="text-sm text-center text-white/70">
            Already have an account?{' '}
            <Link href="/login" className="text-white hover:text-white/90">
              Sign in
            </Link>
          </CardFooter>
        </Card>
      </motion.div>
    </div>
  );
} 