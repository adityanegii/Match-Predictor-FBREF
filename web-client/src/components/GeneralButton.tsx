import React from 'react';

interface GeneralButtonProps {
    primary: boolean;
    size: 's' | 'm' | 'l';
    children: React.ReactNode;
    buttonClick: () => void;
}

export default function GeneralButton({ primary, size, children, buttonClick }: GeneralButtonProps) {
    // Define Tailwind classes for different sizes
    const sizeClasses = {
        s: 'px-2 py-1 text-sm',
        m: 'px-4 py-2 text-base',
        l: 'px-6 py-3 text-lg',
    };

    // Base classes, including conditional classes for primary or secondary styling
    const baseClasses = `
        ${primary ? 'bg-blue-950 text-white border-gray-white' : 'bg-black text-white border-white'}
        border-2 rounded-lg cursor-pointer
    `;

    return (
        <button
            className={`${baseClasses} ${sizeClasses[size]}`}
            onClick={buttonClick}
        >
            {children}	
        </button>
    );
}