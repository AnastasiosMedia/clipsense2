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
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        signal: controller.signal,
        ...options,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${errorText}`);
      }

      const data = await response.json();
      
      if (config.get('enableDebugLogs')) {
        console.log(`✅ API Response: ${endpoint}`, data);
      }
      
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`API request timed out after ${config.get('apiTimeout')}ms`);
      }
      
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
    return this.request<AutoCutResponse>('/autocut', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  static async aiAutoCut(request: AISelectionRequest): Promise<AISelectionResponse> {
    return this.request<AISelectionResponse>('/ai_autocut', {
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
