import React, { useState, useEffect, useCallback } from 'react';
import { Loader2, Send } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import MessageInput from '../components/MessageInput';
import ArchitectureModal from '../components/ArchitectureModal';
import { api, streamChat } from '../lib/api';

export default function ChatPage() {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [draftMessage, setDraftMessage] = useState('');

  // Load conversations on mount
  const loadConversations = useCallback(async () => {
    try {
      const res = await api.get('/conversations');
      setConversations(res.data.conversations || []);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Load messages when conversation changes
  useEffect(() => {
    if (!currentConversationId) {
      setMessages([]);
      return;
    }
    const loadMessages = async () => {
      try {
        const res = await api.get(`/conversations/${currentConversationId}`);
        setMessages(res.data.messages || []);
      } catch (err) {
        console.error('Failed to load messages:', err);
      }
    };
    loadMessages();
  }, [currentConversationId]);

  const handleNewChat = () => {
    setCurrentConversationId(null);
    setMessages([]);
  };

  const handleSend = async (message) => {
    // Optimistically add user message
    const userMsg = { role: 'user', content: message, id: `temp-${Date.now()}` };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setStreamingContent('');

    try {
      await streamChat(
        message,
        currentConversationId,
        // onChunk
        (content, convId) => {
          if (convId && !currentConversationId) {
            setCurrentConversationId(convId);
          }
          if (content) {
            setStreamingContent(prev => prev + content);
          }
        },
        // onDone
        (conversationId) => {
          setStreamingContent(prev => {
            // Move streaming content to messages
            if (prev) {
              setMessages(msgs => [...msgs, { role: 'assistant', content: prev, id: `ai-${Date.now()}` }]);
            }
            return '';
          });
          setIsLoading(false);
          if (conversationId) setCurrentConversationId(conversationId);
          loadConversations();
        },
        // onError
        (errorMsg) => {
          setStreamingContent('');
          setMessages(prev => [...prev, { role: 'assistant', content: `⚠️ Error: ${errorMsg}`, id: `err-${Date.now()}` }]);
          setIsLoading(false);
        }
      );
    } catch (err) {
      setIsLoading(false);
      setStreamingContent('');
      console.error('Chat error:', err);
    }
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        conversations={conversations}
        currentId={currentConversationId}
        onSelect={setCurrentConversationId}
        onNew={handleNewChat}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="h-14 flex items-center justify-between px-6 md:px-8 border-b border-white/10 bg-surface/80 backdrop-blur-md shadow-sm z-10">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-bold text-gray-200 truncate ml-10 md:ml-0 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
              {currentConversationId
                ? conversations.find(c => c.id === currentConversationId)?.title || 'Chat'
                : 'New Conversation'
              }
            </h2>
          </div>
          
          <ArchitectureModal />
        </div>

        {/* Messages */}
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          streamingContent={streamingContent}
          onSuggestionClick={handleSend}
        />

        {/* Input */}
        <MessageInput
          onSend={handleSend}
          isLoading={isLoading}
          onMessageChange={setDraftMessage}
        />
      </div>

      {/* Floating Send Button */}
      <button
        type="button"
        title="Send Message"
        disabled={!draftMessage.trim() || isLoading}
        onClick={() => document.getElementById('chat-message-form')?.requestSubmit()}
        className="fixed bottom-6 right-6 z-40 w-12 h-12 rounded-full bg-gradient-to-br from-primary to-secondary shadow-lg shadow-primary/30 flex items-center justify-center text-white hover:scale-110 transition-transform duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
      >
        {isLoading ? <Loader2 size={22} className="animate-spin" /> : <Send size={22} />}
      </button>
    </div>
  );
}
