'use client'

import { useCallback, useState } from 'react'
import { compressImage, validateImageFile } from '@/lib/storage/image-utils'

interface ImageUploaderProps {
  onImageSelect: (file: File) => void
  onError?: (error: string) => void
  className?: string
}

export function ImageUploader({
  onImageSelect,
  onError,
  className = '',
}: ImageUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleFile = useCallback(
    async (file: File) => {
      // Validate file
      const validation = validateImageFile(file)
      if (!validation.valid) {
        onError?.(validation.error || 'Invalid file')
        return
      }

      try {
        setIsLoading(true)

        // Compress image if needed
        const compressed = await compressImage(file, 2048, 2048, 0.85)
        const compressedFile = new File([compressed], file.name, {
          type: 'image/jpeg',
        })

        onImageSelect(compressedFile)
      } catch (error) {
        onError?.(error instanceof Error ? error.message : 'Failed to process image')
      } finally {
        setIsLoading(false)
      }
    },
    [onImageSelect, onError]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      setIsDragging(false)

      const files = Array.from(e.dataTransfer.files)
      if (files.length > 0) {
        handleFile(files[0])
      }
    },
    [handleFile]
  )

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (files && files.length > 0) {
        handleFile(files[0])
      }
    },
    [handleFile]
  )

  return (
    <div
      className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
        isDragging
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-300 hover:border-gray-400'
      } ${className}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <input
        type="file"
        accept="image/*"
        onChange={handleFileInput}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={isLoading}
      />

      {isLoading ? (
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
          <p className="text-sm text-gray-600">Processing image...</p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3">
          <svg
            className="w-12 h-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <div>
            <p className="text-sm font-medium text-gray-700">
              Drop your photo here or click to upload
            </p>
            <p className="text-xs text-gray-500 mt-1">
              JPEG, PNG, or WebP up to 10MB
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
