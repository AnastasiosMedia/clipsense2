/**
 * Shared TypeScript types for ClipSense
 * Used by both frontend and backend for type safety
 */

export interface AutoCutRequest {
  clips: string[];
  music: string;
  target_seconds: number;
}

export interface AutoCutResponse {
  ok: boolean;
  output?: string;
  error?: string;
  proxy_time?: number;
  render_time?: number;
  total_time?: number;
}

export interface HealthResponse {
  status: string;
  ffmpeg_available: boolean;
  ffmpeg_version?: string;
  ffmpeg_path?: string;
  ffprobe_path?: string;
  installation_instructions?: string;
  error?: string;
}

export interface FileSelection {
  clips: string[];
  music: string | null;
}

export interface ProcessingState {
  isProcessing: boolean;
  progress: number;
  currentStep: string;
  error: string | null;
}
