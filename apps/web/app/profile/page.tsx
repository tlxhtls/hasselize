import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import { SignOutButton } from '@/components/auth/SignOutButton'

export default async function ProfilePage() {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  // Fetch user profile
  const { data: profile } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', user.id)
    .single()

  // Fetch user transformations
  const { data: transformations } = await supabase
    .from('transformations')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })
    .limit(20)

  return (
    <div className="min-h-screen pb-12">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <a href="/" className="text-xl font-bold text-gray-900">
            Hasselize
          </a>
          <SignOutButton />
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Profile Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile</h1>
          <div className="flex items-center gap-2 text-gray-600">
            <span className="font-medium">Logged in as:</span>
            <span>{user.email}</span>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="text-3xl font-bold text-primary-600">
              {profile?.credits_remaining || 0}
            </div>
            <div className="text-sm text-gray-600 mt-1">Credits Remaining</div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="text-3xl font-bold text-gray-900">
              {transformations?.length || 0}
            </div>
            <div className="text-sm text-gray-600 mt-1">Transformations</div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="text-3xl font-bold text-gray-900 capitalize">
              {profile?.subscription_tier || 'free'}
            </div>
            <div className="text-sm text-gray-600 mt-1">Plan</div>
          </div>
        </div>

        {/* Transformations */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Your Transformations
          </h2>
          {transformations && transformations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {transformations.map((transform) => (
                <a
                  key={transform.id}
                  href={transform.transformed_image_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow"
                >
                  <img
                    src={transform.thumbnail_url || transform.transformed_image_url}
                    alt="Transformation"
                    className="w-full aspect-square object-cover"
                  />
                  <div className="p-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="capitalize text-gray-600">
                        {transform.camera_style_id}
                      </span>
                      <span className="text-gray-500">
                        {new Date(transform.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-white rounded-lg">
              <p className="text-gray-500 mb-4">No transformations yet</p>
              <a
                href="/transform"
                className="inline-block px-6 py-2 text-white bg-primary-600 rounded-lg hover:bg-primary-700"
              >
                Transform Your First Photo
              </a>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
