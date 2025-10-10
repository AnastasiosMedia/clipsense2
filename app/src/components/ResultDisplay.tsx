import React from 'react';
import { invoke } from '@tauri-apps/api/tauri';

interface ResultDisplayProps {
  outputPath: string | null;
  onOpenFile: (path: string) => void;
  metrics?: {
    proxy_time?: number;
    render_time?: number;
    total_time?: number;
  };
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({
  outputPath,
  onOpenFile,
  metrics
}) => {
  if (!outputPath) {
    return null;
  }

  const handleOpenFile = () => {
    onOpenFile(outputPath);
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-3 text-green-400">✅ Highlight Video Created!</h3>
      
      <div className="space-y-3">
        <div className="bg-green-900/20 border border-green-500/50 rounded-lg p-4">
          <p className="text-sm text-green-300 mb-2">Output file:</p>
          <p className="text-xs text-gray-300 font-mono break-all">
            {outputPath}
          </p>
        </div>
        
        <button
          onClick={handleOpenFile}
          className="btn-primary w-full"
        >
          Open File Location
        </button>
        
        {/* Processing Metrics */}
        {metrics && (metrics.proxy_time || metrics.render_time || metrics.total_time) && (
          <div className="mt-4 pt-4 border-t border-gray-600">
            <h4 className="text-sm font-medium text-gray-300 mb-2">Processing Metrics</h4>
            <div className="grid grid-cols-3 gap-4 text-xs">
              {metrics.proxy_time && (
                <div className="text-center">
                  <div className="text-gray-400">Proxy Creation</div>
                  <div className="text-green-400 font-mono">{metrics.proxy_time.toFixed(1)}s</div>
                </div>
              )}
              {metrics.render_time && (
                <div className="text-center">
                  <div className="text-gray-400">Final Render</div>
                  <div className="text-blue-400 font-mono">{metrics.render_time.toFixed(1)}s</div>
                </div>
              )}
              {metrics.total_time && (
                <div className="text-center">
                  <div className="text-gray-400">Total Time</div>
                  <div className="text-yellow-400 font-mono">{metrics.total_time.toFixed(1)}s</div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
