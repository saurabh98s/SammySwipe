'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';

export default function LandingPage() {
  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-rose-400 via-fuchsia-500 to-indigo-500">
      {/* Mesh gradient overlay */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iYSIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVHJhbnNmb3JtPSJyb3RhdGUoNDUpIj48cGF0aCBkPSJNMCAyMGgxMHYxMEgwem0yMCAwaDF2MTBoLTF6IiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNhKSIvPjwvc3ZnPg==')] opacity-20"></div>

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-display font-bold text-white">
            SammySwipe
          </Link>
          <div className="space-x-4">
            <Link href="/login">
              <Button variant="ghost" className="text-white hover:bg-white/20">Log in</Button>
            </Link>
            <Link href="/register">
              <Button className="bg-white text-rose-500 hover:bg-white/90">Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 relative z-10">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-5xl md:text-6xl font-display font-bold text-white"
            >
              Find Your Perfect Match with{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 via-pink-200 to-pink-100">
                AI-Powered Dating
              </span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="mt-6 text-xl text-white/90"
            >
              Experience dating reimagined with advanced AI matching, personality analysis,
              and genuine connections based on shared interests and compatibility.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="mt-10 space-x-4"
            >
              <Link href="/register">
                <Button size="lg" className="text-lg bg-white text-rose-500 hover:bg-white/90">
                  Start Your Journey
                </Button>
              </Link>
              <Link href="/about">
                <Button size="lg" variant="outline" className="text-lg text-white border-white hover:bg-white/20">
                  Learn More
                </Button>
              </Link>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 relative z-10">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-display font-bold text-center mb-12 text-white">
            Why Choose SammySwipe?
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Feature
              title="AI-Powered Matching"
              description="Our advanced AI analyzes your interests, personality, and behavior to find truly compatible matches."
              icon="🤖"
            />
            <Feature
              title="Genuine Connections"
              description="Focus on meaningful relationships with people who share your interests and values."
              icon="💝"
            />
            <Feature
              title="Safe & Secure"
              description="Advanced fraud detection and verification systems ensure a safe dating environment."
              icon="🛡️"
            />
          </div>
        </div>
      </section>

      {/* Add new sections after Features Section */}
      <section className="py-20 relative z-10">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-display font-bold text-center mb-12 text-white">
            How It Works
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/20 flex items-center justify-center text-2xl">
                1
              </div>
              <h3 className="text-lg font-semibold mb-2 text-white">Create Profile</h3>
              <p className="text-white/70">Sign up and tell us about yourself</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/20 flex items-center justify-center text-2xl">
                2
              </div>
              <h3 className="text-lg font-semibold mb-2 text-white">AI Matching</h3>
              <p className="text-white/70">Our AI finds your perfect matches</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/20 flex items-center justify-center text-2xl">
                3
              </div>
              <h3 className="text-lg font-semibold mb-2 text-white">Connect</h3>
              <p className="text-white/70">Start chatting with your matches</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/20 flex items-center justify-center text-2xl">
                4
              </div>
              <h3 className="text-lg font-semibold mb-2 text-white">Meet</h3>
              <p className="text-white/70">Take your connection to the real world</p>
            </motion.div>
          </div>
        </div>
      </section>

      <section className="py-20 relative z-10">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-display font-bold text-center mb-12 text-white">
            Success Stories
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              whileHover={{ y: -5 }}
              transition={{ duration: 0.2 }}
              viewport={{ once: true }}
              className="p-6 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20"
            >
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 rounded-full bg-white/20 mr-4"></div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Sarah & Mike</h3>
                  <p className="text-white/70">Matched 6 months ago</p>
                </div>
              </div>
              <p className="text-white/80">
                "Thanks to SammySwipe's AI matching, we found each other instantly. The compatibility was incredible!"
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              whileHover={{ y: -5 }}
              transition={{ duration: 0.2, delay: 0.1 }}
              viewport={{ once: true }}
              className="p-6 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20"
            >
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 rounded-full bg-white/20 mr-4"></div>
                <div>
                  <h3 className="text-lg font-semibold text-white">David & Emma</h3>
                  <p className="text-white/70">Matched 1 year ago</p>
                </div>
              </div>
              <p className="text-white/80">
                "The personality matching was spot on! We share so many interests and values."
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              whileHover={{ y: -5 }}
              transition={{ duration: 0.2, delay: 0.2 }}
              viewport={{ once: true }}
              className="p-6 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20"
            >
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 rounded-full bg-white/20 mr-4"></div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Alex & Jordan</h3>
                  <p className="text-white/70">Matched 9 months ago</p>
                </div>
              </div>
              <p className="text-white/80">
                "We would have never met without SammySwipe. The AI knew exactly what we were looking for!"
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      <section className="py-20 relative z-10">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-display font-bold mb-6 text-white">
              Ready to Find Your Perfect Match?
            </h2>
            <p className="text-xl mb-10 text-white/90">
              Join thousands of happy couples who found love through SammySwipe's AI-powered matching.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/register">
                <Button size="lg" className="text-lg w-full sm:w-auto">
                  Get Started Now
                </Button>
              </Link>
              <Link href="/about">
                <Button size="lg" variant="glass" className="text-lg w-full sm:w-auto">
                  Learn More
                </Button>
              </Link>
            </div>
            <p className="mt-6 text-white/70">
              Free to join • AI-powered matching • Verified profiles
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 relative z-10 border-t border-white/20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-bold mb-4 text-white">SammySwipe</h3>
              <p className="text-white/70">
                Making meaningful connections through AI-powered matchmaking.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-bold mb-4 text-white">Company</h4>
              <ul className="space-y-2">
                <li>
                  <Link href="/about" className="text-white/70 hover:text-white">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link href="/careers" className="text-white/70 hover:text-white">
                    Careers
                  </Link>
                </li>
                <li>
                  <Link href="/blog" className="text-white/70 hover:text-white">
                    Blog
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-bold mb-4 text-white">Support</h4>
              <ul className="space-y-2">
                <li>
                  <Link href="/help" className="text-white/70 hover:text-white">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link href="/safety" className="text-white/70 hover:text-white">
                    Safety Center
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="text-white/70 hover:text-white">
                    Contact Us
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-bold mb-4 text-white">Legal</h4>
              <ul className="space-y-2">
                <li>
                  <Link href="/privacy" className="text-white/70 hover:text-white">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link href="/terms" className="text-white/70 hover:text-white">
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link href="/cookies" className="text-white/70 hover:text-white">
                    Cookie Policy
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-white/20 text-center text-white/70">
            <p>&copy; {new Date().getFullYear()} SammySwipe. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function Feature({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5, scale: 1.02 }}
      transition={{ duration: 0.2 }}
      viewport={{ once: true }}
      className="group p-6 rounded-xl bg-white/10 backdrop-blur-sm text-center border border-white/20 hover:border-white/40 hover:bg-white/20 transition-all duration-200"
    >
      <div className="text-5xl mb-4 transform transition-transform duration-200 group-hover:scale-110">{icon}</div>
      <h3 className="text-xl font-display font-semibold mb-3 text-white">{title}</h3>
      <p className="text-white/80">{description}</p>
    </motion.div>
  );
}
