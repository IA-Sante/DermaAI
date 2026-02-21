export default function RiskCard({ result }) {
  if (!result) return null

  const riskConfig = {
    faible: {
      color: 'bg-green-50 border-green-300',
      badge: 'bg-green-100 text-green-700',
      icon: '✅',
      label: 'Risque Faible',
    },
    modéré: {
      color: 'bg-yellow-50 border-yellow-300',
      badge: 'bg-yellow-100 text-yellow-700',
      icon: '⚠️',
      label: 'Risque Modéré',
    },
    élevé: {
      color: 'bg-red-50 border-red-300',
      badge: 'bg-red-100 text-red-700',
      icon: '🚨',
      label: 'Risque Élevé',
    },
  }

  const config = riskConfig[result.risk_level] || riskConfig.modéré
  const scorePercent = Math.round(result.score_global * 100)

  return (
    <div className={`rounded-2xl border-2 p-6 ${config.color}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{config.icon}</span>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${config.badge}`}>
            {config.label}
          </span>
        </div>
        <span className="text-3xl font-bold text-gray-700">
          {scorePercent}
          <span className="text-lg">%</span>
        </span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
        <div
          className={`h-3 rounded-full transition-all duration-700 ${
            result.risk_level === 'faible'
              ? 'bg-green-500'
              : result.risk_level === 'modéré'
                ? 'bg-yellow-500'
                : 'bg-red-500'
          }`}
          style={{ width: `${scorePercent}%` }}
        />
      </div>

      <div className="bg-white rounded-xl p-4 shadow-sm">
        <p className="text-sm font-semibold text-gray-600 mb-1">💡 Recommandation</p>
        <p className="text-sm text-gray-700 leading-relaxed">{result.recommendation}</p>
      </div>

      <p className="text-xs text-gray-400 mt-3 text-center">
        ⚠️ Ce résultat ne constitue pas un diagnostic médical.
      </p>
    </div>
  )
}