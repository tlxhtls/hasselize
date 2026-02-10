'use client'

import { useState } from 'react'
import { ImageUploader } from '@/components/ImageUploader'
import { BeforeAfterSlider } from '@/components/BeforeAfterSlider'
import { transformImage } from '@/lib/api/transform'
import type { CameraStyle, ResolutionMode, TransformResponse } from '@/lib/api/types'
import { downloadImage } from '@/lib/storage/image-utils'

export default function TransformPage() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [selectedStyle, setSelectedStyle] = useState<CameraStyle>('hasselblad')
  const [resolution, setResolution] = useState<ResolutionMode>('preview')
  const [isTransforming, setIsTransforming] = useState(false)
  const [result, setResult] = useState<TransformResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const cameraStyles = [
    { slug: 'hasselblad' as CameraStyle, name: 'Hasselblad X2D', description: 'Medium format depth', isPremium: false },
    { slug: 'leica_m' as CameraStyle, name: 'Leica M Series', description: 'High contrast street', isPremium: true },
    { slug: 'zeiss' as CameraStyle, name: 'Zeiss Lenses', description: 'Exceptional sharpness', isPremium: true },
    { slug: 'fujifilm_gfx' as CameraStyle, name: 'Fujifilm GFX', description: 'Film simulations', isPremium: true },
  ]

  const resolutions = [
    { mode: 'preview' as ResolutionMode, name: 'Preview', size: '256×256', description: 'Fastest' },
    { mode: 'standard' as ResolutionMode, name: 'Standard', size: '512×512', description: 'Balanced' },
    { mode: 'high' as ResolutionMode, name: 'High Quality', size: '1024×1024', description: 'Best quality' },
  ]

  const handleImageSelect = (file: File) => {
    setSelectedImage(file)
    setResult(null)
    setError(null)

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleTransform = async () => {
    if (!selectedImage) return

    setIsTransforming(true)
    setError(null)

    try {
      const transformResult = await transformImage(
        selectedImage,
        selectedStyle,
        resolution
      )
      setResult(transformResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Transformation failed')
    } finally {
      setIsTransforming(false)
    }
  }

  const handleDownload = () => {
    if (result) {
      downloadImage(result.transformed_image_url, `hasselized-${result.id}.jpg`)
    }
  }

  return (
    <div className="min-h-screen pb-12">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <a href="/" className="text-xl font-bold text-gray-900">
            Hasselize
          </a>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Transform Your Photo</h1>

        {/* Step 1: Upload */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            1. Upload Your Photo
          </h2>
          <ImageUploader
            onImageSelect={handleImageSelect}
            onError={setError}
            className="w-full"
          />
        </div>

        {/* Preview */}
        {imagePreview && !result && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Preview</h2>
            <div className="bg-gray-100 rounded-lg overflow-hidden">
              <img
                src={imagePreview}
                alt="Preview"
                className="w-full h-auto max-h-96 object-contain"
              />
            </div>
          </div>
        )}

        {/* Step 2: Select Style */}
        {selectedImage && !result && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              2. Choose Camera Style
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {cameraStyles.map((style) => (
                <button
                  key={style.slug}
                  onClick={() => setSelectedStyle(style.slug)}
                  disabled={style.isPremium}
                  className={`camera-style-card p-4 rounded-lg border-2 text-left transition-all ${
                    selectedStyle === style.slug
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  } ${style.isPremium ? 'opacity-60' : ''}`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-gray-900">{style.name}</span>
                    {style.isPremium && (
                      <span className="text-xs font-medium text-amber-600 bg-amber-50 px-2 py-0.5 rounded">
                        Premium
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{style.description}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Select Resolution */}
        {selectedImage && !result && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              3. Output Quality
            </h2>
            <div className="grid grid-cols-3 gap-4">
              {resolutions.map((res) => (
                <button
                  key={res.mode}
                  onClick={() => setResolution(res.mode)}
                  className={`p-4 rounded-lg border-2 text-center transition-all ${
                    resolution === res.mode
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-semibold text-gray-900 mb-1">{res.name}</div>
                  <div className="text-sm text-gray-600 mb-1">{res.size}</div>
                  <div className="text-xs text-gray-500">{res.description}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Transform Button */}
        {selectedImage && !result && (
          <div className="mb-8">
            <button
              onClick={handleTransform}
              disabled={isTransforming}
              className="w-full px-6 py-4 text-lg font-semibold text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isTransforming ? (
                <span className="flex items-center justify-center gap-3">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Transforming...
                </span>
              ) : (
                'Transform Photo'
              )}
            </button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Result */}
        {result && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Transformation Complete
            </h2>

            {/* Before/After Slider */}
            <div className="mb-6">
              <BeforeAfterSlider
                beforeImage={result.original_image_url}
                afterImage={result.transformed_image_url}
                className="w-full"
              />
            </div>

            {/* Metadata */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Style</span>
                  <p className="font-medium text-gray-900">{result.style}</p>
                </div>
                <div>
                  <span className="text-gray-500">Resolution</span>
                  <p className="font-medium text-gray-900">{result.resolution}</p>
                </div>
                <div>
                  <span className="text-gray-500">Processing Time</span>
                  <p className="font-medium text-gray-900">{result.processing_time_ms}ms</p>
                </div>
                <div>
                  <span className="text-gray-500">Model</span>
                  <p className="font-medium text-gray-900">{result.model_used}</p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={handleDownload}
                className="flex-1 px-6 py-3 text-center font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
              >
                Download
              </button>
              <button
                onClick={() => {
                  setResult(null)
                  setSelectedImage(null)
                  setImagePreview(null)
                }}
                className="px-6 py-3 font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                New Photo
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
