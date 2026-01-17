import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapPin, Search, History, Layers, Clock, ChevronRight } from 'lucide-react'
import Header from '../components/Header'

export default function HomePage() {
  const navigate = useNavigate()
  const [address, setAddress] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (address.trim()) {
      navigate(`/research?address=${encodeURIComponent(address.trim())}`)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-950">
      <Header />

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23c9a227' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 py-24">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Discover Your Land's
              <span className="block text-amber-400 mt-2">Deep History</span>
            </h1>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto mb-12">
              Uncover the hidden stories of Long Island properties through aerial imagery,
              historical archives, and AI-powered research spanning centuries.
            </p>

            {/* Search Box */}
            <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
              <div className="relative">
                <input
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Enter a Long Island address..."
                  className="w-full px-6 py-5 pl-14 text-lg bg-slate-800/80 border border-slate-600
                             rounded-2xl text-white placeholder-slate-400
                             focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20
                             focus:outline-none transition-all duration-200"
                />
                <MapPin className="absolute left-5 top-1/2 -translate-y-1/2 w-6 h-6 text-slate-400" />
                <button
                  type="submit"
                  className="absolute right-3 top-1/2 -translate-y-1/2 px-6 py-3
                             bg-amber-500 hover:bg-amber-600 text-slate-900 font-semibold
                             rounded-xl transition-colors duration-200 flex items-center gap-2"
                >
                  <Search className="w-5 h-5" />
                  Research
                </button>
              </div>
            </form>

            <p className="text-slate-500 mt-4">
              Covering Suffolk County, Nassau County, and all of Long Island
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-white text-center mb-16">
            Comprehensive Historical Research
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Layers className="w-8 h-8 text-amber-400" />}
              title="Aerial Imagery"
              description="Access NYS orthoimagery from 1994 to present, plus USGS historical topographic maps dating back to the 1890s."
            />
            <FeatureCard
              icon={<History className="w-8 h-8 text-amber-400" />}
              title="Deep Archives"
              description="Search 50+ million pages of historical newspapers, deeds, and records from the Library of Congress and FultonHistory."
            />
            <FeatureCard
              icon={<Clock className="w-8 h-8 text-amber-400" />}
              title="Historical Context"
              description="Understand how wars, development, and major events shaped your land from pre-colonial times to present."
            />
          </div>
        </div>
      </section>

      {/* Data Sources Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-white text-center mb-8">
            Powered by Verified Sources
          </h2>
          <p className="text-slate-400 text-center max-w-2xl mx-auto mb-16">
            We search only authoritative government and archival sources.
            No storytelling or fabrication—just documented history.
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <SourceCard
              name="NYS GIS Clearinghouse"
              type="Aerial Imagery"
              description="Official NY State orthoimagery"
            />
            <SourceCard
              name="Library of Congress"
              type="Historical Archives"
              description="Chronicling America newspapers"
            />
            <SourceCard
              name="FultonHistory"
              type="NY Newspapers"
              description="50 million+ pages of NY history"
            />
            <SourceCard
              name="County GIS Portals"
              type="Parcel Data"
              description="Suffolk & Nassau property records"
            />
          </div>
        </div>
      </section>

      {/* Historical Periods */}
      <section className="py-24 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-white text-center mb-16">
            Explore Long Island Through Time
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <PeriodCard
              period="Pre-Contact"
              years="Before 1624"
              description="Metoac, Shinnecock, and Montaukett territories"
            />
            <PeriodCard
              period="Colonial Era"
              years="1624-1776"
              description="Dutch and English settlements"
            />
            <PeriodCard
              period="Revolutionary"
              years="1776-1783"
              description="Battle of Long Island and British occupation"
            />
            <PeriodCard
              period="Gold Coast"
              years="1890-1940"
              description="Estate era and aviation pioneers"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Discover Your Land's Story?
          </h2>
          <p className="text-xl text-slate-300 mb-10">
            Enter any Long Island address to begin your historical research journey.
          </p>
          <button
            onClick={() => document.querySelector('input')?.focus()}
            className="px-8 py-4 bg-amber-500 hover:bg-amber-600 text-slate-900
                       font-bold text-lg rounded-xl transition-colors duration-200
                       flex items-center gap-2 mx-auto"
          >
            Start Researching
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-slate-400">
              Long Island Historical Land Information System
            </div>
            <div className="text-slate-500 text-sm">
              Data sourced from government archives and historical societies
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="p-8 bg-slate-800/50 border border-slate-700 rounded-2xl hover:border-amber-500/50 transition-colors duration-200">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </div>
  )
}

function SourceCard({ name, type, description }: { name: string, type: string, description: string }) {
  return (
    <div className="p-6 bg-slate-800/30 border border-slate-700/50 rounded-xl">
      <div className="text-amber-400 text-sm font-medium mb-1">{type}</div>
      <h3 className="text-white font-semibold mb-2">{name}</h3>
      <p className="text-slate-500 text-sm">{description}</p>
    </div>
  )
}

function PeriodCard({ period, years, description }: { period: string, years: string, description: string }) {
  return (
    <div className="p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50
                    border border-slate-700 rounded-xl group hover:border-amber-500/50
                    transition-colors duration-200 cursor-pointer">
      <div className="text-amber-400 text-sm font-medium mb-1">{years}</div>
      <h3 className="text-xl font-semibold text-white mb-2">{period}</h3>
      <p className="text-slate-400 text-sm">{description}</p>
    </div>
  )
}
