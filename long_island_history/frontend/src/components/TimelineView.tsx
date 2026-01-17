import { Calendar, MapPin, Newspaper, Scroll } from 'lucide-react'

interface TimelineEvent {
  date: string
  year: number
  event: string
  source?: string
  type?: string
}

interface TimelineViewProps {
  events: TimelineEvent[]
}

export default function TimelineView({ events }: TimelineViewProps) {
  if (events.length === 0) {
    return (
      <div className="text-center py-12">
        <Calendar className="w-12 h-12 text-slate-600 mx-auto mb-4" />
        <p className="text-slate-400">No timeline events to display</p>
      </div>
    )
  }

  // Group events by era
  const eras = groupByEra(events)

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-[23px] top-0 bottom-0 w-0.5 bg-gradient-to-b from-amber-500/50 via-amber-500/30 to-transparent" />

      {Object.entries(eras).map(([era, eraEvents]) => (
        <div key={era} className="mb-8">
          {/* Era header */}
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-amber-500/20 rounded-full flex items-center justify-center z-10">
              <Scroll className="w-6 h-6 text-amber-400" />
            </div>
            <h3 className="text-lg font-semibold text-amber-400">{era}</h3>
          </div>

          {/* Events in this era */}
          <div className="ml-6 pl-6 border-l-2 border-slate-700 space-y-4">
            {eraEvents.map((event, i) => (
              <TimelineEventCard key={i} event={event} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function TimelineEventCard({ event }: { event: TimelineEvent }) {
  const icon = getEventIcon(event.type)

  return (
    <div className="relative">
      {/* Connector dot */}
      <div className="absolute -left-[30px] top-2 w-3 h-3 bg-slate-700 border-2 border-amber-500 rounded-full" />

      {/* Event card */}
      <div className="p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-slate-700/50 rounded-lg">
            {icon}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-amber-400 text-sm font-medium">
                {event.year || event.date}
              </span>
              {event.type && (
                <span className="text-xs px-2 py-0.5 bg-slate-700 rounded text-slate-400">
                  {event.type}
                </span>
              )}
            </div>
            <p className="text-slate-300">{event.event}</p>
            {event.source && (
              <p className="text-xs text-slate-500 mt-2">
                Source: {event.source}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function getEventIcon(type?: string) {
  switch (type) {
    case 'newspaper':
    case 'mention':
      return <Newspaper className="w-4 h-4 text-slate-400" />
    case 'war':
    case 'military':
      return <Scroll className="w-4 h-4 text-red-400" />
    case 'development':
      return <MapPin className="w-4 h-4 text-green-400" />
    default:
      return <Calendar className="w-4 h-4 text-slate-400" />
  }
}

function groupByEra(events: TimelineEvent[]): Record<string, TimelineEvent[]> {
  const eras: Record<string, TimelineEvent[]> = {}

  for (const event of events) {
    const era = getEra(event.year)
    if (!eras[era]) {
      eras[era] = []
    }
    eras[era].push(event)
  }

  // Sort each era's events by year
  for (const era in eras) {
    eras[era].sort((a, b) => a.year - b.year)
  }

  return eras
}

function getEra(year: number): string {
  if (year < 1700) return 'Pre-Colonial Era'
  if (year < 1776) return 'Colonial Period (1700-1776)'
  if (year < 1800) return 'Revolutionary Era (1776-1800)'
  if (year < 1865) return 'Antebellum Period (1800-1865)'
  if (year < 1900) return 'Gilded Age (1865-1900)'
  if (year < 1945) return 'Early 20th Century (1900-1945)'
  if (year < 1970) return 'Post-War Era (1945-1970)'
  return 'Modern Era (1970-Present)'
}
