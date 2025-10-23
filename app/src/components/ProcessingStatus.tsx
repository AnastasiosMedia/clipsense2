import React from 'react';
import { ProcessingState } from '../types';

interface ProcessingStatusProps {
  processingState: ProcessingState;
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  processingState
}) => {
  if (!processingState.isProcessing && !processingState.error) {
    return null;
  }

  return (
    <div className="card transition-all duration-500 ease-in-out">
      <h3 className="text-lg font-semibold mb-3 transition-all duration-300">Processing Status</h3>
      
      {processingState.isProcessing && (
        <div className="space-y-3 transition-all duration-500 ease-in-out">
          <div className="flex items-center space-x-3 transition-all duration-300">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            <span className="text-sm text-[#666666] transition-all duration-300">Rendering...</span>
          </div>
          
          <div className="w-full bg-[#0f0f0f] rounded-full h-2 transition-all duration-300">
            <div 
              className="bg-white h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${processingState.progress}%` }}
            ></div>
          </div>
          
          <p className="text-sm text-[#555555] transition-all duration-300">
            {processingState.currentStep}
          </p>
        </div>
      )}
      
      {processingState.error && (
        <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-4 transition-all duration-500 ease-in-out">
          <div className="flex items-center space-x-2 transition-all duration-300">
            <svg className="w-5 h-5 text-red-400 transition-all duration-300" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="text-red-400 font-medium transition-all duration-300">Error</span>
          </div>
          <p className="text-red-300 text-sm mt-2 transition-all duration-300">{processingState.error}</p>
        </div>
      )}
    </div>
  );
};
