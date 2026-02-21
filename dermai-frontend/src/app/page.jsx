import Navbar from '@/components/Navbar'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center">
        <div className="w-24 h-24 bg-blue-600 rounded-full flex items-center justify-center mb-6 shadow-lg">
          <span className="text-white text-4xl font-bold">D</span>
        </div>

        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Bienvenue sur <span className="text-blue-600">DermAI</span>
        </h1>

        <p className="text-lg text-gray-500 max-w-xl mb-10">
          Obtenez une première estimation du risque dermatologique grâce à
          l&apos;intelligence artificielle. Rapide, simple et accessible.
        </p>

        <Link
          href="/analyse"
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-4 rounded-full text-lg transition-colors shadow-md"
        >
          Lancer une analyse →
        </Link>

        <p className="mt-8 text-sm text-gray-400 max-w-md">
          ⚠️ Cet outil ne remplace pas un diagnostic médical. Consultez toujours
          un professionnel de santé.
        </p>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl w-full">
          {[
            {
              icon: '🖼️',
              title: "Analyse d'image",
              desc: 'Uploadez une photo de votre lésion cutanée',
            },
            {
              icon: '💬',
              title: 'Décrivez vos symptômes',
              desc: 'Douleur, démangeaison, durée...',
            },
            {
              icon: '📊',
              title: 'Score de risque',
              desc: 'Recevez un score et une recommandation claire',
            },
          ].map((card, i) => (
            <div key={i} className="bg-white rounded-2xl shadow p-6 text-center">
              <div className="text-4xl mb-3">{card.icon}</div>
              <h3 className="font-semibold text-gray-700 mb-1">{card.title}</h3>
              <p className="text-sm text-gray-400">{card.desc}</p>
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