import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { X, Terminal, Briefcase, Mail, Code2, ExternalLink, Sparkles, User } from 'lucide-react';

const DEVELOPER = {
  name: 'Hitesh Priyadarshi',
  role: 'Full-Stack Developer',
  bio: 'B.Tech student passionate about building AI-powered web applications. This project demonstrates a production-ready chatbot with Groq (Llama 3), FastAPI, React, and Neon PostgreSQL (pgvector).',
  github: 'https://github.com/Hitesh92004',
  linkedin: 'https://linkedin.com/in/hiteshpriyadarshi',
  email: 'hiteshpriyadarshis@gmail.com',
  tech: ['React + Vite', 'FastAPI', 'Groq (Llama 3)', 'Neon PostgreSQL', 'Scikit-Learn', 'JWT Auth'],
};

export default function AboutModal({ triggerClassName = '' }) {
  const [isOpen, setIsOpen] = useState(false);
  const defaultTriggerClassName = "fixed bottom-6 right-6 z-40 w-12 h-12 rounded-full bg-gradient-to-br from-primary to-secondary shadow-lg shadow-primary/30 flex items-center justify-center text-white hover:scale-110 transition-transform duration-200";

  return (
    <>
      {/* Floating About Button */}
      <button
        onClick={() => setIsOpen(true)}
        title="About Developer"
        className={triggerClassName || defaultTriggerClassName}
      >
        <User size={22} />
      </button>

      {/* Modal */}
      {isOpen && createPortal(
        <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-4">
          <div className="glass-panel rounded-2xl p-6 w-full max-w-md relative animate-fade-in shadow-2xl shadow-primary/20">
            {/* Close */}
            <button
              onClick={() => setIsOpen(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
            >
              <X size={20} />
            </button>

            {/* Header */}
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20 flex-shrink-0">
                <Sparkles className="text-white" size={28} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">{DEVELOPER.name}</h2>
                <p className="text-primary text-sm font-medium">{DEVELOPER.role}</p>
              </div>
            </div>

            {/* Bio */}
            <p className="text-gray-400 text-sm leading-relaxed mb-6">
              {DEVELOPER.bio}
            </p>

            {/* Tech Stack */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <Code2 size={16} className="text-primary" />
                <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Built With</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {DEVELOPER.tech.map((t) => (
                  <span key={t} className="text-xs px-2.5 py-1 rounded-full bg-primary/10 text-primary border border-primary/20">
                    {t}
                  </span>
                ))}
              </div>
            </div>

            {/* Links */}
            <div className="flex gap-3">
              <a
                href={DEVELOPER.github}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white transition-colors text-sm"
              >
                <Terminal size={16} />
                GitHub
                <ExternalLink size={12} className="opacity-50" />
              </a>
              <a
                href={DEVELOPER.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl border border-primary/20 bg-primary/5 hover:bg-primary/10 text-primary transition-colors text-sm"
              >
                <Briefcase size={16} />
                LinkedIn
                <ExternalLink size={12} className="opacity-50" />
              </a>

              <a
                href={`mailto:${DEVELOPER.email}`}
                className="flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white transition-colors"
                title={DEVELOPER.email}
              >
                <Mail size={16} />
              </a>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
