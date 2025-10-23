/**
 * API service for communicating with the Python FastAPI backend
 */

import { AutoCutRequest, AutoCutResponse, HealthResponse, AISelectionRequest, AISelectionResponse } from '../types';
import config from '../config';

export class ApiService {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${config.get('apiBaseUrl')}${endpoint}`;
    
    if (config.get('enableDebugLogs')) {
      console.log(`🌐 API Request: ${options.method || 'GET'} ${url}`);
    }
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.get('apiTimeout'));
    
    try {
      console.log(`🚀 Starting request to ${url} with timeout ${config.get('apiTimeout')}ms`);
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        signal: controller.signal,
        ...options,
      });

      clearTimeout(timeoutId);
      console.log(`📡 Response received: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API request failed: ${response.status} ${errorText}`);
        throw new Error(`API request failed: ${response.status} ${errorText}`);
      }

      const data = await response.json();
      console.log(`✅ Response data:`, data);
      
      if (config.get('enableDebugLogs')) {
        console.log(`✅ API Response: ${endpoint}`, data);
      }
      
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error && error.name === 'AbortError') {
        console.error(`⏰ Request timeout after ${config.get('apiTimeout')}ms for ${url}`);
        throw new Error(`API request timed out after ${config.get('apiTimeout')}ms`);
      }
      
      console.error(`❌ Request error for ${url}:`, error);
      throw error;
    }
  }

  static async ping(): Promise<{ message: string; timestamp: number }> {
    return this.request<{ message: string; timestamp: number }>('/ping');
  }

  static async healthCheck(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  static async autoCut(request: AutoCutRequest): Promise<AutoCutResponse> {
    console.log('🎬 AutoCut request:', {
      clips: request.clips,
      music: request.music,
      target_seconds: request.target_seconds
    });
    
    try {
      const result = await this.request<AutoCutResponse>('/autocut', {
        method: 'POST',
        body: JSON.stringify(request),
      });
      console.log('✅ AutoCut response:', result);
      return result;
    } catch (error) {
      console.error('❌ AutoCut error:', error);
      throw error;
    }
  }

  static async aiAutoCut(request: AISelectionRequest): Promise<AISelectionResponse> {
    return this.request<AISelectionResponse>('/ai_autocut', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  static async generateStoryNarrative(request: {
    clips: string[];
    narrative_style?: string;
    target_duration?: number;
  }): Promise<{
    ok: boolean;
    story_narrative?: {
      story_title: string;
      story_theme: string;
      narrative_structure: string;
      story_arc: any[];
      selected_clips: any[];
      narrative_flow: string;
      emotional_journey: string[];
      story_duration: number;
      story_notes: string;
    };
    error?: string;
  }> {
    return this.request('/generate_story_narrative', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Async preview flow
  static async previewStart(request: AutoCutRequest): Promise<{ ok: boolean; job_id?: string; error?: string }> {
    return this.request<{ ok: boolean; job_id?: string; error?: string }>('/preview/start', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  static async previewStatus(jobId: string): Promise<{ ok: boolean; job_id: string; status: string; progress: number; current_step: string; error?: string }> {
    return this.request<{ ok: boolean; job_id: string; status: string; progress: number; current_step: string; error?: string }>(`/preview/status/${jobId}`);
  }

  static async previewResult(jobId: string): Promise<{ ok: boolean; preview: any }> {
    return this.request<{ ok: boolean; preview: any }>(`/preview/result/${jobId}`);
  }
}
