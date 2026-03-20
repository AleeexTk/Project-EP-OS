const trimTrailingSlash = (value: string) => value.replace(/\/+$/, '');

const toWsUrl = (httpBase: string, path: string) => {
  const wsBase = httpBase.replace(/^http/, 'ws');
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${trimTrailingSlash(wsBase)}${normalizedPath}`;
};

export const CORE_API_BASE = trimTrailingSlash(import.meta.env.VITE_CORE_API_BASE ?? 'http://127.0.0.1:8000');
export const SESSION_API_BASE = trimTrailingSlash(import.meta.env.VITE_SESSION_API_BASE ?? 'http://127.0.0.1:8000/v1');

export const CORE_WS_URL = import.meta.env.VITE_CORE_WS_URL ?? toWsUrl(CORE_API_BASE, '/ws');
export const SWARM_WS_URL = import.meta.env.VITE_SWARM_WS_URL ?? toWsUrl(SESSION_API_BASE, '/ws/swarm');
