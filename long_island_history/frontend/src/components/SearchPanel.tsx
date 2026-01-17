import { useState } from 'react'
import { Search, MapPin, Clock, Loader2 } from 'lucide-react'
import { useStore } from '../store/useStore'

interface SearchPanelProps {
  onSearch: (address: string) => void
  isLoading: boolean
}

export default function SearchPanel({ onSearch, isLoading }: SearchPanelProps) {
  const [address, setAddress] = useState('')
  const { selectedLocation, parcelData } = useStore()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (address.trim()) {
      onSearch(address.trim())
    }
  }

  const recentSearches = [
    "5 Lawrence Court, Bay Shore, NY",
    "Main Street, Huntington, NY",
    "Ocean Avenue, Patchogue, NY"
  ]

  return (
    <div className="p-4">
      {/* Search form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="relative">
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Enter a Long Island address..."
            className="search-input pr-24"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !address.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2
                       bg-amber-500 hover:bg-amber-600 disabled:bg-slate-600
                       text-slate-900 font-medium rounded-lg transition-colors
                       disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
          </button>
        </div>
      </form>

      {/* Current location info */}
      {selectedLocation && (
        <div className="mb-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
          <div className="flex items-start gap-3">
            <MapPin className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-medium text-white">
                {selectedLocation.formatted || selectedLocation.address}
              </h3>
              <p className="text-sm text-slate-400 mt-1">
                {selectedLocation.lat.toFixed(5)}, {selectedLocation.lon.toFixed(5)}
              </p>
              {parcelData && (
                <div className="mt-3 pt-3 border-t border-slate-700">
                  <p className="text-xs text-slate-500 mb-1">PARCEL DATA</p>
                  <p className="text-sm text-slate-300">SBL: {parcelData.sbl}</p>
                  {parcelData.municipality && (
                    <p className="text-sm text-slate-300">
                      {parcelData.municipality}, {parcelData.county} County
                    </p>
                  )}
                  {parcelData.acreage && (
                    <p className="text-sm text-slate-400">
                      {parcelData.acreage} acres
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Quick search examples */}
      {!selectedLocation && (
        <div>
          <h3 className="text-sm font-medium text-slate-400 mb-3 flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Example Searches
          </h3>
          <div className="space-y-2">
            {recentSearches.map((search, i) => (
              <button
                key={i}
                onClick={() => {
                  setAddress(search)
                  onSearch(search)
                }}
                disabled={isLoading}
                className="w-full text-left p-3 bg-slate-800/30 hover:bg-slate-800/50
                           rounded-lg text-slate-300 text-sm transition-colors
                           disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {search}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Search tips */}
      <div className="mt-6 p-4 bg-slate-800/30 rounded-lg">
        <h4 className="text-sm font-medium text-slate-400 mb-2">Search Tips</h4>
        <ul className="text-xs text-slate-500 space-y-1">
          <li>• Enter a full street address for best results</li>
          <li>• Include city/town name (e.g., "Bay Shore, NY")</li>
          <li>• Coverage: Suffolk and Nassau Counties only</li>
        </ul>
      </div>
    </div>
  )
}
