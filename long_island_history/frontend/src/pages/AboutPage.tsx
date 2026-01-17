import Header from '../components/Header'
import { Database, Shield, History, MapPin, ExternalLink } from 'lucide-react'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-950">
      <Header />

      <main className="max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-white mb-8">
          About This Project
        </h1>

        <section className="prose prose-invert max-w-none">
          <p className="text-xl text-slate-300 mb-8">
            The Long Island Historical Land Information System is a comprehensive
            research platform for discovering the deep historical connections of
            parcels of land on Long Island, New York.
          </p>

          <h2 className="text-2xl font-bold text-white mt-12 mb-4">Our Approach</h2>
          <p className="text-slate-400 mb-6">
            We believe in <strong className="text-white">strict accuracy</strong> over
            storytelling. Our system only presents verified historical records from
            authoritative sources. When no records are found, we clearly state that—we
            never fabricate or embellish history.
          </p>

          <div className="grid md:grid-cols-2 gap-6 my-8">
            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
              <Shield className="w-8 h-8 text-amber-400 mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">Verified Sources Only</h3>
              <p className="text-slate-400 text-sm">
                Every piece of historical information is sourced from government archives,
                official newspapers, and authenticated historical records.
              </p>
            </div>
            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
              <Database className="w-8 h-8 text-amber-400 mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">Deep Search</h3>
              <p className="text-slate-400 text-sm">
                Our system searches across 50+ million newspaper pages, government
                GIS databases, and historical archives to find every relevant record.
              </p>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-white mt-12 mb-4">Data Sources</h2>
          <p className="text-slate-400 mb-6">
            We integrate with the following authoritative sources:
          </p>

          <div className="space-y-4 mb-8">
            <SourceItem
              name="NYS GIS Program Office"
              description="Official New York State orthoimagery (aerial photography) from 1994 to present"
              url="https://gis.ny.gov"
            />
            <SourceItem
              name="Library of Congress - Chronicling America"
              description="Digitized historical newspapers from 1789-1963"
              url="https://chroniclingamerica.loc.gov"
            />
            <SourceItem
              name="FultonHistory (Old Fulton NY Post Cards)"
              description="50+ million pages of New York State historical newspapers"
              url="https://fultonhistory.com"
            />
            <SourceItem
              name="Suffolk County GIS"
              description="Official parcel data, property boundaries, and tax records"
              url="https://gis.suffolkcountyny.gov"
            />
            <SourceItem
              name="Nassau County GIS"
              description="Official parcel data and property information"
              url="https://www.nassaucountyny.gov/gis"
            />
            <SourceItem
              name="USGS National Map"
              description="Historical topographic maps dating back to the 1890s"
              url="https://www.usgs.gov/programs/national-geospatial-program/national-map"
            />
            <SourceItem
              name="Library of Congress - Sanborn Maps"
              description="Fire insurance maps showing building details (1867-1970)"
              url="https://www.loc.gov/collections/sanborn-maps"
            />
          </div>

          <h2 className="text-2xl font-bold text-white mt-12 mb-4">Coverage Area</h2>
          <p className="text-slate-400 mb-6">
            This system covers <strong className="text-white">Long Island, New York</strong> exclusively, including:
          </p>
          <ul className="list-disc list-inside text-slate-400 space-y-2 mb-8">
            <li>Suffolk County (eastern Long Island)</li>
            <li>Nassau County (western Long Island)</li>
            <li>Historical Queens County territory</li>
            <li>Historical Kings County (Brooklyn) territory</li>
          </ul>

          <h2 className="text-2xl font-bold text-white mt-12 mb-4">Historical Periods</h2>
          <p className="text-slate-400 mb-6">
            Our research spans from pre-colonial times to the present:
          </p>

          <div className="space-y-4 mb-8">
            <PeriodItem
              period="Pre-Contact Era"
              years="Before 1624"
              description="Home to the Metoac Confederation including Shinnecock, Montaukett, and other Algonquian peoples"
            />
            <PeriodItem
              period="Colonial Period"
              years="1624-1776"
              description="Dutch and English settlements, establishment of townships"
            />
            <PeriodItem
              period="Revolutionary War"
              years="1776-1783"
              description="Battle of Long Island, British occupation, Culper Spy Ring"
            />
            <PeriodItem
              period="19th Century"
              years="1800-1900"
              description="Agricultural economy, whaling industry, railroad expansion"
            />
            <PeriodItem
              period="Gold Coast Era"
              years="1890-1940"
              description="Gilded Age estates, aviation pioneers"
            />
            <PeriodItem
              period="World Wars"
              years="1914-1945"
              description="Military installations, aviation industry"
            />
            <PeriodItem
              period="Post-War Era"
              years="1945-1970"
              description="Levittown and mass suburbanization"
            />
            <PeriodItem
              period="Modern Era"
              years="1970-Present"
              description="Contemporary development and preservation"
            />
          </div>

          <h2 className="text-2xl font-bold text-white mt-12 mb-4">AI Synthesis</h2>
          <p className="text-slate-400 mb-6">
            When generating historical reports, our AI system follows strict guidelines:
          </p>
          <ul className="list-disc list-inside text-slate-400 space-y-2 mb-8">
            <li>Only uses information from verified sources</li>
            <li>Never fabricates or embellishes facts</li>
            <li>Always cites sources for claims</li>
            <li>Clearly states when information is missing</li>
            <li>Identifies gaps in the historical record</li>
            <li>Recommends additional research avenues</li>
          </ul>

          <h2 className="text-2xl font-bold text-white mt-12 mb-4">Limitations</h2>
          <p className="text-slate-400 mb-6">
            While comprehensive, this system has limitations:
          </p>
          <ul className="list-disc list-inside text-slate-400 space-y-2 mb-8">
            <li>Pre-digital records (before ~1980) may not be fully available online</li>
            <li>Some local newspaper archives are not yet digitized</li>
            <li>Physical deed records at county clerk offices may contain additional information</li>
            <li>Local historical society collections may not be indexed</li>
          </ul>

          <div className="p-6 bg-amber-500/10 border border-amber-500/30 rounded-xl mt-12">
            <h3 className="text-lg font-semibold text-amber-400 mb-2">
              Disclaimer
            </h3>
            <p className="text-slate-400 text-sm">
              This system is for informational and research purposes only. It does not
              constitute a professional title search, historical survey, or legal document.
              For official property records, please consult the relevant county clerk's office.
            </p>
          </div>
        </section>
      </main>
    </div>
  )
}

function SourceItem({ name, description, url }: { name: string, description: string, url: string }) {
  return (
    <div className="p-4 bg-slate-800/30 border border-slate-700/50 rounded-lg">
      <div className="flex items-start justify-between">
        <div>
          <h4 className="font-semibold text-white">{name}</h4>
          <p className="text-slate-400 text-sm mt-1">{description}</p>
        </div>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-amber-400 hover:text-amber-300 p-1"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  )
}

function PeriodItem({ period, years, description }: { period: string, years: string, description: string }) {
  return (
    <div className="flex gap-4">
      <div className="w-32 flex-shrink-0">
        <span className="text-amber-400 text-sm font-medium">{years}</span>
      </div>
      <div>
        <h4 className="font-semibold text-white">{period}</h4>
        <p className="text-slate-400 text-sm">{description}</p>
      </div>
    </div>
  )
}
