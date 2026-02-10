import { AuthButton } from '@/components/AuthButton'
import { FeedCard } from '@/components/FeedCard'
import { createClient } from '@/lib/supabase/server'

async function getFeedTransformations() {
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

  return data
}

async function getCameraStyles() {
  const supabase = await createClient()

  const { data } = await supabase
    .from('camera_styles')
    .select('*')
    .eq('is_active', true)
    .order('display_order')

  return data || []
}

export default async function HomePage() {
  const feedItems = await getFeedTransformations()
  const cameraStyles = await getCameraStyles()

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg" />
              <span className="text-xl font-bold text-gray-900">Hasselize</span>
            </div>

            {/* Auth Button */}
            <AuthButton />
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Medium Format Photography in Your Pocket
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            Transform your smartphone photos into Hasselblad-quality images with
            superior sharpness and depth of field.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/transform"
              className="px-6 py-3 text-base font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
            >
              Transform Your Photo
            </a>
            <a
              href="#feed"
              className="px-6 py-3 text-base font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              View Gallery
            </a>
          </div>
        </div>
      </section>

      {/* Camera Styles */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Camera Styles</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {cameraStyles.map((style) => (
              <div
                key={style.id}
                className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{style.name}</h3>
                  {style.is_premium && (
                    <span className="text-xs font-medium text-amber-600 bg-amber-50 px-2 py-0.5 rounded">
                      Premium
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600">{style.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feed */}
      <section id="feed" className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Community Gallery</h2>
          {feedItems.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {feedItems.map((item) => {
                const transformation = item.transformations as any
                const profile = item.profiles as any

                return (
                  <FeedCard
                    key={item.id}
                    id={transformation.id}
                    originalImage={transformation.original_image_url}
                    transformedImage={transformation.transformed_image_url}
                    thumbnail={transformation.thumbnail_url}
                    cameraStyle="Hasselblad"
                    userName={profile?.full_name}
                    likesCount={item.likes_count}
                  />
                )
              })}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">No photos yet. Be the first to share!</p>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
