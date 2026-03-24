import { useState, useEffect } from 'react'
import axios from 'axios'
import UserPhotoUpload from './components/UserPhotoUpload'
import GarmentSelector, { Garment } from './components/GarmentSelector'
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
  }

  const handleTryOn = async () => {
    if (!selectedPhoto || !selectedGarment) return

    setStatus('processing')
    setErrorMessage(null)

    try {
      // 1. Fetch the garment image as a blob (since it's a placeholder URL)
      // In a real app, you might just send the garment ID or a direct URL if backend supports it
      const garmentResp = await axios.get(selectedGarment.fullImage, { responseType: 'blob' })
      const garmentFile = new File([garmentResp.data], "garment.jpg", { type: "image/jpeg" })

      // 2. Submit to API
      const formData = new FormData()
      formData.append('user_image', selectedPhoto)
      formData.append('garment_image', garmentFile)

      const response = await axios.post(`${API_BASE_URL}/try-on`, formData)
      setTaskId(response.data.task_id)
    } catch (err: any) {
      console.error('Submission error:', err)
      setStatus('error')
      setErrorMessage(err.message || 'Failed to submit task.')
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
            
            {selectedPhoto && (
              <div className="garment-selection">
                <GarmentSelector onGarmentSelect={handleGarmentSelect} />
                
                <button 
                  className="primary-button tryon-btn" 
                  disabled={!selectedGarment || status === 'processing'}
                  onClick={handleTryOn}
                >
                  {status === 'processing' ? 'Processing...' : 'Run Virtual Try-On'}
                </button>
              </div>
            )}

            {status === 'error' && (
              <div className="error-box">
                <p>Error: {errorMessage}</p>
              </div>
            )}
          </section>

          <section className="result-panel">
            <h3>3. Result</h3>
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
                  <p>Your result will appear here after processing.</p>
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
