/**
 * Frontend configuration for ClipSense
 * Handles environment variables and API settings
 */

// Type definitions for Vite environment variables (ambient via declaration merging)
declare global {
  interface ImportMetaEnv {
    readonly VITE_API_BASE_URL?: string;
    readonly VITE_API_TIMEOUT?: string;
    readonly VITE_ENABLE_DEBUG_LOGS?: string;
  }
}

// Use Vite's ImportMeta type contextually without redeclaration

export interface AppConfig {
  apiBaseUrl: string;
  apiTimeout: number;
  enableDebugLogs: boolean;
}

class Config {
  private static instance: Config;
  private config: AppConfig;

  private constructor() {
    this.config = {
      apiBaseUrl: (import.meta as any).env?.VITE_API_BASE_URL || 'http://127.0.0.1:8123',
      apiTimeout: parseInt((import.meta as any).env?.VITE_API_TIMEOUT || '300000'),
      enableDebugLogs: ((import.meta as any).env?.VITE_ENABLE_DEBUG_LOGS) === 'true'
    };
  }

  public static getInstance(): Config {
    if (!Config.instance) {
      Config.instance = new Config();
    }
    return Config.instance;
  }

  public get<K extends keyof AppConfig>(key: K): AppConfig[K] {
    return this.config[key];
  }

  public getAll(): AppConfig {
    return { ...this.config };
  }

  public updateConfig(updates: Partial<AppConfig>): void {
    this.config = { ...this.config, ...updates };
  }
}

export default Config.getInstance();
