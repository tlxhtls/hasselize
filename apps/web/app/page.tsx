import { AuthButton } from '@/components/AuthButton'
import { FeedCard } from '@/components/FeedCard'
import { createClient } from '@/lib/supabase/server'

interface CameraStyleCard {
  id: string
  name: string
  description: string | null
  is_premium: boolean
}

interface FeedTransformation {
  id: string
  original_image_url: string
  transformed_image_url: string
  thumbnail_url: string | null
}

interface FeedProfile {
  full_name: string | null
}

interface FeedItem {
  id: string
  likes_count: number
  transformations: FeedTransformation | null
  profiles: FeedProfile | null
}

async function getFeedTransformations(): Promise<FeedItem[]> {
  const supabase = await createClient()

  const { data, error } = await supabase
    .from('feed')
    .select(`
      *,
      transformations (
        id,
        original_image_url,
        transformed_image_url,
        thumbnail_url,
        camera_style_id,
        created_at
      ),
      profiles (
        full_name
      )
    `)
    .eq('is_public', true)
    .order('created_at', { ascending: false })
    .limit(20)

  if (error) {
    console.error('Error fetching feed:', error)
    return []
  }

  return data as FeedItem[]
}

async function getCameraStyles(): Promise<CameraStyleCard[]> {
  const supabase = await createClient()

  const { data, error } = await supabase
    .from('camera_styles')
    .select('*')
    .eq('is_active', true)
    .order('display_order')

  if (error || !data) {
    return []
  }

  return data as CameraStyleCard[]
}

export default async function HomePage() {
  const feedItems = await getFeedTransformations()
  const cameraStyles = await getCameraStyles()

  return (
    <div className="min-h-screen bg-gradient-to-b from-pastel-lavender/30 via-white to-pastel-mint/20">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/70 backdrop-blur-xl border-b border-pastel-lavender-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <a href="/" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 bg-gradient-to-br from-pastel-lavender-300 to-pastel-skyBlue-300 rounded-soft shadow-soft group-hover:shadow-soft-lg transition-all" />
              <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-pastel-skyBlue-500 bg-clip-text text-transparent">
                Hasselize
              </span>
            </a>

            {/* Actions */}
            <div className="flex items-center gap-3">
              <AuthButton />
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 sm:py-28 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          {/* Floating decoration */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-pastel-lavender-100/80 text-pastel-lavender-600 text-sm font-medium mb-6 animate-float">
            <span className="w-2 h-2 rounded-full bg-pastel-lavender-400 animate-pulse-soft" />
            AI-powered Photography
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            <span className="bg-gradient-to-r from-gray-900 via-gray-700 to-gray-900 bg-clip-text text-transparent">
              Medium Format Photography
            </span>
            <br />
            <span className="bg-gradient-to-r from-pastel-lavender-500 to-pastel-skyBlue-500 bg-clip-text text-transparent">
              in Your Pocket
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
            Transform your smartphone photos into Hasselblad-quality images with
            superior sharpness and depth of field.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/transform"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold text-white bg-gradient-to-r from-pastel-lavender-400 to-pastel-skyBlue-400 rounded-soft hover:from-pastel-lavender-500 hover:to-pastel-skyBlue-500 transition-all shadow-soft hover:shadow-soft-lg"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Transform Your Photo
            </a>
            <a
              href="#feed"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold text-gray-700 bg-white border-2 border-pastel-lavender-200 rounded-soft hover:bg-pastel-lavender-50 hover:border-pastel-lavender-300 transition-all shadow-soft"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              View Gallery
            </a>
          </div>
        </div>
      </section>

      {/* Camera Styles */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-3">
              Camera Styles
            </h2>
            <p className="text-gray-600">
              Choose your favorite camera look
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
            {cameraStyles.map((style) => (
              <div
                key={style.id}
                className="group bg-white rounded-soft p-5 shadow-soft hover:shadow-soft-xl transition-all duration-300 border-2 border-transparent hover:border-pastel-lavender-200 cursor-default"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 rounded-soft bg-gradient-to-br from-pastel-lavender-100 to-pastel-mint-100 flex items-center justify-center">
                    <svg className="w-5 h-5 text-pastel-lavender-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0016.07 6H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    </svg>
                  </div>
                  {style.is_premium && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-pastel-peach-100 text-pastel-peach-600">
                      Premium
                    </span>
                  )}
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{style.name}</h3>
                <p className="text-sm text-gray-600">{style.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="max-w-4xl mx-auto px-4">
        <div className="h-px bg-gradient-to-r from-transparent via-pastel-lavender-200 to-transparent" />
      </div>

      {/* Feed */}
      <section id="feed" className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-3">
              Community Gallery
            </h2>
            <p className="text-gray-600">
              See beautiful photos created by our community
            </p>
          </div>

          {feedItems.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {feedItems.map((item) => {
                const transformation = item.transformations
                const profile = item.profiles

                if (!transformation) {
                  return null
                }

                return (
                  <FeedCard
                    key={item.id}
                    id={transformation.id}
                    originalImage={transformation.original_image_url}
                    transformedImage={transformation.transformed_image_url}
                    thumbnail={transformation.thumbnail_url ?? undefined}
                    cameraStyle="Hasselblad"
                    userName={profile?.full_name ?? undefined}
                    likesCount={item.likes_count}
                  />
                )
              })}
            </div>
          ) : (
            <div className="text-center py-16 px-6 bg-white rounded-soft shadow-soft max-w-md mx-auto">
              <div className="w-16 h-16 rounded-full bg-pastel-lavender-100 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-pastel-lavender-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <p className="text-gray-600 font-medium">No photos yet.</p>
              <p className="text-gray-500 text-sm mt-1">Be the first to share!</p>
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 sm:px-6 lg:px-8 border-t border-pastel-lavender-200">
        <div className="max-w-7xl mx-auto text-center text-sm text-gray-500">
          <p>Made with love by Hasselize Team</p>
        </div>
      </footer>
    </div>
  )
}
