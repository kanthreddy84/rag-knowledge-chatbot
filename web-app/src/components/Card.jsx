import React from 'react';
import clsx from 'clsx';

export const Card = ({
  children,
  className,
  interactive = false,
  ...props
}) => {
  return (
    <div
      className={clsx(
        'bg-datafacz-gray-900 border border-datafacz-gray-800 rounded-xl transition-all duration-300',
        interactive && 'hover:border-datafacz-gray-700 hover:shadow-lg hover:translate-y-[-5px] cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className, ...props }) => (
  <div
    className={clsx('px-6 py-4 border-b border-datafacz-gray-800', className)}
    {...props}
  >
    {children}
  </div>
);

export const CardBody = ({ children, className, ...props }) => (
  <div className={clsx('px-6 py-4', className)} {...props}>
    {children}
  </div>
);

export const CardFooter = ({ children, className, ...props }) => (
  <div
    className={clsx('px-6 py-4 border-t border-datafacz-gray-800 flex gap-3', className)}
    {...props}
  >
    {children}
  </div>
);
