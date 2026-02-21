'use client'
import { useRef, useState } from 'react'

export default function ImageUploader({ onImageSelected }) {
  const [preview, setPreview] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)

  const handleFile = (file) => {
    if (!file) return

    if (!file.type.startsWith('image/')) {
      alert('Veuillez sélectionner une image (JPG, PNG...)')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      alert("L'image ne doit pas dépasser 5MB")
      return
    }

    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result)
    }
    reader.readAsDataURL(file)

    onImageSelected(file)
  }

  const handleInputChange = (e) => {
    handleFile(e.target.files[0])
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const resetImage = () => {
    setPreview(null)
    onImageSelected(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="w-full">
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        📷 Photo de la lésion
      </label>

      {!preview ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => inputRef.current.click()}
          className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-colors
            ${
              isDragging
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50'
            }`}
        >
          <div className="text-5xl mb-3">🖼️</div>
          <p className="text-gray-600 font-medium">
            Glissez une image ici ou{' '}
            <span className="text-blue-600 underline">cliquez pour choisir</span>
          </p>
          <p className="text-sm text-gray-400 mt-1">JPG, PNG – Max 5MB</p>
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            onChange={handleInputChange}
            className="hidden"
          />
        </div>
      ) : (
        <div className="relative rounded-2xl overflow-hidden border border-gray-200 shadow">
          <img src={preview} alt="Aperçu lésion" className="w-full max-h-72 object-cover" />
          <button
            onClick={resetImage}
            className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white text-xs px-3 py-1 rounded-full transition-colors"
          >
            ✕ Supprimer
          </button>
          <div className="absolute bottom-0 left-0 right-0 bg-green-500 text-white text-xs text-center py-1">
            ✅ Image sélectionnée
          </div>
        </div>
      )}
    </div>
  )
}