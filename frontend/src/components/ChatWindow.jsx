import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import { Bot, Sparkles } from 'lucide-react';

export default function ChatWindow({ messages, isLoading, streamingContent, onSuggestionClick }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  // Empty state
  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
        <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center mb-6 shadow-2xl shadow-primary/20">
          <Sparkles className="text-white" size={40} />
        </div>
        <h2 className="text-2xl md:text-3xl font-bold text-white mb-3">How can I help you?</h2>
        <p className="text-gray-400 max-w-md text-sm md:text-base">
          Ask me anything about our products, services, or troubleshoot an issue. I'm here to help!
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8 w-full max-w-lg">
          {[
            'How do I reset my password?',
            'What are your pricing plans?',
            'I need help with my order',
            'Tell me about your features',
          ].map((prompt, i) => (
            <button
              key={i}
              type="button"
              onClick={() => onSuggestionClick?.(prompt)}
              disabled={isLoading}
              className="text-left text-sm text-gray-300 bg-surface hover:bg-white/10 border border-white/10 p-4 rounded-xl transition-colors"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-2">
      {messages.map((msg, idx) => (
        <MessageBubble key={msg.id || idx} message={msg} />
      ))}

      {/* Streaming content */}
      {streamingContent && (
        <MessageBubble
          message={{ role: 'assistant', content: streamingContent }}
        />
      )}

      {/* Typing indicator */}
      {isLoading && !streamingContent && (
        <div className="flex justify-start mb-4">
          <div className="flex items-center gap-3 max-w-[75%]">
            <div className="w-8 h-8 rounded-full bg-surface border border-white/10 flex items-center justify-center">
              <Bot size={16} className="text-primary" />
            </div>
            <div className="px-5 py-4 rounded-2xl rounded-tl-sm bg-surface border border-white/10">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
