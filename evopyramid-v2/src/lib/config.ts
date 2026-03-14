const trimTrailingSlash = (value: string) => value.replace(/\/+$/, '');

const toWsUrl = (httpBase: string, path: string) => {
  const url = new URL(path, `${trimTrailingSlash(httpBase)}/`);
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  return url.toString();
};

export const CORE_API_BASE = trimTrailingSlash(import.meta.env.VITE_CORE_API_BASE ?? 'http://127.0.0.1:8000');
export const SESSION_API_BASE = trimTrailingSlash(import.meta.env.VITE_SESSION_API_BASE ?? 'http://127.0.0.1:8001');

export const CORE_WS_URL = import.meta.env.VITE_CORE_WS_URL ?? toWsUrl(CORE_API_BASE, '/ws');
export const SWARM_WS_URL = import.meta.env.VITE_SWARM_WS_URL ?? toWsUrl(SESSION_API_BASE, '/ws/swarm');
