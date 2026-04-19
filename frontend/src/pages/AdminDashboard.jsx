import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { LayoutDashboard, MessageSquare, Ticket, BarChart3, TrendingUp, AlertTriangle } from 'lucide-react';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/admin/dashboard');
        setStats(response.data);
      } catch (err) {
        setError('Failed to load dashboard stats.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-red-500 bg-red-100 p-4 rounded-lg">{error}</div>
      </div>
    );
  }

  const sentiment = stats?.sentiment_distribution || { positive: 0, neutral: 0, negative: 0 };
  const totalSentiments = sentiment.positive + sentiment.neutral + sentiment.negative || 1;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <LayoutDashboard className="w-8 h-8 text-blue-600" />
              Admin Support Dashboard
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-2">
              Overview of AI Chatbot performance and escalations
            </p>
          </div>
        </header>

        {/* Top Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 text-blue-600 rounded-lg">
                <MessageSquare className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Chats</p>
                <h3 className="text-2xl font-bold">{stats?.total_chats || 0}</h3>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-red-100 text-red-600 rounded-lg">
                <Ticket className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Open Tickets</p>
                <h3 className="text-2xl font-bold">{stats?.total_tickets || 0}</h3>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 text-green-600 rounded-lg">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Avg Resolution</p>
                <h3 className="text-2xl font-bold">~2m</h3>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-orange-100 text-orange-600 rounded-lg">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Escalation Rate</p>
                <h3 className="text-2xl font-bold">
                  {stats?.total_chats ? Math.round((stats.total_tickets / stats.total_chats) * 100) : 0}%
                </h3>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Sentiment Distribution */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-500" />
              Message Sentiment Distribution
            </h3>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-green-600 font-medium">Positive</span>
                  <span>{Math.round((sentiment.positive / totalSentiments) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                  <div className="bg-green-500 h-2.5 rounded-full" style={{ width: `${(sentiment.positive / totalSentiments) * 100}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 dark:text-gray-400 font-medium">Neutral</span>
                  <span>{Math.round((sentiment.neutral / totalSentiments) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                  <div className="bg-gray-400 h-2.5 rounded-full" style={{ width: `${(sentiment.neutral / totalSentiments) * 100}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-red-600 font-medium">Negative</span>
                  <span>{Math.round((sentiment.negative / totalSentiments) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                  <div className="bg-red-500 h-2.5 rounded-full" style={{ width: `${(sentiment.negative / totalSentiments) * 100}%` }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Frequent Queries */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-6">Most Frequent User Queries</h3>
            <div className="space-y-4">
              {stats?.most_frequent_queries?.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg transition-colors">
                  <span className="font-medium text-gray-700 dark:text-gray-300">"{item.query}"</span>
                  <span className="px-3 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full text-sm font-semibold">
                    {item.count} hits
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
