'use client'

import { useState } from 'react'
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

  const handleDownload = () => {
    downloadImage(transformedImage, `hasselized-${id}.jpg`)
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm overflow-hidden ${className}`}>
      {/* Before/After Slider */}
      <div className="relative bg-gray-100">
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
          className={`w-full ${imageLoaded ? 'block' : 'hidden'}`}
          onLoad={() => setImageLoaded(true)}
        />
      </div>

      {/* Card Content */}
      <div className="p-4">
        {/* Camera Style Badge */}
        <div className="flex items-center justify-between mb-3">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
            {cameraStyle}
          </span>
          <span className="text-xs text-gray-500">
            {userName || 'Anonymous'}
          </span>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <button
            onClick={onLike}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ${
              isLiked
                ? 'text-red-500 bg-red-50 hover:bg-red-100'
                : 'text-gray-600 hover:bg-gray-100'
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
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-gray-600 hover:bg-gray-100 transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
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
