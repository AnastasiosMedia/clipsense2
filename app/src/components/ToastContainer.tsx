import React from 'react';
import { Toast, ToastProps } from './Toast';

export interface ToastData extends Omit<ToastProps, 'onClose'> {
  id: string;
}

interface ToastContainerProps {
  toasts: ToastData[];
  onRemoveToast: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({
  toasts,
  onRemoveToast
}) => {
  return (
    <div className="fixed top-0 right-0 z-50 space-y-2 p-4">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          duration={toast.duration}
          onClose={() => onRemoveToast(toast.id)}
        />
      ))}
    </div>
  );
};
