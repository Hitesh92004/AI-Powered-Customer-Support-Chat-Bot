import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Plus, LogOut, ChevronRight, Menu, X } from 'lucide-react';

export default function Sidebar({ conversations, currentId, onSelect, onNew, onDelete }) {
  const { signOut, user } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const handleSignOut = async () => {
    // If this is the demo account, clear all conversations before logging out
    if (user?.email === 'demo@example.com') {
      try {
        await api.delete('/conversations/all');
      } catch (e) {
        // Non-critical, continue with sign out
      }
    }
    await signOut();
    navigate('/login');
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-surface border-r border-white/10 w-64">
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <button
          onClick={() => {
            onNew();
            setIsOpen(false);
          }}
          className="w-full flex items-center justify-center gap-2 btn-primary"
        >
          <Plus size={18} />
          <span>New Chat</span>
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            onClick={() => {
              onSelect(conv.id);
              setIsOpen(false);
            }}
            className={`group flex items-center justify-between px-3 py-3 rounded-lg cursor-pointer transition-colors ${
              currentId === conv.id ? 'bg-primary/20 text-white' : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
            }`}
          >
            <div className="flex items-center gap-3 overflow-hidden">
              <MessageSquare size={16} className="flex-shrink-0" />
              <span className="truncate text-sm font-medium">{conv.title}</span>
            </div>
          </div>
        ))}
        {conversations.length === 0 && (
          <div className="text-center text-gray-500 text-sm mt-8">
            No conversations yet
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center justify-between">
          <div className="text-xs text-gray-400 truncate max-w-[150px]">
            {user?.email}
          </div>
          <button
            onClick={handleSignOut}
            className="text-gray-400 hover:text-white transition-colors"
            title="Sign Out"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Toggle */}
      <button
        className="md:hidden fixed top-3 left-3 z-50 p-2 bg-surface text-white rounded-md border border-white/10"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Desktop Sidebar */}
      <div className="hidden md:block h-screen">
        <SidebarContent />
      </div>

      {/* Mobile Sidebar Overlay */}
      {isOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-background/80 backdrop-blur-sm flex">
          <SidebarContent />
          <div className="flex-1" onClick={() => setIsOpen(false)} />
        </div>
      )}
    </>
  );
}
