import { useState } from 'react'
import { Layers, Map, Image, History, ChevronDown, ChevronRight, Eye, EyeOff } from 'lucide-react'
import { useStore } from '../store/useStore'

interface LayerOption {
  id: string
  name: string
  description: string
  category: 'base' | 'historical' | 'overlay'
  year?: number | string
}

const layerOptions: LayerOption[] = [
  // Base layers
  {
    id: 'osm',
    name: 'OpenStreetMap',
    description: 'Standard street map',
    category: 'base'
  },
  {
    id: 'nys_ortho',
    name: 'NYS Orthoimagery (Latest)',
    description: 'Most recent aerial photography',
    category: 'base'
  },
  {
    id: 'usgs_topo',
    name: 'USGS Topographic',
    description: 'Current USGS topo map',
    category: 'base'
  },
  // Historical imagery
  {
    id: 'nys_ortho_2019',
    name: 'NYS Ortho 2019',
    description: 'Leaf-off imagery',
    category: 'historical',
    year: 2019
  },
  {
    id: 'nys_ortho_2016',
    name: 'NYS Ortho 2016',
    description: 'Statewide imagery',
    category: 'historical',
    year: 2016
  },
  {
    id: 'nys_ortho_2010',
    name: 'NYS Ortho 2010',
    description: 'Historical aerial',
    category: 'historical',
    year: 2010
  },
  {
    id: 'nys_ortho_2004',
    name: 'NYS Ortho 2004',
    description: 'Nassau/Suffolk imagery',
    category: 'historical',
    year: 2004
  },
  {
    id: 'nys_ortho_1994',
    name: 'NYS Ortho 1994',
    description: 'First statewide digital',
    category: 'historical',
    year: 1994
  },
  // Overlays
  {
    id: 'parcels',
    name: 'Parcel Boundaries',
    description: 'Property lines',
    category: 'overlay'
  },
  {
    id: 'native_territories',
    name: 'Native Territories',
    description: 'Pre-contact tribal areas',
    category: 'overlay',
    year: 'Pre-1624'
  },
  {
    id: 'colonial_towns',
    name: 'Colonial Townships',
    description: 'Historical town boundaries',
    category: 'overlay',
    year: '1683'
  },
  {
    id: 'battle_long_island',
    name: 'Battle of Long Island',
    description: 'Revolutionary War sites',
    category: 'overlay',
    year: '1776'
  },
  {
    id: 'lirr_1890',
    name: 'LIRR Network 1890',
    description: 'Historical railroad routes',
    category: 'overlay',
    year: '1890'
  }
]

export default function LayersPanel() {
  const [expandedCategory, setExpandedCategory] = useState<string | null>('base')
  const { activeLayers, setActiveLayers, toggleLayer } = useStore()

  const categories = [
    { id: 'base', name: 'Base Maps', icon: Map },
    { id: 'historical', name: 'Historical Imagery', icon: History },
    { id: 'overlay', name: 'Overlays', icon: Layers }
  ]

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold text-white mb-4">Map Layers</h2>

      {/* Category sections */}
      {categories.map((category) => {
        const Icon = category.icon
        const categoryLayers = layerOptions.filter(l => l.category === category.id)
        const activeCount = categoryLayers.filter(l => activeLayers.includes(l.id)).length

        return (
          <div key={category.id} className="mb-4">
            <button
              onClick={() => setExpandedCategory(
                expandedCategory === category.id ? null : category.id
              )}
              className="w-full flex items-center justify-between p-3 bg-slate-800/50
                         rounded-lg hover:bg-slate-800 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Icon className="w-5 h-5 text-amber-400" />
                <span className="font-medium text-white">{category.name}</span>
                {activeCount > 0 && (
                  <span className="text-xs px-1.5 py-0.5 bg-amber-500/20 text-amber-400 rounded">
                    {activeCount}
                  </span>
                )}
              </div>
              {expandedCategory === category.id ? (
                <ChevronDown className="w-5 h-5 text-slate-400" />
              ) : (
                <ChevronRight className="w-5 h-5 text-slate-400" />
              )}
            </button>

            {expandedCategory === category.id && (
              <div className="mt-2 space-y-1">
                {categoryLayers.map((layer) => (
                  <LayerToggle
                    key={layer.id}
                    layer={layer}
                    isActive={activeLayers.includes(layer.id)}
                    onToggle={() => toggleLayer(layer.id)}
                  />
                ))}
              </div>
            )}
          </div>
        )
      })}

      {/* Active layers summary */}
      {activeLayers.length > 0 && (
        <div className="mt-6 p-4 bg-slate-800/30 rounded-lg">
          <h4 className="text-sm font-medium text-slate-400 mb-2">Active Layers</h4>
          <div className="flex flex-wrap gap-2">
            {activeLayers.map((layerId) => {
              const layer = layerOptions.find(l => l.id === layerId)
              return layer ? (
                <span
                  key={layerId}
                  className="text-xs px-2 py-1 bg-amber-500/20 text-amber-400 rounded"
                >
                  {layer.name}
                </span>
              ) : null
            })}
          </div>
        </div>
      )}

      {/* Layer info */}
      <div className="mt-6 p-4 bg-slate-800/30 rounded-lg">
        <h4 className="text-sm font-medium text-slate-400 mb-2">About Layers</h4>
        <ul className="text-xs text-slate-500 space-y-1">
          <li>• Base maps are mutually exclusive</li>
          <li>• Historical imagery shows aerial photos from that year</li>
          <li>• Overlays can be stacked on any base map</li>
        </ul>
      </div>
    </div>
  )
}

function LayerToggle({
  layer,
  isActive,
  onToggle
}: {
  layer: LayerOption
  isActive: boolean
  onToggle: () => void
}) {
  return (
    <button
      onClick={onToggle}
      className={`w-full flex items-center justify-between p-3 rounded-lg
                  transition-colors ${
        isActive
          ? 'bg-amber-500/10 border border-amber-500/30'
          : 'bg-slate-800/30 hover:bg-slate-800/50 border border-transparent'
      }`}
    >
      <div className="flex-1 text-left">
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${isActive ? 'text-amber-400' : 'text-white'}`}>
            {layer.name}
          </span>
          {layer.year && (
            <span className="text-xs text-slate-500">{layer.year}</span>
          )}
        </div>
        <p className="text-xs text-slate-500 mt-0.5">{layer.description}</p>
      </div>
      {isActive ? (
        <Eye className="w-4 h-4 text-amber-400 flex-shrink-0" />
      ) : (
        <EyeOff className="w-4 h-4 text-slate-500 flex-shrink-0" />
      )}
    </button>
  )
}
