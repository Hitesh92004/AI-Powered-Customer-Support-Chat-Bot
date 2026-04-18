import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { X, Server, Database, Code2, BrainCircuit, Activity, Layers, ArrowRight } from 'lucide-react';

export default function ArchitectureModal({ triggerClassName = '' }) {
  const [isOpen, setIsOpen] = useState(false);
  const defaultTriggerClassName = "px-3 py-1.5 text-xs font-medium bg-white/5 hover:bg-white/10 text-primary border border-primary/20 rounded-lg flex items-center gap-2 transition-all hover:scale-105";

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className={triggerClassName || defaultTriggerClassName}
        title="View Architecture"
      >
        <Layers size={14} />
        <span className="hidden sm:inline">Architecture Explorer</span>
      </button>

      {isOpen && createPortal(
        <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto relative animate-fade-in custom-scrollbar">
            
            {/* Header Fix for scrolling */}
            <div className="sticky top-0 z-10 glass-panel border-b border-white/10 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20">
                  <Activity className="text-white" size={20} />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">AI System Architecture</h2>
                  <p className="text-gray-400 text-xs">How this full-stack AI/ML platform works</p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-8">
              
              {/* Flow Diagram */}
              <div className="bg-slate-900/50 rounded-xl p-6 border border-white/5 relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-secondary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
                <h3 className="text-sm font-semibold text-gray-200 mb-6 flex items-center gap-2">
                  <BrainCircuit className="text-primary" size={16} /> AI Data Flow Diagram
                </h3>
                
                <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                  {/* Step 1 */}
                  <div className="flex-1 w-full glass-panel p-4 rounded-xl text-center relative z-10 hover:-translate-y-1 transition-transform duration-300">
                    <Code2 className="mx-auto mb-2 text-blue-400" size={24} />
                    <h4 className="text-sm font-bold text-white mb-1">1. User UI</h4>
                    <p className="text-[10px] text-gray-400">User prompts the AI via Vite React. Server-Sent Events (SSE) stream back generated tokens.</p>
                  </div>
                  
                  <ArrowRight className="hidden md:block text-gray-600 animate-pulse-glow" size={20} />
                  
                  {/* Step 2 */}
                  <div className="flex-1 w-full glass-panel border-primary/30 p-4 rounded-xl text-center relative z-10 hover:-translate-y-1 transition-transform duration-300 shadow-lg shadow-primary/10">
                    <Server className="mx-auto mb-2 text-primary" size={24} />
                    <h4 className="text-sm font-bold text-white mb-1">2. ML Python Backend</h4>
                    <p className="text-[10px] text-gray-400">FastAPI routes request. Machine Learning classifies intent. Queries Postgres for AI context.</p>
                  </div>

                  <ArrowRight className="hidden md:block text-gray-600 animate-pulse-glow" size={20} />

                  {/* Step 3 */}
                  <div className="flex-1 w-full glass-panel p-4 rounded-xl text-center relative z-10 hover:-translate-y-1 transition-transform duration-300">
                    <Database className="mx-auto mb-2 text-green-400" size={24} />
                    <h4 className="text-sm font-bold text-white mb-1">3. Generative AI (LLM)</h4>
                    <p className="text-[10px] text-gray-400">Groq accelerates Llama 3 generation, injecting vector context (RAG) for accurate output.</p>
                  </div>
                </div>
              </div>

              {/* Detailed Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="glass-panel p-5 rounded-xl">
                  <h4 className="text-sm font-bold text-white mb-3 border-b border-white/10 pb-2">Frontend Stack</h4>
                  <ul className="space-y-2 text-xs text-gray-300">
                    <li className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5"></span>
                      <span><strong>React 18 + Vite:</strong> Ultra-fast dev server and optimized production builds.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5"></span>
                      <span><strong>Tailwind CSS v3:</strong> Utility-first styling with custom glassmorphism components.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5"></span>
                      <span><strong>SSE Streaming:</strong> Real-time chunk-by-chunk chat rendering, identical to ChatGPT.</span>
                    </li>
                  </ul>
                </div>

                <div className="glass-panel p-5 rounded-xl relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-secondary/10 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none"></div>
                  <h4 className="text-sm font-bold text-white mb-3 border-b border-white/10 pb-2">AI & Backend Stack</h4>
                  <ul className="space-y-2 text-xs text-gray-300">
                    <li className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-secondary mt-1.5"></span>
                      <span><strong>Python FastAPI:</strong> High-performance async routing for Artificial Intelligence pipelines.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-secondary mt-1.5"></span>
                      <span><strong>Neon DB (pgvector):</strong> Serverless vector search for RAG (Retrieval-Augmented Generation).</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-secondary mt-1.5"></span>
                      <span><strong>Machine Learning:</strong> Scikit-Learn custom TF-IDF classifier for human-escalation routing.</span>
                    </li>
                  </ul>
                </div>
              </div>

            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
