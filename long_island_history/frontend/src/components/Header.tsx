import { Link } from 'react-router-dom'
import { Map, Menu, X } from 'lucide-react'
import { useState } from 'react'

interface HeaderProps {
  compact?: boolean
}

export default function Header({ compact = false }: HeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className={`bg-slate-900/80 backdrop-blur-md border-b border-slate-800 ${
      compact ? 'py-2' : 'py-4'
    }`}>
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-500/20 rounded-lg flex items-center justify-center">
              <Map className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <h1 className={`font-bold text-white ${compact ? 'text-lg' : 'text-xl'}`}>
                Long Island History
              </h1>
              {!compact && (
                <p className="text-xs text-slate-400">Historical Land Research</p>
              )}
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <Link
              to="/"
              className="text-slate-300 hover:text-white transition-colors"
            >
              Home
            </Link>
            <Link
              to="/research"
              className="text-slate-300 hover:text-white transition-colors"
            >
              Research
            </Link>
            <Link
              to="/about"
              className="text-slate-300 hover:text-white transition-colors"
            >
              About
            </Link>
          </nav>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 text-slate-400 hover:text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <nav className="md:hidden py-4 border-t border-slate-800 mt-4">
            <div className="flex flex-col gap-4">
              <Link
                to="/"
                className="text-slate-300 hover:text-white transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Home
              </Link>
              <Link
                to="/research"
                className="text-slate-300 hover:text-white transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Research
              </Link>
              <Link
                to="/about"
                className="text-slate-300 hover:text-white transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                About
              </Link>
            </div>
          </nav>
        )}
      </div>
    </header>
  )
}
