import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className="w-12 h-12 rounded-full border-4 border-solid border-[#1e2d4a] border-t-[#3b82f6] animate-pulse spin-animation" style={{animation: 'spin 1.5s linear infinite'}}></div>
      <p className="mt-4 text-[#3b82f6] font-semibold tracking-wide">Loading...</p>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default LoadingSpinner;
