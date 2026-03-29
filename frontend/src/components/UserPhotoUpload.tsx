import React, { useState } from 'react';
import type { ChangeEvent } from 'react';
import '../styles/UserPhotoUpload.css';

interface UserPhotoUploadProps {
  onPhotoSelect: (file: File) => void;
}

const UserPhotoUpload: React.FC<UserPhotoUploadProps> = ({ onPhotoSelect }) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setError(null);

    if (!file) return;

    // 1. Validation: File Type
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      setError('Please upload a JPG or PNG image.');
      return;
    }

    // 2. Validation: File Size (< 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB.');
      return;
    }

    // 3. Validation: Aspect Ratio (Portrait)
    const img = new Image();
    img.src = URL.createObjectURL(file);
    img.onload = () => {
      if (img.width > img.height) {
        setError('Please upload a portrait image (height > width) for better results.');
      }
      setPreview(img.src);
      onPhotoSelect(file);
    };
  };

  return (
    <div className="upload-container">
      <h3>1. Upload Your Photo</h3>
      <p className="upload-hint">Upload a clear portrait photo of yourself.</p>
      
      <div className="upload-box">
        <input 
          type="file" 
          id="photo-upload" 
          accept="image/jpeg,image/png" 
          onChange={handleFileChange} 
          className="file-input"
        />
        <label htmlFor="photo-upload" className="file-label">
          {preview ? (
            <img src={preview} alt="Preview" className="preview-image" />
          ) : (
            <div className="upload-placeholder">
              <span>+</span>
              <p>Click to upload portrait</p>
            </div>
          )}
        </label>
      </div>

      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default UserPhotoUpload;
