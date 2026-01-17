import { X, Download, Calendar, MapPin, FileText, AlertTriangle, Lightbulb } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface ReportViewProps {
  report: any
  onClose: () => void
}

export default function ReportView({ report, onClose }: ReportViewProps) {
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="w-full max-w-4xl max-h-[90vh] bg-slate-900 rounded-2xl border border-slate-700
                     overflow-hidden flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-700">
            <div>
              <h2 className="text-2xl font-bold text-white">Historical Research Report</h2>
              <p className="text-slate-400 mt-1">{report.property_address}</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  // Download functionality
                  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `history-report-${Date.now()}.json`
                  a.click()
                }}
                className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg"
              >
                <Download className="w-5 h-5" />
              </button>
              <button
                onClick={onClose}
                className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {/* Confidence Level */}
            <div className={`mb-6 p-4 rounded-lg border ${getConfidenceStyle(report.confidence_level)}`}>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-medium">Confidence Level:</span>
                <span className="font-bold capitalize">{report.confidence_level}</span>
              </div>
              <p className="text-sm opacity-80">
                {getConfidenceDescription(report.confidence_level)}
              </p>
            </div>

            {/* Executive Summary */}
            <section className="mb-8">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <FileText className="w-5 h-5 text-amber-400" />
                Executive Summary
              </h3>
              <p className="text-slate-300 leading-relaxed">
                {report.executive_summary}
              </p>
            </section>

            {/* Key Findings */}
            {report.key_findings && report.key_findings.length > 0 && (
              <section className="mb-8">
                <h3 className="text-lg font-semibold text-white mb-3">Key Findings</h3>
                <ul className="space-y-2">
                  {report.key_findings.map((finding: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-slate-300">
                      <span className="text-amber-400 mt-1">•</span>
                      <span>{finding}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Timeline */}
            {report.timeline && report.timeline.length > 0 && (
              <section className="mb-8">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-amber-400" />
                  Historical Timeline
                </h3>
                <div className="relative pl-8">
                  <div className="timeline-line" />
                  {report.timeline.map((item: any, i: number) => (
                    <div key={i} className="relative mb-4 pb-4 border-b border-slate-800 last:border-0">
                      <div className="timeline-dot" style={{ top: '4px' }} />
                      <div className="ml-4">
                        <span className="text-amber-400 text-sm font-medium">
                          {item.year || item.date}
                        </span>
                        <p className="text-slate-300 mt-1">{item.event}</p>
                        {item.source && (
                          <p className="text-slate-500 text-xs mt-1">
                            Source: {item.source}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Historical Context */}
            {report.historical_context && (
              <section className="mb-8">
                <h3 className="text-lg font-semibold text-white mb-3">Historical Context</h3>
                <p className="text-slate-300 leading-relaxed">
                  {report.historical_context}
                </p>
              </section>
            )}

            {/* Notable Events */}
            {report.notable_events && report.notable_events.length > 0 && (
              <section className="mb-8">
                <h3 className="text-lg font-semibold text-white mb-3">Notable Events</h3>
                <div className="space-y-3">
                  {report.notable_events.map((event: any, i: number) => (
                    <div key={i} className="p-4 bg-slate-800/50 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-amber-400 font-medium">{event.date || event.year}</span>
                        <span className="text-white font-medium">{event.name}</span>
                      </div>
                      <p className="text-slate-400 text-sm">{event.description}</p>
                      {event.relevance && (
                        <p className="text-slate-500 text-xs mt-2 italic">{event.relevance}</p>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Land Use History */}
            {report.land_use_history && (
              <section className="mb-8">
                <h3 className="text-lg font-semibold text-white mb-3">Land Use History</h3>
                <p className="text-slate-300 leading-relaxed">
                  {report.land_use_history}
                </p>
              </section>
            )}

            {/* Data Gaps */}
            {report.data_gaps && report.data_gaps.length > 0 && (
              <section className="mb-8">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-yellow-500" />
                  Gaps in Historical Record
                </h3>
                <ul className="space-y-2">
                  {report.data_gaps.map((gap: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-slate-400">
                      <span className="text-yellow-500 mt-1">•</span>
                      <span>{gap}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Recommendations */}
            {report.recommendations_for_further_research &&
              report.recommendations_for_further_research.length > 0 && (
              <section className="mb-8">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-amber-400" />
                  Recommendations for Further Research
                </h3>
                <ul className="space-y-2">
                  {report.recommendations_for_further_research.map((rec: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-slate-300">
                      <span className="text-amber-400 mt-1">→</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Sources */}
            {report.sources_cited && report.sources_cited.length > 0 && (
              <section className="mb-8">
                <h3 className="text-lg font-semibold text-white mb-3">Sources Cited</h3>
                <div className="flex flex-wrap gap-2">
                  {report.sources_cited.map((source: string, i: number) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-slate-800 rounded-full text-sm text-slate-300"
                    >
                      {source}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {/* Disclaimer */}
            {report.disclaimer && (
              <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700 text-sm text-slate-400">
                <strong className="text-slate-300">Disclaimer:</strong> {report.disclaimer}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

function getConfidenceStyle(level: string): string {
  switch (level) {
    case 'high':
      return 'bg-green-500/10 border-green-500/30 text-green-400'
    case 'medium':
      return 'bg-amber-500/10 border-amber-500/30 text-amber-400'
    case 'low':
      return 'bg-orange-500/10 border-orange-500/30 text-orange-400'
    case 'insufficient_data':
    default:
      return 'bg-red-500/10 border-red-500/30 text-red-400'
  }
}

function getConfidenceDescription(level: string): string {
  switch (level) {
    case 'high':
      return 'Multiple corroborating sources found for this property.'
    case 'medium':
      return 'Several sources found, but some gaps in the historical record.'
    case 'low':
      return 'Limited sources found. Physical records may contain more information.'
    case 'insufficient_data':
    default:
      return 'No historical records found in digital archives. Visit county offices for physical records.'
  }
}
