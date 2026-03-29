import React from 'react';
import { BACKEND_ORIGIN } from '../config';
import '../styles/StylingRecommendations.css';

interface RecommendedItem {
  id: string;
  name: string;
  category: string;
  price: number;
  thumbnail_url: string;
}

interface StylingRecommendationsProps {
  recommendations: RecommendedItem[];
  stylingTip: string;
}

const StylingRecommendations: React.FC<StylingRecommendationsProps> = ({ recommendations, stylingTip }) => {
  if (recommendations.length === 0) {
    return (
      <div className="recommendations-container empty">
        <h3>Complete the Look</h3>
        <p className="empty-state-text">Select a garment from the catalog to see matching styling advice.</p>
      </div>
    );
  }

  const getImageUrl = (url: string) => {
    if (url.startsWith('http')) return url;
    return `${BACKEND_ORIGIN}${url}`;
  };

  return (
    <div className="recommendations-container">
      <h3>Complete the Look</h3>
      <div className="styling-tip-box">
        <p className="styling-tip-text">
          <span className="ai-badge">AI Stylist</span> {stylingTip}
        </p>
      </div>
      
      <div className="matched-items-grid">
        {recommendations.map((item) => (
          <div key={item.id} className="matched-item-card">
            <img src={getImageUrl(item.thumbnail_url)} alt={item.name} />
            <div className="matched-item-info">
              <p className="matched-item-name">{item.name}</p>
              <p className="matched-item-category">{item.category}</p>
              <p className="matched-item-price">${item.price.toFixed(2)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StylingRecommendations;
export type { RecommendedItem };
