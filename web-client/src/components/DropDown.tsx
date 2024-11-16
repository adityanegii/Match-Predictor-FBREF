import { useState } from 'react';
import { League, Model } from '@/utils/types';
import { SVGs } from '@/utils/SVG';
import GeneralIcon from './GeneralIcon';

interface DropDownProps {
    onSelect: (item: League | Model) => void;
    items: (League | Model)[];
    text: string;
}

const DropDown: React.FC<DropDownProps> = ({ onSelect, items, text }) => {
    const [isHovered, setIsHovered] = useState(false);
    const [selectedItem, setSelected] = useState<string>(text);

    const handleMouseEnter = () => setIsHovered(true);
    const handleMouseLeave = () => setIsHovered(false);

    const handleSelect = (item: League | Model) => {
        onSelect(item);
        setSelected(item.name);
    }

    return (
        <div 
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            className="relative inline-block text-center"
        >
            <button className="w-64 flex items-center justify-between px-4 py-2 border border-gray-300 rounded hover:bg-blue-900 hover:text-white">
                <div className="flex-grow text-center">{selectedItem}</div>
                <div>
                    {isHovered ? (<GeneralIcon alt="arrowUp">{SVGs.arrowUp}</GeneralIcon>) 
                    : (<GeneralIcon alt="arrowDown">{SVGs.arrowDown}</GeneralIcon>)
                    }
                </div>
            </button>

            {isHovered && (
                <div className="absolute w-64 border border-gray-300 rounded shadow-lg z-10">
                    {items.map((item) => (
                        <span
                            key={item.id}
                            onClick={() => (handleSelect(item))}
                            className="w-full block px-4 py-2 hover:bg-blue-900 hover:text-white cursor-pointer"
                        >
                            {item.name}
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
};

export default DropDown;
