'use client'
import { useState } from 'react'
import Navbar from '@/components/Navbar'
import ImageUploader from '@/components/ImageUploader'
import SymptomsForm from '@/components/SymptomsForm'
import RiskCard from '@/components/RiskCard'

const MOCK_RESULT = {
  score_global: 0.72,
  risk_level: 'élevé',
  recommendation:
    'Les caractéristiques détectées suggèrent une consultation rapide chez un dermatologue. Prenez rendez-vous dans les prochains jours.',
}

export default function Analyse() {
  const [image, setImage] = useState(null)
  const [symptoms, setSymptoms] = useState({
    duration: '',
    pain: 'none',
    itching: false,
    bleeding: false,
    growing: false,
    changing: false,
    description: '',
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const isFormValid = image && symptoms.duration && symptoms.pain

  const handleSubmit = async () => {
    if (!isFormValid) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      await new Promise((resolve) => setTimeout(resolve, 2000))
      setResult(MOCK_RESULT)

      // const formData = new FormData()
      // formData.append('image', image)
      // formData.append('symptoms', JSON.stringify(symptoms))
      // const response = await axios.post('http://localhost:8000/api/analyze', formData)
      // setResult(response.data)
    } catch {
      setError('Une erreur est survenue. Veuillez réessayer.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setImage(null)
    setSymptoms({
      duration: '',
      pain: 'none',
      itching: false,
      bleeding: false,
      growing: false,
      changing: false,
      description: '',
    })
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      <main className="flex-1 max-w-2xl w-full mx-auto px-4 py-10">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          🔬 Analyser une lésion
        </h1>
        <p className="text-gray-500 mb-8">
          Uploadez une photo et décrivez vos symptômes pour obtenir une
          estimation du risque.
        </p>

        <div className="bg-white rounded-2xl shadow p-6 space-y-8">
          <ImageUploader onImageSelected={setImage} />

          <hr className="border-gray-100" />

          <SymptomsForm symptoms={symptoms} onChange={setSymptoms} />

          <button
            onClick={handleSubmit}
            disabled={!isFormValid || loading}
            className={`w-full py-4 rounded-2xl font-semibold text-lg transition-all ${
              isFormValid && !loading
                ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg
                  className="animate-spin h-5 w-5 text-white"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8z"
                  />
                </svg>
                Analyse en cours...
              </span>
            ) : (
              "🔍 Lancer l'analyse"
            )}
          </button>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
              ❌ {error}
            </div>
          )}
        </div>

        {result && (
          <div className="mt-8 space-y-4">
            <RiskCard result={result} />
            <button
              onClick={handleReset}
              className="w-full py-3 rounded-2xl border border-gray-300 text-gray-600 hover:bg-gray-100 transition-colors text-sm"
            >
              🔄 Faire une nouvelle analyse
            </button>
          </div>
        )}
      </main>

      <footer className="text-center py-4 text-sm text-gray-400 border-t">
        © 2025 DermAI – Projet académique
      </footer>
    </div>
  )
}