'use client'
import Navbar from '@/components/Navbar'

const MOCK_HISTORY = [
  {
    id: 1,
    date: '2025-01-15',
    risk_level: 'faible',
    score: 0.22,
    classe: 'Naevus',
  },
  {
    id: 2,
    date: '2025-01-20',
    risk_level: 'modéré',
    score: 0.55,
    classe: 'Kératose',
  },
  {
    id: 3,
    date: '2025-01-28',
    risk_level: 'élevé',
    score: 0.81,
    classe: 'Mélanome',
  },
]

const badgeColor = {
  faible: 'bg-green-100 text-green-700',
  modéré: 'bg-yellow-100 text-yellow-700',
  élevé: 'bg-red-100 text-red-700',
}

export default function Historique() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      <main className="flex-1 max-w-2xl w-full mx-auto px-4 py-10">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">📋 Historique</h1>
        <p className="text-gray-500 mb-8">Vos analyses précédentes.</p>

        <div className="space-y-4">
          {MOCK_HISTORY.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl shadow p-5 flex items-center justify-between"
            >
              <div>
                <p className="font-semibold text-gray-700">{item.classe}</p>
                <p className="text-sm text-gray-400">{item.date}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-lg font-bold text-gray-600">
                  {Math.round(item.score * 100)}%
                </span>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-semibold ${badgeColor[item.risk_level]}`}
                >
                  {item.risk_level}
                </span>
              </div>
            </div>
          ))}
        </div>
      </main>

      <footer className="text-center py-4 text-sm text-gray-400 border-t">
        © 2025 DermAI – Projet académique
      </footer>
    </div>
  )
}