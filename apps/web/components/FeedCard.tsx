'use client'

import { useState, useEffect } from 'react'
import { BeforeAfterSlider } from './BeforeAfterSlider'
import { downloadImage } from '@/lib/storage/image-utils'

interface FeedCardProps {
  id: string
  originalImage: string
  transformedImage: string
  thumbnail?: string
  cameraStyle: string
  userName?: string
  likesCount?: number
  isLiked?: boolean
  onLike?: () => void
  className?: string
}

export function FeedCard({
  id,
  originalImage,
  transformedImage,
  thumbnail,
  cameraStyle,
  userName,
  likesCount = 0,
  isLiked = false,
  onLike,
  className = '',
}: FeedCardProps) {
  const [imageLoaded, setImageLoaded] = useState(false)

  useEffect(() => {
    const img = new Image()
    img.onload = () => setImageLoaded(true)
    img.src = transformedImage
  }, [transformedImage])

  const handleDownload = () => {
    downloadImage(transformedImage, `hasselized-${id}.jpg`)
  }

  return (
    <div className={`bg-white rounded-soft shadow-soft hover:shadow-soft-lg transition-all duration-300 overflow-hidden ${className}`}>
      {/* Before/After Slider */}
      <div className="relative bg-gradient-to-br from-pastel-lavender-50 to-pastel-mint-50">
        {thumbnail && !imageLoaded && (
          <img
            src={thumbnail}
            alt="Loading..."
            className="w-full aspect-square object-cover"
          />
        )}
        <BeforeAfterSlider
          beforeImage={originalImage}
          afterImage={transformedImage}
          beforeLabel="Before"
          afterLabel="After"
          className={`w-full ${imageLoaded ? 'block' : 'hidden'}`}
        />
      </div>

      {/* Card Content */}
      <div className="p-5">
        {/* Camera Style Badge */}
        <div className="flex items-center justify-between mb-4">
          <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-pastel-lavender-100 text-pastel-lavender-700">
            {cameraStyle}
          </span>
          <span className="text-sm text-gray-500 font-medium">
            {userName || 'Anonymous'}
          </span>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between gap-2">
          <button
            onClick={onLike}
            className={`flex items-center gap-2 px-4 py-2 rounded-softer text-sm font-medium transition-all duration-200 ${
              isLiked
                ? 'bg-pastel-pink-100 text-pastel-pink-600 hover:bg-pastel-pink-200'
                : 'bg-pastel-lavender-50 text-gray-600 hover:bg-pastel-lavender-100'
            }`}
          >
            <svg
              className={`w-5 h-5 ${isLiked ? 'fill-current' : 'stroke-current'}`}
              fill={isLiked ? 'currentColor' : 'none'}
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
              />
            </svg>
            <span>{likesCount}</span>
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-4 py-2 rounded-softer text-sm font-medium text-gray-600 bg-pastel-lavender-50 hover:bg-pastel-lavender-100 transition-all duration-200"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            <span>Download</span>
          </button>
        </div>
      </div>
    </div>
  )
}
