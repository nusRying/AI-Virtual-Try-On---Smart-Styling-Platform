import { useState, useEffect } from 'react'
import axios from 'axios'
import UserPhotoUpload from './components/UserPhotoUpload'
import ProductCatalog, { Garment } from './components/ProductCatalog'
import './App.css'

const API_BASE_URL = 'http://localhost:8000/api/v1'

function App() {
  const [selectedPhoto, setSelectedPhoto] = useState<File | null>(null)
  const [selectedGarment, setSelectedGarment] = useState<Garment | null>(null)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [status, setStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle')
  const [resultImage, setResultImage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handlePhotoSelect = (file: File) => {
    setSelectedPhoto(file)
    setStatus('idle')
    setResultImage(null)
  }

  const handleGarmentSelect = (garment: Garment) => {
    setSelectedGarment(garment)
    
    // Auto-trigger try-on if photo is already uploaded
    if (selectedPhoto && status !== 'processing') {
      triggerTryOn(selectedPhoto, garment.id)
    }
  }

  const triggerTryOn = async (photo: File, garmentId: string) => {
    setStatus('processing')
    setErrorMessage(null)
    setResultImage(null)

    try {
      const formData = new FormData()
      formData.append('user_image', photo)
      formData.append('garment_id', garmentId)

      const response = await axios.post(`${API_BASE_URL}/try-on`, formData)
      setTaskId(response.data.task_id)
    } catch (err: any) {
      console.error('Submission error:', err)
      setStatus('error')
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to submit task.')
    }
  }

  // Manual trigger handle (for UI consistency if needed)
  const handleTryOnManual = () => {
    if (selectedPhoto && selectedGarment) {
      triggerTryOn(selectedPhoto, selectedGarment.id)
    }
  }

  // Polling logic
  useEffect(() => {
    let interval: number | undefined

    if (taskId && status === 'processing') {
      interval = window.setInterval(async () => {
        try {
          const response = await axios.get(`${API_BASE_URL}/tasks/${taskId}`)
          const currentStatus = response.data.status

          if (currentStatus === 'SUCCESS') {
            const resultData = response.data.result
            if (resultData.status === 'success') {
              const filename = resultData.output_path.split(/[\\/]/).pop()
              setResultImage(`${API_BASE_URL}/results/${filename}`)
              setStatus('success')
              clearInterval(interval)
            } else {
              throw new Error(resultData.message || 'Processing failed on server')
            }
          } else if (currentStatus === 'FAILURE') {
            throw new Error(response.data.error || 'Task execution failed')
          }
        } catch (err: any) {
          console.error('Polling error:', err)
          setStatus('error')
          setErrorMessage(err.message || 'Failed to get task status.')
          clearInterval(interval)
        }
      }, 2000)
    }

    return () => clearInterval(interval)
  }, [taskId, status])

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AI Virtual Try-On</h1>
        <p>Smart Styling Platform</p>
      </header>

      <main className="app-main">
        <div className="workspace">
          <section className="setup-panel">
            <UserPhotoUpload onPhotoSelect={handlePhotoSelect} />
            
            <ProductCatalog 
              onGarmentSelect={handleGarmentSelect} 
              selectedGarmentId={selectedGarment?.id || null} 
            />

            {status === 'error' && (
              <div className="error-box">
                <p>Error: {errorMessage}</p>
                <button onClick={handleTryOnManual} className="retry-btn">Retry Try-On</button>
              </div>
            )}
          </section>

          <section className="result-panel">
            <h3>3. Try-On Result</h3>
            <div className="result-display">
              {status === 'processing' && (
                <div className="loader-container">
                  <div className="loader"></div>
                  <p>Our AI is dressing you up...</p>
                </div>
              )}
              
              {status === 'success' && resultImage && (
                <div className="result-image-container">
                  <img src={resultImage} alt="Try-On Result" className="final-result" />
                  <a href={resultImage} download="tryon_result.png" className="download-link">Download Result</a>
                </div>
              )}

              {status === 'idle' && !resultImage && (
                <div className="result-placeholder">
                  {selectedPhoto ? (
                    <p>Select a garment to see the magic!</p>
                  ) : (
                    <p>Please upload a portrait photo first.</p>
                  )}
                </div>
              )}
            </div>
          </section>
        </div>
      </main>

      <footer className="app-footer">
        <p>&copy; 2026 AI Virtual Try-On Platform</p>
      </footer>
    </div>
  )
}

export default App
