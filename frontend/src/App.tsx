import { useEffect, useState } from 'react'
import axios from 'axios'
import UserPhotoUpload from './components/UserPhotoUpload'
import ProductCatalog from './components/ProductCatalog'
import type { Garment } from './components/ProductCatalog'
import StylingRecommendations from './components/StylingRecommendations'
import type { RecommendedItem } from './components/StylingRecommendations'
import MerchantDashboard from './components/MerchantDashboard'
import { BACKEND_ORIGIN, API_BASE_URL } from './config'
import './App.css'

interface RecommendationsResponse {
  recommendations: RecommendedItem[]
  styling_tip: string
}

interface TryOnSubmissionResponse {
  task_id: string
  status?: string
  result?: TryOnTaskResult
}

interface TryOnTaskResult {
  status: 'success' | 'error'
  output_path?: string
  result_url?: string
  message?: string
}

interface TryOnTaskStatusResponse {
  status: string
  result: TryOnTaskResult | null
  error?: string
}

interface ApiErrorResponse {
  detail?: string
  error?: string
  message?: string
}

const getErrorMessage = (error: unknown, fallback: string) => {
  if (axios.isAxiosError<ApiErrorResponse>(error)) {
    return error.response?.data?.detail
      ?? error.response?.data?.error
      ?? error.response?.data?.message
      ?? error.message
      ?? fallback
  }

  if (error instanceof Error) {
    return error.message
  }

  return fallback
}

function App() {
  const [viewMode, setViewMode] = useState<'user' | 'merchant'>('user')
  const [selectedPhoto, setSelectedPhoto] = useState<File | null>(null)
  const [selectedGarment, setSelectedGarment] = useState<Garment | null>(null)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [status, setStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle')
  const [resultImage, setResultImage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  
  // Recommendations state
  const [recommendations, setRecommendations] = useState<RecommendedItem[]>([])
  const [stylingTip, setStylingTip] = useState<string>('')

  const handlePhotoSelect = (file: File) => {
    setSelectedPhoto(file)
    setStatus('idle')
    setResultImage(null)
  }

  const handleGarmentSelect = (garment: Garment) => {
    setSelectedGarment(garment)
    fetchRecommendations(garment.id)
    
    // Auto-trigger try-on if photo is already uploaded
    if (selectedPhoto && status !== 'processing') {
      triggerTryOn(selectedPhoto, garment.id)
    }
  }

  const fetchRecommendations = async (garmentId: string) => {
    try {
      const response = await axios.get<RecommendationsResponse>(`${API_BASE_URL}/recommendations/${garmentId}`)
      setRecommendations(response.data.recommendations)
      setStylingTip(response.data.styling_tip)
    } catch (err) {
      console.error('Error fetching recommendations:', err)
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

      const response = await axios.post<TryOnSubmissionResponse>(`${API_BASE_URL}/try-on`, formData)
      
      // Check for immediate synchronous result (Mock Mode)
      if (response.data.status === 'SUCCESS' && response.data.result) {
        const resultData = response.data.result
        if (resultData.status === 'success') {
          if (resultData.result_url) {
            const finalUrl = resultData.result_url.startsWith('http') 
              ? resultData.result_url 
              : `${BACKEND_ORIGIN}${resultData.result_url}`
            setResultImage(finalUrl)
          } else if (resultData.output_path) {
            const filename = resultData.output_path.split(/[\\/]/).pop()
            setResultImage(`${API_BASE_URL}/results/${filename}`)
          }
          setStatus('success')
          return // Skip polling
        } else {
          throw new Error(resultData.message || 'Processing failed')
        }
      }

      setTaskId(response.data.task_id)
    } catch (err) {
      console.error('Submission error:', err)
      setStatus('error')
      setErrorMessage(getErrorMessage(err, 'Failed to submit task.'))
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
          const response = await axios.get<TryOnTaskStatusResponse>(`${API_BASE_URL}/tasks/${taskId}`)
          const currentStatus = response.data.status

          if (currentStatus === 'SUCCESS') {
            const resultData = response.data.result
            if (resultData?.status === 'success') {
              // Prefer result_url if provided by backend
              if (resultData.result_url) {
                const finalUrl = resultData.result_url.startsWith('http') 
                  ? resultData.result_url 
                  : `${BACKEND_ORIGIN}${resultData.result_url}`
                setResultImage(finalUrl)
              } else if (resultData.output_path) {
                // Fallback for older task formats
                const filename = resultData.output_path.split(/[\\/]/).pop()
                setResultImage(`${API_BASE_URL}/results/${filename}`)
              }
              
              setStatus('success')
              clearInterval(interval)
            } else {
              throw new Error(resultData?.message || 'Processing failed on server')
            }
          } else if (currentStatus === 'FAILURE') {
            throw new Error(response.data.error || 'Task failed')
          }
        } catch (err) {
          console.error('Polling error:', err)
          setStatus('error')
          setErrorMessage(getErrorMessage(err, 'Error while processing your request.'))
          clearInterval(interval)
        }
      }, 2000)
    }

    return () => clearInterval(interval)
  }, [taskId, status])

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <h1>Styling <span>AI</span></h1>
          </div>
          <div className="view-toggle">
            <button 
              className={viewMode === 'user' ? 'active' : ''} 
              onClick={() => setViewMode('user')}
            >
              User Studio
            </button>
            <button 
              className={viewMode === 'merchant' ? 'active' : ''} 
              onClick={() => setViewMode('merchant')}
            >
              Merchant Portal
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">
        {viewMode === 'merchant' ? (
          <MerchantDashboard />
        ) : (
          <div className="workspace">
            <aside className="setup-panel">
              <UserPhotoUpload onPhotoSelect={handlePhotoSelect} />
              
              {selectedGarment && (
                <StylingRecommendations 
                  recommendations={recommendations} 
                  stylingTip={stylingTip} 
                />
              )}
            </aside>

            <section className="catalog-panel">
              <ProductCatalog 
                onGarmentSelect={handleGarmentSelect} 
                selectedGarmentId={selectedGarment?.id || null} 
              />
            </section>

            <section className="result-panel">
              <h3><span>✨</span> Try-On Studio</h3>
              <div className="result-display">
                {status === 'processing' && (
                  <div className="loader-container">
                    <span className="loader"></span>
                    <p>AI is dressing you up...</p>
                  </div>
                )}
                
                {status === 'success' && resultImage && (
                  <div className="result-image-container">
                    <img src={resultImage} alt="Try-On Result" className="final-result" />
                    <a href={resultImage} download="tryon_result.png" className="download-link">Download Result</a>
                  </div>
                )}

                {status === 'error' && (
                  <div className="error-box">
                    <p>Something went wrong: {errorMessage}</p>
                    <button onClick={handleTryOnManual} className="retry-btn">Try Again</button>
                  </div>
                )}

                {status === 'idle' && !resultImage && (
                  <div className="result-placeholder">
                    {!selectedPhoto ? (
                      <p>Upload a portrait to begin your styling session</p>
                    ) : !selectedGarment ? (
                      <p>Choose a garment to see the virtual try-on</p>
                    ) : (
                      <p>Ready to try on the {selectedGarment.name}!</p>
                    )}
                  </div>
                )}
              </div>
            </section>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; 2026 AI Virtual Try-On Platform • Built for the Future of Fashion</p>
      </footer>
    </div>
  )
}

export default App
