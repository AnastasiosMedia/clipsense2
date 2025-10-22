import React from 'react';

interface ResultDisplayProps {
  outputPath: string | null;
  onOpenFile: (path: string) => void;
  onOpenPreview?: () => void;
  metrics?: {
    proxy_time?: number;
    render_time?: number;
    total_time?: number;
  };
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({
  outputPath,
  onOpenFile,
  onOpenPreview,
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
          <p className="text-xs text-[#666666] font-mono break-all">
            {outputPath}
          </p>
        </div>
        
        <div className="flex space-x-3">
          {onOpenPreview && (
            <button
              onClick={onOpenPreview}
              className="btn-yellow flex-1"
            >
              Open Preview
            </button>
          )}
          <button
            onClick={handleOpenFile}
            className="btn-primary flex-1"
          >
            Open File Location
          </button>
        </div>
        
        {/* Processing Metrics */}
        {metrics && (metrics.proxy_time || metrics.render_time || metrics.total_time) && (
          <div className="mt-4 pt-4 border-t border-[#1a1a1a]">
            <h4 className="text-sm font-medium text-[#666666] mb-2">Processing Metrics</h4>
            <div className="grid grid-cols-3 gap-4 text-xs">
              {metrics.proxy_time && (
                <div className="text-center">
                  <div className="text-[#555555]">Proxy Creation</div>
                  <div className="text-green-400 font-mono">{metrics.proxy_time.toFixed(1)}s</div>
                </div>
              )}
              {metrics.render_time && (
                <div className="text-center">
                  <div className="text-[#555555]">Final Render</div>
                  <div className="text-white font-mono">{metrics.render_time.toFixed(1)}s</div>
                </div>
              )}
              {metrics.total_time && (
                <div className="text-center">
                  <div className="text-[#555555]">Total Time</div>
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
