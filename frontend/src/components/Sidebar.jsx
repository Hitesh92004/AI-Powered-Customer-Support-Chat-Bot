import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Plus, Trash2, Menu, X, Rocket } from 'lucide-react';
import AboutModal from './AboutModal';
import { api } from '../lib/api';

export default function Sidebar({ conversations, currentId, onSelect, onNew }) {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const handleClearDemo = async () => {
    try {
       // Optional: implement clear all backend endpoint if needed in future
       localStorage.removeItem('anonymous_session_id');
       window.location.reload();
    } catch {
       window.location.reload();
    }
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
        <div className="mb-3">
          <AboutModal triggerClassName="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white transition-colors text-sm" />
        </div>
        <div className="flex items-center justify-between">
          <div className="text-xs text-primary flex items-center gap-1 font-semibold">
            <Rocket size={14} />
            Demo Mode Active
          </div>
          <button
            onClick={handleClearDemo}
            className="text-gray-400 hover:text-red-400 transition-colors flex items-center pr-1"
            title="Clear Demo Session"
          >
            <Trash2 size={18} />
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
