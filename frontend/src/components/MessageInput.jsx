import React, { useState, useRef } from 'react';

export default function MessageInput({ onSend, isLoading, onMessageChange }) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;
    onSend(message.trim());
    setMessage('');
    onMessageChange?.('');
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInput = (e) => {
    setMessage(e.target.value);
    onMessageChange?.(e.target.value);
    // Auto-resize textarea
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 200) + 'px';
    }
  };

  return (
    <form id="chat-message-form" onSubmit={handleSubmit} className="glass-panel rounded-2xl p-3 mx-4 mb-4">
      <div className="flex items-end gap-2">
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          rows={1}
          disabled={isLoading}
          className="flex-1 bg-transparent text-gray-100 placeholder-gray-400 resize-none focus:outline-none text-sm md:text-base py-2.5 max-h-[200px]"
        />

      </div>
    </form>
  );
}
