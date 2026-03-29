import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BACKEND_ORIGIN, API_BASE_URL } from '../config';
import '../styles/ProductCatalog.css';

interface Garment {
  id: string;
  name: string;
  category: string;
  price: number;
  description: string;
  thumbnail_url: string;
  full_image_url: string;
  tags: string[];
}

interface ProductCatalogProps {
  onGarmentSelect: (garment: Garment) => void;
  selectedGarmentId: string | null;
}

const ProductCatalog: React.FC<ProductCatalogProps> = ({ onGarmentSelect, selectedGarmentId }) => {
  const [garments, setGarments] = useState<Garment[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSemantic, setIsSemantic] = useState(false);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const limit = 6;

  useEffect(() => {
    const delayDebounceFn = window.setTimeout(() => {
      const fetchCatalog = async () => {
        setIsLoading(true);
        try {
          const response = await axios.get(`${API_BASE_URL}/catalog`, {
            params: {
              q: searchQuery || undefined,
              page: page,
              limit: limit,
              semantic: isSemantic
            }
          });
          setGarments(response.data.garments);
          setTotalCount(response.data.total_count);
        } catch (error) {
          console.error('Error fetching catalog:', error);
        } finally {
          setIsLoading(false);
        }
      };

      void fetchCatalog();
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery, page, isSemantic]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setPage(1); // Reset to first page on search
  };

  const handlePrevPage = () => {
    setPage((prev) => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    if (page * limit < totalCount) {
      setPage((prev) => prev + 1);
    }
  };

  const totalPages = Math.ceil(totalCount / limit);

  const getImageUrl = (url: string) => {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    // Ensure leading slash for relative paths
    const normalizedUrl = url.startsWith('/') ? url : `/${url}`;
    return `${BACKEND_ORIGIN}${normalizedUrl}`;
  };

  return (
    <div className="catalog-container">
      <div className="catalog-header">
        <div className="catalog-title-row">
          <h3>2. Select a Garment</h3>
          <div className="semantic-toggle-container">
            <span className="toggle-label">AI Discovery</span>
            <label className="switch">
              <input 
                type="checkbox" 
                checked={isSemantic} 
                onChange={(e) => setIsSemantic(e.target.checked)} 
              />
              <span className="slider round"></span>
            </label>
          </div>
        </div>
        <input
          type="text"
          placeholder={isSemantic ? "Search with AI (e.g. stylish office wear)..." : "Search by tags (e.g. white, denim)..."}
          value={searchQuery}
          onChange={handleSearchChange}
          className="search-input"
        />
      </div>

      {isLoading ? (
        <div className="catalog-loader">Loading catalog...</div>
      ) : (
        <>
          <div className="garment-grid">
            {garments.map((garment) => (
              <div 
                key={garment.id} 
                className={`garment-card ${selectedGarmentId === garment.id ? 'selected' : ''}`}
                onClick={() => onGarmentSelect(garment)}
              >
                <div className="image-wrapper">
                  <img src={getImageUrl(garment.thumbnail_url)} alt={garment.name} />
                </div>
                <div className="garment-info">
                  <p className="garment-name">{garment.name}</p>
                  <p className="garment-price">${garment.price.toFixed(2)}</p>
                </div>
              </div>
            ))}
          </div>

          {garments.length === 0 && !isLoading && (
            <p className="no-results">No garments found matching your search.</p>
          )}

          {totalPages > 1 && (
            <div className="pagination">
              <button onClick={handlePrevPage} disabled={page === 1}>Previous</button>
              <span>Page {page} of {totalPages}</span>
              <button onClick={handleNextPage} disabled={page === totalPages}>Next</button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ProductCatalog;
export type { Garment };
