import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { MapContainer, TileLayer, Marker, Popup, useMap, GeoJSON } from 'react-leaflet'
import { LatLng, Icon } from 'leaflet'
import { toast } from 'react-hot-toast'
import {
  Search, Layers, History, FileText, ChevronRight, ChevronDown,
  Calendar, MapPin, Building, Newspaper, AlertCircle, Loader2,
  X, ZoomIn, ZoomOut, Maximize2
} from 'lucide-react'

import Header from '../components/Header'
import SearchPanel from '../components/SearchPanel'
import HistoryPanel from '../components/HistoryPanel'
import LayersPanel from '../components/LayersPanel'
import TimelineView from '../components/TimelineView'
import ReportView from '../components/ReportView'
import { useStore } from '../store/useStore'
import { api } from '../services/api'

// Custom marker icon
const markerIcon = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

// Map controller component
function MapController({ center }: { center: [number, number] | null }) {
  const map = useMap()

  useEffect(() => {
    if (center) {
      map.flyTo(center, 16, { duration: 1.5 })
    }
  }, [center, map])

  return null
}

export default function ResearchPage() {
  const [searchParams] = useSearchParams()

  // State
  const [activePanel, setActivePanel] = useState<'search' | 'layers' | 'history' | null>('search')
  const [showReport, setShowReport] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [mapCenter, setMapCenter] = useState<[number, number] | null>(null)

  // Store
  const {
    selectedLocation,
    setSelectedLocation,
    historicalRecords,
    setHistoricalRecords,
    historicalEvents,
    setHistoricalEvents,
    parcelData,
    setParcelData,
    activeLayers,
    setActiveLayers,
    synthesisReport,
    setSynthesisReport
  } = useStore()

  // Initial search from URL
  useEffect(() => {
    const address = searchParams.get('address')
    if (address) {
      handleSearch(address)
    }
  }, [])

  // Handle address search
  const handleSearch = async (address: string) => {
    setIsLoading(true)
    toast.loading('Searching for property...', { id: 'search' })

    try {
      // Step 1: Geocode the address
      const geocodeResult = await api.geocode(address)

      if (!geocodeResult) {
        toast.error('Could not find that address', { id: 'search' })
        setIsLoading(false)
        return
      }

      const { lat, lon } = geocodeResult

      // Check if within Long Island
      if (!isWithinLongIsland(lat, lon)) {
        toast.error('Address is outside Long Island coverage area', { id: 'search' })
        setIsLoading(false)
        return
      }

      // Update location
      setSelectedLocation({
        address,
        lat,
        lon,
        formatted: geocodeResult.formatted_address
      })

      setMapCenter([lat, lon])
      toast.success('Location found! Starting research...', { id: 'search' })

      // Step 2: Fetch parcel data
      const parcels = await api.getParcelByCoordinates(lat, lon)
      if (parcels.length > 0) {
        setParcelData(parcels[0])
      }

      // Step 3: Deep historical search
      toast.loading('Searching historical archives...', { id: 'history' })

      const historyResults = await api.deepSearch({
        address,
        lat,
        lon,
        yearStart: 1700,
        yearEnd: 2000
      })

      setHistoricalRecords(historyResults.records || [])
      setHistoricalEvents(historyResults.events || [])

      toast.success(
        `Found ${historyResults.records?.length || 0} historical records`,
        { id: 'history' }
      )

      // Switch to history panel
      setActivePanel('history')

    } catch (error) {
      console.error('Search error:', error)
      toast.error('An error occurred during search', { id: 'search' })
    } finally {
      setIsLoading(false)
    }
  }

  // Generate AI synthesis report
  const handleGenerateReport = async () => {
    if (!selectedLocation) return

    setIsLoading(true)
    toast.loading('Generating historical synthesis...', { id: 'synthesis' })

    try {
      const report = await api.generateReport({
        address: selectedLocation.address,
        lat: selectedLocation.lat,
        lon: selectedLocation.lon,
        parcelData,
        historicalRecords,
        historicalEvents
      })

      setSynthesisReport(report)
      setShowReport(true)
      toast.success('Report generated!', { id: 'synthesis' })

    } catch (error) {
      console.error('Synthesis error:', error)
      toast.error('Could not generate report', { id: 'synthesis' })
    } finally {
      setIsLoading(false)
    }
  }

  // Check if coordinates are within Long Island
  const isWithinLongIsland = (lat: number, lon: number): boolean => {
    return (
      lat >= 40.5431 && lat <= 41.1612 &&
      lon >= -74.0421 && lon <= -71.8562
    )
  }

  // Long Island center and bounds
  const longIslandCenter: [number, number] = [40.7891, -73.1350]
  const longIslandBounds: [[number, number], [number, number]] = [
    [40.5431, -74.0421],
    [41.1612, -71.8562]
  ]

  return (
    <div className="h-screen flex flex-col bg-slate-950">
      <Header compact />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-96 bg-slate-900 border-r border-slate-800 flex flex-col">
          {/* Tab buttons */}
          <div className="flex border-b border-slate-800">
            <TabButton
              active={activePanel === 'search'}
              onClick={() => setActivePanel('search')}
              icon={<Search className="w-4 h-4" />}
              label="Search"
            />
            <TabButton
              active={activePanel === 'layers'}
              onClick={() => setActivePanel('layers')}
              icon={<Layers className="w-4 h-4" />}
              label="Layers"
            />
            <TabButton
              active={activePanel === 'history'}
              onClick={() => setActivePanel('history')}
              icon={<History className="w-4 h-4" />}
              label="History"
            />
          </div>

          {/* Panel content */}
          <div className="flex-1 overflow-y-auto">
            {activePanel === 'search' && (
              <SearchPanel onSearch={handleSearch} isLoading={isLoading} />
            )}
            {activePanel === 'layers' && (
              <LayersPanel />
            )}
            {activePanel === 'history' && (
              <HistoryPanel onGenerateReport={handleGenerateReport} isLoading={isLoading} />
            )}
          </div>
        </div>

        {/* Map */}
        <div className="flex-1 relative">
          <MapContainer
            center={longIslandCenter}
            zoom={10}
            className="h-full w-full"
            maxBounds={longIslandBounds}
            minZoom={9}
          >
            {/* Base layer - based on selected layer */}
            {activeLayers.includes('osm') && (
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
            )}

            {activeLayers.includes('nys_ortho') && (
              <TileLayer
                attribution='NYS GIS Program Office'
                url="https://orthos.its.ny.gov/arcgis/rest/services/wms/Latest/MapServer/tile/{z}/{y}/{x}"
              />
            )}

            {activeLayers.includes('usgs_topo') && (
              <TileLayer
                attribution='USGS National Map'
                url="https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}"
              />
            )}

            {/* Default to OSM if no layers selected */}
            {activeLayers.length === 0 && (
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
            )}

            {/* Selected location marker */}
            {selectedLocation && (
              <Marker
                position={[selectedLocation.lat, selectedLocation.lon]}
                icon={markerIcon}
              >
                <Popup>
                  <div className="text-sm">
                    <div className="font-semibold text-white mb-1">
                      {selectedLocation.address}
                    </div>
                    <div className="text-slate-400">
                      {selectedLocation.lat.toFixed(5)}, {selectedLocation.lon.toFixed(5)}
                    </div>
                    {parcelData && (
                      <div className="mt-2 text-xs text-slate-500">
                        SBL: {parcelData.sbl}
                      </div>
                    )}
                  </div>
                </Popup>
              </Marker>
            )}

            <MapController center={mapCenter} />
          </MapContainer>

          {/* Map controls overlay */}
          <div className="absolute top-4 right-4 flex flex-col gap-2 z-[1000]">
            {selectedLocation && (
              <button
                onClick={handleGenerateReport}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600
                           text-slate-900 font-medium rounded-lg transition-colors
                           disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <FileText className="w-4 h-4" />
                )}
                Generate Report
              </button>
            )}
          </div>

          {/* Loading overlay */}
          {isLoading && (
            <div className="absolute inset-0 bg-slate-950/50 flex items-center justify-center z-[1000]">
              <div className="flex flex-col items-center gap-4">
                <div className="spinner" />
                <p className="text-white">Searching archives...</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Report modal */}
      {showReport && synthesisReport && (
        <ReportView
          report={synthesisReport}
          onClose={() => setShowReport(false)}
        />
      )}
    </div>
  )
}

function TabButton({
  active,
  onClick,
  icon,
  label
}: {
  active: boolean
  onClick: () => void
  icon: React.ReactNode
  label: string
}) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium
                  transition-colors ${
        active
          ? 'text-amber-400 border-b-2 border-amber-400 bg-slate-800/50'
          : 'text-slate-400 hover:text-white hover:bg-slate-800/30'
      }`}
    >
      {icon}
      {label}
    </button>
  )
}
