import React from 'react';
import clsx from 'clsx';

export const Button = ({
  children,
  variant = 'primary',
  size = 'base',
  fullWidth = false,
  disabled = false,
  loading = false,
  icon: Icon,
  className,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-datafacz-dark focus:ring-datafacz-orange disabled:opacity-50 disabled:cursor-not-allowed';

  const variantStyles = {
    primary: 'bg-gradient-to-r from-datafacz-yellow via-datafacz-orange to-datafacz-red text-white hover:shadow-hover active:scale-95',
    secondary: 'bg-datafacz-gray-800 text-datafacz-gray-50 hover:bg-datafacz-gray-700 active:scale-95',
    tertiary: 'bg-transparent border border-datafacz-gray-700 text-datafacz-gray-50 hover:bg-datafacz-gray-900 hover:border-datafacz-orange active:scale-95',
    danger: 'bg-datafacz-red/20 text-datafacz-red border border-datafacz-red/30 hover:bg-datafacz-red/30 active:scale-95',
    ghost: 'text-datafacz-gray-50 hover:bg-datafacz-gray-800/50 active:scale-95',
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm rounded-md',
    base: 'px-4 py-2.5 text-base rounded-md',
    lg: 'px-6 py-3 text-base rounded-md',
  };

  return (
    <button
      className={clsx(
        baseStyles,
        variantStyles[variant],
        sizeStyles[size],
        fullWidth && 'w-full',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          {children}
        </>
      ) : (
        <>
          {Icon && <Icon size={18} />}
          {children}
        </>
      )}
    </button>
  );
};
