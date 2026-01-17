import { create } from 'zustand'

interface Location {
  address: string
  lat: number
  lon: number
  formatted?: string
}

interface ParcelData {
  sbl: string
  address?: string
  municipality?: string
  county?: string
  owner_name?: string
  acreage?: number
  land_use_code?: string
  land_use_description?: string
  year_built?: number
  assessed_value?: number
  deed_book?: string
  deed_page?: string
  deed_date?: string
  boundary?: any
  centroid?: any
}

interface HistoricalRecord {
  id: string
  source: string
  source_name: string
  date: string
  year: number
  title?: string
  snippet: string
  full_text_available: boolean
  url?: string
  page_number?: number
  confidence_score: number
  relevance_score: number
  record_type: string
}

interface HistoricalEvent {
  event_id: string
  name: string
  date: string
  year: number
  description: string
  event_type: string
  geographic_scope: string
  sources: string[]
  relevance_to_property?: string
}

interface SynthesisReport {
  property_address: string
  coordinates: { lat: number; lon: number }
  executive_summary: string
  confidence_level: string
  timeline: any[]
  key_findings: string[]
  historical_context: string
  notable_events: any[]
  land_use_history: string
  sources_cited: string[]
  data_gaps: string[]
  recommendations_for_further_research: string[]
  disclaimer: string
}

interface AppState {
  // Selected location
  selectedLocation: Location | null
  setSelectedLocation: (location: Location | null) => void

  // Parcel data
  parcelData: ParcelData | null
  setParcelData: (data: ParcelData | null) => void

  // Historical records
  historicalRecords: HistoricalRecord[]
  setHistoricalRecords: (records: HistoricalRecord[]) => void

  // Historical events
  historicalEvents: HistoricalEvent[]
  setHistoricalEvents: (events: HistoricalEvent[]) => void

  // Synthesis report
  synthesisReport: SynthesisReport | null
  setSynthesisReport: (report: SynthesisReport | null) => void

  // Active map layers
  activeLayers: string[]
  setActiveLayers: (layers: string[]) => void
  toggleLayer: (layerId: string) => void

  // Search history
  searchHistory: string[]
  addToSearchHistory: (address: string) => void

  // UI state
  isLoading: boolean
  setIsLoading: (loading: boolean) => void

  // Reset state
  resetSearch: () => void
}

export const useStore = create<AppState>((set, get) => ({
  // Selected location
  selectedLocation: null,
  setSelectedLocation: (location) => set({ selectedLocation: location }),

  // Parcel data
  parcelData: null,
  setParcelData: (data) => set({ parcelData: data }),

  // Historical records
  historicalRecords: [],
  setHistoricalRecords: (records) => set({ historicalRecords: records }),

  // Historical events
  historicalEvents: [],
  setHistoricalEvents: (events) => set({ historicalEvents: events }),

  // Synthesis report
  synthesisReport: null,
  setSynthesisReport: (report) => set({ synthesisReport: report }),

  // Active map layers
  activeLayers: ['osm'],
  setActiveLayers: (layers) => set({ activeLayers: layers }),
  toggleLayer: (layerId) => {
    const { activeLayers } = get()

    // Base layers are mutually exclusive
    const baseLayers = ['osm', 'nys_ortho', 'usgs_topo']

    if (baseLayers.includes(layerId)) {
      // If clicking a base layer, replace other base layers
      const newLayers = activeLayers.filter(l => !baseLayers.includes(l))
      if (!activeLayers.includes(layerId)) {
        newLayers.push(layerId)
      }
      set({ activeLayers: newLayers })
    } else {
      // Toggle overlay layer
      if (activeLayers.includes(layerId)) {
        set({ activeLayers: activeLayers.filter(l => l !== layerId) })
      } else {
        set({ activeLayers: [...activeLayers, layerId] })
      }
    }
  },

  // Search history
  searchHistory: [],
  addToSearchHistory: (address) => {
    const { searchHistory } = get()
    const newHistory = [
      address,
      ...searchHistory.filter(a => a !== address)
    ].slice(0, 10)
    set({ searchHistory: newHistory })
  },

  // UI state
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Reset search
  resetSearch: () => set({
    selectedLocation: null,
    parcelData: null,
    historicalRecords: [],
    historicalEvents: [],
    synthesisReport: null
  })
}))
