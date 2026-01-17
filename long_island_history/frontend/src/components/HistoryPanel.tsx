import { useState } from 'react'
import {
  Newspaper, Calendar, MapPin, FileText, ChevronDown, ChevronRight,
  ExternalLink, AlertCircle, Loader2, History, Scroll
} from 'lucide-react'
import { useStore } from '../store/useStore'

interface HistoryPanelProps {
  onGenerateReport: () => void
  isLoading: boolean
}

export default function HistoryPanel({ onGenerateReport, isLoading }: HistoryPanelProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>('records')
  const { historicalRecords, historicalEvents, selectedLocation } = useStore()

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  if (!selectedLocation) {
    return (
      <div className="p-4">
        <div className="text-center py-12">
          <History className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-400 mb-2">
            No Location Selected
          </h3>
          <p className="text-sm text-slate-500">
            Search for an address to view historical records
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4">
      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <div className="p-3 bg-slate-800/50 rounded-lg">
          <div className="text-2xl font-bold text-amber-400">
            {historicalRecords.length}
          </div>
          <div className="text-xs text-slate-400">Historical Records</div>
        </div>
        <div className="p-3 bg-slate-800/50 rounded-lg">
          <div className="text-2xl font-bold text-amber-400">
            {historicalEvents.length}
          </div>
          <div className="text-xs text-slate-400">Related Events</div>
        </div>
      </div>

      {/* Generate report button */}
      <button
        onClick={onGenerateReport}
        disabled={isLoading}
        className="w-full py-3 px-4 bg-amber-500 hover:bg-amber-600
                   disabled:bg-slate-600 text-slate-900 font-semibold
                   rounded-lg transition-colors flex items-center justify-center gap-2
                   disabled:cursor-not-allowed mb-6"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Generating...
          </>
        ) : (
          <>
            <FileText className="w-5 h-5" />
            Generate AI Report
          </>
        )}
      </button>

      {/* Historical Records Section */}
      <div className="mb-4">
        <button
          onClick={() => toggleSection('records')}
          className="w-full flex items-center justify-between p-3 bg-slate-800/50
                     rounded-lg hover:bg-slate-800 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Newspaper className="w-5 h-5 text-amber-400" />
            <span className="font-medium text-white">Historical Records</span>
            <span className="text-xs text-slate-500">
              ({historicalRecords.length})
            </span>
          </div>
          {expandedSection === 'records' ? (
            <ChevronDown className="w-5 h-5 text-slate-400" />
          ) : (
            <ChevronRight className="w-5 h-5 text-slate-400" />
          )}
        </button>

        {expandedSection === 'records' && (
          <div className="mt-2 space-y-2">
            {historicalRecords.length === 0 ? (
              <div className="p-4 bg-slate-800/30 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-slate-400 text-sm">
                      No historical records found in digital archives.
                    </p>
                    <p className="text-slate-500 text-xs mt-1">
                      This doesn't mean no history exists—physical records may be
                      available at county clerk offices.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              historicalRecords.slice(0, 10).map((record, i) => (
                <RecordCard key={record.id || i} record={record} />
              ))
            )}
            {historicalRecords.length > 10 && (
              <p className="text-center text-sm text-slate-500 py-2">
                + {historicalRecords.length - 10} more records
              </p>
            )}
          </div>
        )}
      </div>

      {/* Historical Events Section */}
      <div className="mb-4">
        <button
          onClick={() => toggleSection('events')}
          className="w-full flex items-center justify-between p-3 bg-slate-800/50
                     rounded-lg hover:bg-slate-800 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Scroll className="w-5 h-5 text-amber-400" />
            <span className="font-medium text-white">Historical Events</span>
            <span className="text-xs text-slate-500">
              ({historicalEvents.length})
            </span>
          </div>
          {expandedSection === 'events' ? (
            <ChevronDown className="w-5 h-5 text-slate-400" />
          ) : (
            <ChevronRight className="w-5 h-5 text-slate-400" />
          )}
        </button>

        {expandedSection === 'events' && (
          <div className="mt-2 space-y-2">
            {historicalEvents.length === 0 ? (
              <div className="p-4 bg-slate-800/30 rounded-lg text-center">
                <p className="text-slate-400 text-sm">
                  No significant historical events found for this location.
                </p>
              </div>
            ) : (
              historicalEvents.map((event, i) => (
                <EventCard key={event.event_id || i} event={event} />
              ))
            )}
          </div>
        )}
      </div>

      {/* Research tips */}
      <div className="mt-6 p-4 bg-slate-800/30 rounded-lg">
        <h4 className="text-sm font-medium text-slate-400 mb-2">
          For More Information
        </h4>
        <ul className="text-xs text-slate-500 space-y-2">
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Visit Suffolk/Nassau County Clerk for physical deed records</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Check local historical societies for additional archives</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>
              Search{' '}
              <a
                href="https://fultonhistory.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-amber-400 hover:underline"
              >
                FultonHistory.com
              </a>
              {' '}directly for more newspapers
            </span>
          </li>
        </ul>
      </div>
    </div>
  )
}

function RecordCard({ record }: { record: any }) {
  return (
    <div className="p-3 bg-slate-800/30 rounded-lg hover:bg-slate-800/50 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium text-amber-400">
              {record.year || 'Unknown year'}
            </span>
            <span className="text-slate-600">•</span>
            <span className="text-xs text-slate-400 truncate">
              {record.source_name || record.source}
            </span>
          </div>
          <p className="text-sm text-slate-300 line-clamp-2">
            {record.snippet}
          </p>
        </div>
        {record.url && (
          <a
            href={record.url}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-2 p-1 text-slate-500 hover:text-amber-400 flex-shrink-0"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>
    </div>
  )
}

function EventCard({ event }: { event: any }) {
  return (
    <div className="p-3 bg-slate-800/30 rounded-lg">
      <div className="flex items-start gap-3">
        <div className="w-16 flex-shrink-0">
          <span className="text-sm font-bold text-amber-400">
            {event.year}
          </span>
        </div>
        <div>
          <h4 className="text-sm font-medium text-white mb-1">
            {event.name}
          </h4>
          <p className="text-xs text-slate-400 line-clamp-2">
            {event.description}
          </p>
          {event.event_type && (
            <span className="inline-block mt-2 px-2 py-0.5 bg-slate-700 rounded text-xs text-slate-300">
              {event.event_type}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
