import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BACKEND_ORIGIN, API_BASE_URL } from '../config';
import '../styles/MerchantDashboard.css';

interface Garment {
  id: string;
  name: string;
  category: string;
  price: number;
  try_on_count: number;
  thumbnail_url: string;
}

interface SystemStatus {
  models: {
    sam2: boolean;
    idm_vton: boolean;
  };
  queue: {
    mode: string;
    connected: boolean;
  };
  device: string;
}

const MerchantDashboard: React.FC = () => {
  const [inventory, setInventory] = useState<Garment[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  
  // Form state
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [category, setCategory] = useState('Shirts');
  const [tags, setTags] = useState('');
  const [image, setImage] = useState<File | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [invRes, statusRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/catalog?limit=100`),
        axios.get(`${API_BASE_URL}/system/status`)
      ]);
      setInventory(invRes.data.garments);
      setSystemStatus(statusRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!image || !name || !price) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('name', name);
    formData.append('price', price);
    formData.append('category', category);
    formData.append('tags', tags);
    formData.append('image', image);

    try {
      await axios.post(`${API_BASE_URL}/catalog`, formData);
      // Reset form
      setName('');
      setPrice('');
      setTags('');
      setImage(null);
      // Refresh list
      fetchData();
    } catch (error) {
      console.error('Error uploading garment:', error);
      alert('Failed to upload garment.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;
    
    try {
      await axios.delete(`${API_BASE_URL}/catalog/${id}`);
      fetchData();
    } catch (error) {
      console.error('Error deleting item:', error);
    }
  };

  const totalTryOns = inventory.reduce((sum, item) => sum + item.try_on_count, 0);

  const getImageUrl = (url: string) => {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    const normalizedUrl = url.startsWith('/') ? url : `/${url}`;
    return `${BACKEND_ORIGIN}${normalizedUrl}`;
  };

  return (
    <div className="merchant-dashboard">
      <header className="dashboard-header">
        <h1>Merchant Control Center</h1>
        <div className="header-stats">
          <div className="stat-card">
            <span className="stat-label">Total Inventory</span>
            <span className="stat-value">{inventory.length}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Platform Engagement</span>
            <span className="stat-value">{totalTryOns} <small>Try-ons</small></span>
          </div>
        </div>
      </header>

      {isLoading ? (
        <div className="dashboard-loader">Loading intelligence...</div>
      ) : (
        <div className="dashboard-grid">
          <section className="inventory-section">
            <h2>Inventory Management</h2>
            <div className="inventory-table-container">
              <table className="inventory-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Name</th>
                    <th>Category</th>
                    <th>Price</th>
                    <th>Try-Ons</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {inventory.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <img 
                          src={getImageUrl(item.thumbnail_url)} 
                          alt={item.name} 
                          className="table-thumb" 
                        />
                      </td>
                      <td className="item-name-cell">{item.name}</td>
                      <td>{item.category}</td>
                      <td>${item.price.toFixed(2)}</td>
                      <td className="metrics-cell">{item.try_on_count}</td>
                      <td>
                        <button 
                          className="delete-btn"
                          onClick={() => handleDelete(item.id)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="add-item-section">
            <h2>Add New Garment</h2>
            <form className="upload-form" onSubmit={handleUpload}>
              <div className="form-group">
                <label>Product Name</label>
                <input 
                  type="text" 
                  value={name} 
                  onChange={(e) => setName(e.target.value)} 
                  placeholder="e.g. Classic Silk Shirt"
                  required
                />
              </div>
              <div className="form-group">
                <label>Price ($)</label>
                <input 
                  type="number" 
                  value={price} 
                  onChange={(e) => setPrice(e.target.value)} 
                  placeholder="99.00"
                  step="0.01"
                  required
                />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select value={category} onChange={(e) => setCategory(e.target.value)}>
                  <option value="Shirts">Shirts</option>
                  <option value="Pants">Pants</option>
                  <option value="Shoes">Shoes</option>
                  <option value="Accessories">Accessories</option>
                </select>
              </div>
              <div className="form-group">
                <label>Tags (comma separated)</label>
                <input 
                  type="text" 
                  value={tags} 
                  onChange={(e) => setTags(e.target.value)} 
                  placeholder="formal, blue, slim-fit"
                />
              </div>
              <div className="form-group">
                <label>Product Image</label>
                <input 
                  type="file" 
                  onChange={(e) => setImage(e.target.files ? e.target.files[0] : null)}
                  accept="image/*"
                  required
                />
              </div>
              <button 
                type="submit" 
                className="primary-button"
                disabled={isUploading}
              >
                {isUploading ? 'Uploading...' : 'Publish to Catalog'}
              </button>
            </form>

            {systemStatus && (
              <div className="system-health-section">
                <h3>System Infrastructure</h3>
                <div className="system-card">
                  <h4>VTO Engine</h4>
                  <div className="model-status-list">
                    <div className="model-status-item">
                      <span>SAM 2 (Segmentation)</span>
                      <span className={`indicator ${systemStatus.models.sam2 ? 'ready' : 'missing'}`}>
                        {systemStatus.models.sam2 ? 'READY' : 'OFFLINE'}
                      </span>
                    </div>
                    <div className="model-status-item">
                      <span>SDXL (Inference)</span>
                      <span className={`indicator ${systemStatus.models.idm_vton ? 'ready' : 'missing'}`}>
                        {systemStatus.models.idm_vton ? 'READY' : 'OFFLINE'}
                      </span>
                    </div>
                  </div>
                  <div className="system-meta">
                    <span className="status-hint">Processing Device: </span>
                    <span className="device-tag">{systemStatus.device}</span>
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
};

export default MerchantDashboard;
