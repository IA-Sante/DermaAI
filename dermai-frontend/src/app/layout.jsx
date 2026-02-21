import './globals.css'

export const metadata = {
  title: 'DermAI – Analyse dermatologique',
  description: 'Outil de pré-dépistage dermatologique par IA',
}

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body className="bg-gray-50 min-h-screen flex flex-col">{children}</body>
    </html>
  )
}