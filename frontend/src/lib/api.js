import axios from 'axios';

const normalizeApiBaseUrl = (rawUrl) => {
  const fallback = 'http://localhost:8000/api';
  if (!rawUrl) return fallback;

  const trimmed = rawUrl.trim().replace(/\/+$/, '');
  if (!trimmed) return fallback;

  try {
    const parsed = new URL(trimmed);
    if (!parsed.pathname || parsed.pathname === '/') {
      parsed.pathname = '/api';
    } else if (!parsed.pathname.endsWith('/api')) {
      parsed.pathname = `${parsed.pathname.replace(/\/+$/, '')}/api`;
    }
    return parsed.toString().replace(/\/+$/, '');
  } catch {
    return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`;
  }
};

const API_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_URL);

export const api = axios.create({ baseURL: API_URL });

const getSessionId = () => {
  let sessionId = localStorage.getItem('anonymous_session_id');
  if (!sessionId) {
    // Generate a simple random UUID-like string for anonymous tracking
    sessionId = 'guest-' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('anonymous_session_id', sessionId);
  }
  return sessionId;
};

// Attach session ID on every request
api.interceptors.request.use((config) => {
  config.headers['X-User-Id'] = getSessionId();
  return config;
});

/**
 * Stream a chat response via Server-Sent Events.
 */
export const streamChat = async (
  message, conversationId = null,
  onChunk, onDone, onError
) => {
  try {
    const sessionId = getSessionId();

    const response = await fetch(`${API_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': sessionId,
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const lines = decoder.decode(value).split('\n\n');
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === 'chunk') onChunk(data.content, null);
          else if (data.type === 'meta') onChunk('', data.conversation_id);
          else if (data.type === 'done') onDone(data.conversation_id);
          else if (data.type === 'error') onError(data.message);
        } catch (e) { /* skip malformed */ }
      }
    }
  } catch (err) {
    onError(err.message);
  }
};
