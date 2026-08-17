import React from 'react';
import clsx from 'clsx';

export const Badge = ({
  children,
  variant = 'primary',
  size = 'base',
  icon: Icon,
  className,
  ...props
}) => {
  const variantStyles = {
    primary: 'bg-datafacz-orange/20 text-datafacz-orange',
    success: 'bg-emerald-500/20 text-emerald-300',
    error: 'bg-datafacz-red/20 text-datafacz-red',
    warning: 'bg-yellow-500/20 text-yellow-300',
    gray: 'bg-datafacz-gray-800/50 text-datafacz-gray-400',
  };

  const sizeStyles = {
    sm: 'px-2 py-1 text-xs',
    base: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 rounded-full font-medium',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {Icon && <Icon size={14} />}
      {children}
    </span>
  );
};
