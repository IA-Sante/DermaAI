import Navbar from '@/components/Navbar'

export default function Resultats() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-700 mb-2">Page Résultats</h1>
          <p className="text-gray-400">Sprint 2 – En cours de développement</p>
        </div>
      </main>
    </div>
  )
}