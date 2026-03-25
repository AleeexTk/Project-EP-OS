import { usePyramidContext } from './PyramidContext';

/**
 * usePyramidState is now a wrapper around PyramidContext to maintain backward compatibility.
 * This ensures the entire application shares a single WebSocket connection.
 */
export function usePyramidState() {
  return usePyramidContext();
}



