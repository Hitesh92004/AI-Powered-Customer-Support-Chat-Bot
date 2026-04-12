import React, { useState, useRef } from 'react';
import { Upload, X, FileText, Loader2 } from 'lucide-react';
import { api } from '../lib/api';

export default function DocumentUpload({ isOpen, onClose, conversationId, onDocumentUploaded }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const inputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    setError(null);
    setResult(null);
    if (selectedFile) {
      const ext = selectedFile.name.split('.').pop().toLowerCase();
      if (!['pdf', 'txt'].includes(ext)) {
        setError('Only PDF and TXT files are supported.');
        return;
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be under 10MB.');
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (conversationId) formData.append('conversation_id', conversationId);

      const res = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setResult(res.data);
      if (onDocumentUploaded) {
        onDocumentUploaded(res.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setError(null);
    setResult(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="glass-panel rounded-2xl p-6 w-full max-w-md relative">
        {/* Close button */}
        <button onClick={handleClose} className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors">
          <X size={20} />
        </button>

        <h2 className="text-xl font-bold text-white mb-1">Upload Document</h2>
        <p className="text-gray-400 text-sm mb-6">Upload a PDF or TXT file to provide context for your conversation.</p>

        {error && (
          <div className="bg-red-500/10 text-red-400 border border-red-500/20 p-3 rounded-lg text-sm mb-4">
            {error}
          </div>
        )}

        {result ? (
          <div className="space-y-4">
            <div className="bg-green-500/10 text-green-400 border border-green-500/20 p-4 rounded-lg text-sm">
              <p className="font-medium mb-1">✓ Document processed!</p>
              <p className="text-gray-400">{result.filename} — {result.char_count.toLocaleString()} characters extracted</p>
            </div>
            <p className="text-gray-400 text-xs">{result.content_preview}</p>
            <button onClick={handleClose} className="w-full btn-primary py-3">Done</button>
          </div>
        ) : (
          <>
            {/* Drop Zone */}
            <div
              onClick={() => inputRef.current?.click()}
              className="border-2 border-dashed border-white/10 hover:border-primary/40 rounded-xl p-8 text-center cursor-pointer transition-colors mb-4"
            >
              <input
                ref={inputRef}
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileSelect}
                className="hidden"
              />
              {file ? (
                <div className="flex flex-col items-center gap-2">
                  <FileText className="text-primary" size={36} />
                  <p className="text-white font-medium">{file.name}</p>
                  <p className="text-gray-400 text-xs">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2">
                  <Upload className="text-gray-400" size={36} />
                  <p className="text-gray-300">Click to select a file</p>
                  <p className="text-gray-500 text-xs">PDF or TXT, up to 10MB</p>
                </div>
              )}
            </div>

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="w-full btn-primary py-3 flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Upload size={18} />
                  Upload & Extract
                </>
              )}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
