import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, Loader2, Sparkles, UserCircle2 } from 'lucide-react';
import { api } from '../lib/api';
import AboutModal from '../components/AboutModal';
import ArchitectureModal from '../components/ArchitectureModal';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);
  const { signIn, signUp } = useAuth();
  const navigate = useNavigate();

  const handleDemoSignIn = async () => {
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      // Direct call to demo endpoint without auth context since it manages its own token set
      const res = await api.post('/auth/demo');
      const { access_token, user_id, email } = res.data;
      const userData = { id: user_id, email };
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Force reload to pick up context correctly since we bypassed AuthContext signIn method
      window.location.href = '/';
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Demo sign in failed.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      if (isLogin) {
        await signIn(email, password);
        navigate('/');
      } else {
        await signUp(email, password);
        setSuccess('Account created! You are now logged in.');
        navigate('/');
      }
    } catch (err) {
      // Handle axios error response
      const msg = err.response?.data?.detail || err.message || 'Something went wrong.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/30 rounded-full blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary/30 rounded-full blur-[120px]" />

      <div className="w-full max-w-md glass-panel rounded-2xl p-8 relative z-10">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary mb-4 shadow-lg shadow-primary/20">
            <Sparkles className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-gray-400">
            {isLogin ? 'Sign in to your AI Assistant' : 'Sign up to get started for free'}
          </p>
        </div>

        {error && (
          <div className="p-4 rounded-lg mb-6 text-sm bg-red-500/10 text-red-400 border border-red-500/20">
            {error}
          </div>
        )}
        {success && (
          <div className="p-4 rounded-lg mb-6 text-sm bg-green-500/10 text-green-400 border border-green-500/20">
            {success}
          </div>
        )}

        {/* Demo Button */}
        <button
          onClick={handleDemoSignIn}
          disabled={loading}
          className="w-full btn-secondary flex justify-center items-center py-3 mb-6 gap-2 border-primary/30 hover:border-primary/60 text-primary-100 bg-primary/5"
        >
          <UserCircle2 size={20} className="text-primary" />
          <span>Try Demo Account</span>
        </button>

        <div className="flex items-center py-4 mb-2">
          <div className="flex-grow h-px bg-white/10"></div>
          <span className="flex-shrink-0 px-4 text-gray-500 text-sm">or with email</span>
          <div className="flex-grow h-px bg-white/10"></div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="email" required value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email address"
              className="input-field pl-10"
            />
          </div>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="password" required value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password (min 6 chars)"
              className="input-field pl-10" minLength={6}
            />
          </div>
          <button type="submit" disabled={loading}
            className="w-full btn-primary flex justify-center items-center py-3 mt-4">
            {loading
              ? <Loader2 className="animate-spin" size={20} />
              : (isLogin ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        <div className="mt-8 text-center text-gray-400 text-sm">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => { setIsLogin(!isLogin); setError(null); setSuccess(null); }}
            className="text-primary hover:text-primary/80 transition-colors font-medium"
          >
            {isLogin ? 'Sign up' : 'Sign in'}
          </button>
        </div>
      </div>

      {/* External Presentation Links */}
      <div className="absolute bottom-8 flex flex-col sm:flex-row items-center gap-4 z-20">
        <ArchitectureModal triggerClassName="px-4 py-2 text-sm font-medium bg-surface/80 backdrop-blur-md text-white border border-white/10 shadow-lg rounded-xl flex items-center gap-2 transition-all hover:scale-105 hover:bg-white/10" />
        <AboutModal triggerClassName="px-4 py-2 text-sm font-medium bg-surface/80 backdrop-blur-md text-white border border-white/10 shadow-lg rounded-xl flex items-center gap-2 transition-all hover:scale-105 hover:bg-white/10 text-center" />
      </div>
    </div>
  );
}
