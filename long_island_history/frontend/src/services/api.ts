import axios from 'axios'

const API_BASE = '/api'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 minutes for deep searches
  headers: {
    'Content-Type': 'application/json'
  }
})

export const api = {
  /**
   * Geocode an address to coordinates
   */
  async geocode(address: string) {
    try {
      const response = await client.get('/parcels/search/address', {
        params: { address, include_boundary: false }
      })

      if (response.data.success && response.data.results.length > 0) {
        const parcel = response.data.results[0]
        return {
          lat: parcel.centroid?.lat || 40.7891,
          lon: parcel.centroid?.lon || -73.135,
          formatted_address: parcel.address
        }
      }

      // Fallback to a simple geocoding approach using the geocoding service
      // In production, this would call a geocoding API
      return await this.simpleGeocode(address)

    } catch (error) {
      console.error('Geocoding error:', error)
      return await this.simpleGeocode(address)
    }
  },

  /**
   * Simple fallback geocoding for known Long Island locations
   */
  async simpleGeocode(address: string) {
    const addressLower = address.toLowerCase()

    // Known locations for demo
    const knownLocations: Record<string, { lat: number; lon: number }> = {
      'bay shore': { lat: 40.7251, lon: -73.2454 },
      'huntington': { lat: 40.8682, lon: -73.4257 },
      'patchogue': { lat: 40.7654, lon: -73.0151 },
      'babylon': { lat: 40.6956, lon: -73.3257 },
      'islip': { lat: 40.7295, lon: -73.2107 },
      'smithtown': { lat: 40.8557, lon: -73.2007 },
      'riverhead': { lat: 40.9170, lon: -72.6620 },
      'southampton': { lat: 40.8843, lon: -72.3896 },
      'east hampton': { lat: 40.9634, lon: -72.1848 },
      'montauk': { lat: 41.0359, lon: -71.9545 },
      'freeport': { lat: 40.6576, lon: -73.5832 },
      'hempstead': { lat: 40.7062, lon: -73.6187 },
      'garden city': { lat: 40.7268, lon: -73.6343 },
      'mineola': { lat: 40.7490, lon: -73.6407 },
      'oyster bay': { lat: 40.8715, lon: -73.5318 },
      'glen cove': { lat: 40.8623, lon: -73.6332 }
    }

    for (const [name, coords] of Object.entries(knownLocations)) {
      if (addressLower.includes(name)) {
        return {
          lat: coords.lat,
          lon: coords.lon,
          formatted_address: address
        }
      }
    }

    // Default to Bay Shore if nothing found
    return {
      lat: 40.7251,
      lon: -73.2454,
      formatted_address: address
    }
  },

  /**
   * Get parcel data by coordinates
   */
  async getParcelByCoordinates(lat: number, lon: number) {
    try {
      const response = await client.get('/parcels/search/coordinates', {
        params: { lat, lon, include_boundary: true }
      })
      return response.data.results || []
    } catch (error) {
      console.error('Parcel search error:', error)
      return []
    }
  },

  /**
   * Get parcel data by SBL
   */
  async getParcelBySBL(sbl: string) {
    try {
      const response = await client.get(`/parcels/search/sbl/${sbl}`)
      return response.data.results || []
    } catch (error) {
      console.error('SBL search error:', error)
      return []
    }
  },

  /**
   * Deep historical search
   */
  async deepSearch(params: {
    address: string
    lat: number
    lon: number
    yearStart?: number
    yearEnd?: number
    includeNewspapers?: boolean
    includeMilitary?: boolean
    includeDeeds?: boolean
    deepMode?: boolean
  }) {
    try {
      const response = await client.post('/history/deep-search', null, {
        params: {
          address: params.address,
          lat: params.lat,
          lon: params.lon,
          year_start: params.yearStart || 1700,
          year_end: params.yearEnd || 2000,
          include_newspapers: params.includeNewspapers !== false,
          include_military: params.includeMilitary !== false,
          include_deeds: params.includeDeeds !== false,
          deep_mode: params.deepMode !== false
        }
      })
      return {
        records: response.data.records || [],
        events: response.data.related_events || []
      }
    } catch (error) {
      console.error('Deep search error:', error)
      // Return empty results on error
      return { records: [], events: [] }
    }
  },

  /**
   * Generate AI synthesis report
   */
  async generateReport(params: {
    address: string
    lat: number
    lon: number
    parcelData?: any
    historicalRecords?: any[]
    historicalEvents?: any[]
  }) {
    try {
      const response = await client.post('/synthesis/comprehensive-report', {
        address: params.address,
        lat: params.lat,
        lon: params.lon,
        parcel_data: params.parcelData,
        historical_records: params.historicalRecords || [],
        historical_events: params.historicalEvents || [],
        imagery_available: [],
        synthesis_type: 'comprehensive'
      })
      return response.data
    } catch (error) {
      console.error('Report generation error:', error)
      throw error
    }
  },

  /**
   * Get available imagery for a location
   */
  async getAvailableImagery(lat: number, lon: number) {
    try {
      const response = await client.get('/imagery/available', {
        params: { lat, lon }
      })
      return response.data.available_imagery || []
    } catch (error) {
      console.error('Imagery error:', error)
      return []
    }
  },

  /**
   * Get available Sanborn maps
   */
  async getSanbornMaps(lat: number, lon: number, municipality?: string) {
    try {
      const response = await client.get('/maps/sanborn/available', {
        params: { lat, lon, municipality }
      })
      return response.data.maps || []
    } catch (error) {
      console.error('Sanborn maps error:', error)
      return []
    }
  },

  /**
   * Get historical periods/map layers
   */
  async getHistoricalPeriods() {
    try {
      const response = await client.get('/maps/historical-periods')
      return response.data.periods || []
    } catch (error) {
      console.error('Historical periods error:', error)
      return []
    }
  },

  /**
   * Get GeoJSON layer
   */
  async getGeoJsonLayer(layerId: string) {
    try {
      const response = await client.get(`/maps/geojson/${layerId}`)
      return response.data
    } catch (error) {
      console.error('GeoJSON error:', error)
      return null
    }
  },

  /**
   * Get Long Island historical events
   */
  async getHistoricalEvents(params?: {
    yearStart?: number
    yearEnd?: number
    eventType?: string
    municipality?: string
  }) {
    try {
      const response = await client.get('/history/events/long-island', {
        params: {
          year_start: params?.yearStart || 1600,
          year_end: params?.yearEnd || 2024,
          event_type: params?.eventType,
          municipality: params?.municipality
        }
      })
      return response.data.events || []
    } catch (error) {
      console.error('Events error:', error)
      return []
    }
  },

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await client.get('/health')
      return response.data
    } catch (error) {
      console.error('Health check error:', error)
      return { status: 'error' }
    }
  }
}
