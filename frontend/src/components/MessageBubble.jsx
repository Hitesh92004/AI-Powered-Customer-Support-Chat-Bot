import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Bot } from 'lucide-react';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} group mb-4`}>
      <div className={`flex max-w-[85%] md:max-w-[75%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-3`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1 ${isUser ? 'bg-primary shadow-lg shadow-primary/20' : 'bg-surface border border-white/10'}`}>
          {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-primary" />}
        </div>

        {/* Bubble */}
        <div className={`px-5 py-3.5 rounded-2xl ${
          isUser 
            ? 'bg-primary text-white rounded-tr-sm shadow-lg shadow-primary/10' 
            : 'bg-surface border border-white/10 text-gray-100 rounded-tl-sm shadow-md'
        }`}>
          <ReactMarkdown 
            className={`prose ${isUser ? 'prose-invert' : 'prose-invert'} max-w-none text-sm md:text-base leading-relaxed break-words`}
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
              a: ({node, ...props}) => <a className="text-blue-400 hover:underline" {...props} />,
              code: ({node, inline, ...props}) => 
                inline ? 
                  <code className="bg-black/30 px-1.5 py-0.5 rounded text-xs text-primary" {...props} /> :
                  <div className="bg-black/50 rounded-md p-3 my-2 overflow-x-auto">
                    <code className="text-sm font-mono text-gray-300" {...props} />
                  </div>
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
