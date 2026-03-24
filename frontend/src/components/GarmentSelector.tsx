import React, { useState } from 'react';
import '../styles/GarmentSelector.css';

interface Garment {
  id: string;
  name: string;
  thumbnail: string; // URL to thumbnail
  fullImage: string; // URL to full image for processing
}

interface GarmentSelectorProps {
  onGarmentSelect: (garment: Garment) => void;
}

const SAMPLE_GARMENTS: Garment[] = [
  { id: 'shirt-1', name: 'Classic White Shirt', thumbnail: 'https://via.placeholder.com/150x200?text=White+Shirt', fullImage: 'https://via.placeholder.com/600x800?text=White+Shirt' },
  { id: 'shirt-2', name: 'Blue Denim Shirt', thumbnail: 'https://via.placeholder.com/150x200?text=Blue+Denim', fullImage: 'https://via.placeholder.com/600x800?text=Blue+Denim' },
  { id: 'shirt-3', name: 'Black Polo', thumbnail: 'https://via.placeholder.com/150x200?text=Black+Polo', fullImage: 'https://via.placeholder.com/600x800?text=Black+Polo' },
];

const GarmentSelector: React.FC<GarmentSelectorProps> = ({ onGarmentSelect }) => {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const handleSelect = (garment: Garment) => {
    setSelectedId(garment.id);
    onGarmentSelect(garment);
  };

  return (
    <div className="garment-container">
      <h3>2. Choose a Garment</h3>
      <p className="garment-hint">Select a shirt to try on.</p>
      
      <div className="garment-grid">
        {SAMPLE_GARMENTS.map((garment) => (
          <div 
            key={garment.id} 
            className={`garment-card ${selectedId === garment.id ? 'selected' : ''}`}
            onClick={() => handleSelect(garment)}
          >
            <img src={garment.thumbnail} alt={garment.name} />
            <p>{garment.name}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GarmentSelector;
export type { Garment };
