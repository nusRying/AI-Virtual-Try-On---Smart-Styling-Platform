import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/MerchantDashboard.css';

interface Garment {
  id: string;
  name: string;
  category: string;
  price: number;
  try_on_count: number;
  thumbnail_url: string;
}

const API_BASE_URL = 'http://localhost:8000/api/v1';

const MerchantDashboard: React.FC = () => {
  const [garments, setGarments] = useState<Garment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Form state
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [tags, setTags] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const fetchCatalog = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/catalog`, {
        params: { limit: 100 } // Fetch all for dashboard
      });
      setGarments(response.data.garments);
    } catch (error) {
      console.error('Error fetching catalog:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCatalog();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!image || !name || !price) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('name', name);
    formData.append('price', price);
    formData.append('tags', tags);
    formData.append('image', image);

    try {
      await axios.post(`${API_BASE_URL}/catalog`, formData);
      alert('Garment added successfully!');
      setName('');
      setPrice('');
      setTags('');
      setImage(null);
      fetchCatalog(); // Refresh list
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to add garment.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;
    
    try {
      await axios.delete(`${API_BASE_URL}/catalog/${id}`);
      fetchCatalog();
    } catch (error) {
      console.error('Delete error:', error);
    }
  };

  return (
    <div className="merchant-dashboard">
      <div className="dashboard-grid">
        <section className="inventory-section">
          <h2>Inventory & Analytics</h2>
          {isLoading ? <p>Loading...</p> : (
            <table className="inventory-table">
              <thead>
                <tr>
                  <th>Image</th>
                  <th>Name</th>
                  <th>Price</th>
                  <th>Total Try-Ons</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {garments.map(g => (
                  <tr key={g.id}>
                    <td><img src={`http://localhost:8000${g.thumbnail_url}`} className="table-thumb" alt="" /></td>
                    <td>{g.name}</td>
                    <td>${g.price.toFixed(2)}</td>
                    <td className="metrics-cell">{g.try_on_count}</td>
                    <td>
                      <button onClick={() => handleDelete(g.id)} className="delete-btn">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        <section className="add-item-section">
          <h2>Add New Garment</h2>
          <form onSubmit={handleUpload} className="upload-form">
            <div className="form-group">
              <label>Garment Name</label>
              <input type="text" value={name} onChange={e => setName(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Price ($)</label>
              <input type="number" step="0.01" value={price} onChange={e => setPrice(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Tags (comma separated)</label>
              <input type="text" placeholder="white, cotton, formal" value={tags} onChange={e => setTags(e.target.value)} />
            </div>
            <div className="form-group">
              <label>Garment Image</label>
              <input type="file" accept="image/*" onChange={e => setImage(e.target.files?.[0] || null)} required />
            </div>
            <button type="submit" className="primary-button" disabled={isUploading}>
              {isUploading ? 'Uploading...' : 'Add to Catalog'}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
};

export default MerchantDashboard;
