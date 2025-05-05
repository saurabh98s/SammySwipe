import * as React from 'react';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'outline' | 'secondary';
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  className = '',
  children,
  ...props
}) => {
  const base = 'inline-block text-xs font-medium rounded-full px-2 py-1';
  const variants: Record<string,string> = {
    default: 'bg-gray-100 text-gray-800',
    outline: 'border border-gray-300 text-gray-700',
    secondary: 'bg-gray-200 text-gray-900',
  };
  return (
    <span
      className={`${base} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};
