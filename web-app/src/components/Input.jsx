import React from 'react';
import clsx from 'clsx';

export const Input = ({
  label,
  error,
  helpText,
  icon: Icon,
  className,
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-datafacz-gray-50 mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <Icon
            size={18}
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-datafacz-gray-500 pointer-events-none"
          />
        )}
        <input
          className={clsx(
            'w-full px-4 py-2.5 bg-datafacz-gray-800 border rounded-md text-datafacz-gray-50 placeholder-datafacz-gray-500 transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-datafacz-orange focus:border-transparent',
            error && 'border-datafacz-red focus:ring-datafacz-red',
            !error && 'border-datafacz-gray-700',
            Icon && 'pl-10',
            className
          )}
          {...props}
        />
      </div>
      {error && (
        <p className="mt-2 text-sm text-datafacz-red">{error}</p>
      )}
      {helpText && !error && (
        <p className="mt-2 text-sm text-datafacz-gray-400">{helpText}</p>
      )}
    </div>
  );
};
