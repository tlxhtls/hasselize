export default function ProfileLoading() {
  return (
    <div className="min-h-screen pb-12 animate-pulse">
      {/* Header Skeleton */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="h-7 w-24 bg-gray-200 rounded"></div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Profile Header Skeleton */}
        <div className="mb-8">
          <div className="h-9 w-32 bg-gray-200 rounded mb-2"></div>
          <div className="h-6 w-48 bg-gray-200 rounded"></div>
        </div>

        {/* Stats Skeleton */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-lg p-6 shadow-sm">
              <div className="h-9 w-16 bg-gray-200 rounded mb-1"></div>
              <div className="h-5 w-24 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>

        {/* Transformations Skeleton */}
        <div>
          <div className="h-7 w-48 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white rounded-lg overflow-hidden shadow-sm h-64">
                <div className="w-full h-full bg-gray-200"></div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
