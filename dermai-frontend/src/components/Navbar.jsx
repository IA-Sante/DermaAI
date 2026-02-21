'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Navbar() {
  const pathname = usePathname()

  const links = [
    { href: '/', label: 'Accueil' },
    { href: '/analyse', label: 'Analyser' },
    { href: '/historique', label: 'Historique' },
  ]

  return (
    <nav className="bg-white shadow-md px-6 py-4 flex items-center justify-between">
      <Link href="/" className="flex items-center gap-2">
        <div className="w-9 h-9 bg-blue-600 rounded-full flex items-center justify-center">
          <span className="text-white font-bold text-sm">D</span>
        </div>
        <span className="text-xl font-bold text-blue-600">DermAI</span>
      </Link>

      <div className="flex gap-6">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`text-sm font-medium transition-colors ${
              pathname === link.href
                ? 'text-blue-600 border-b-2 border-blue-600 pb-1'
                : 'text-gray-500 hover:text-blue-600'
            }`}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}