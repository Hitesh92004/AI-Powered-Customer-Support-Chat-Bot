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
    // Handle non-absolute URLs gracefully
    return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`;
  }
};

const API_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_URL);

export const api = axios.create({ baseURL: API_URL });

// Attach token from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

/**
 * Stream a chat response via Server-Sent Events.
 */
export const streamChat = async (
  message, conversationId = null, documentContext = null,
  onChunk, onDone, onError
) => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('Not authenticated');

    const response = await fetch(`${API_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        document_context: documentContext,
      }),
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return;
      }
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
