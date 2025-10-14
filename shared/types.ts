/**
 * Shared TypeScript types for ClipSense
 * Used by both frontend and backend for type safety
 */

export interface AutoCutRequest {
  clips: string[];
  music: string;
  target_seconds: number;
  quality_settings?: any;
  story_style?: string;
  style_preset?: string;
  use_ai_selection?: boolean;
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

export interface AISelectionRequest {
  clips: string[];
  music_path: string;
  target_duration: number;
  story_style: string;
  style_preset: string;
  use_ai_selection: boolean;
}

export interface AISelectionResponse {
  ok: boolean;
  proxy_output?: string;
  timeline_path?: string;
  timeline_hash?: string;
  proxy_time?: number;
  render_time?: number;
  total_time?: number;
  selected_clips?: any[];
  story_breakdown?: any;
  quality_metrics?: any;
  error?: string;
}

export interface StoryStyle {
  id: string;
  name: string;
  description: string;
}

export interface StylePreset {
  id: string;
  name: string;
  description: string;
  story_style: string;
}
