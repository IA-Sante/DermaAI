'use client'

export default function SymptomsForm({ symptoms, onChange }) {
  const handleChange = (field, value) => {
    onChange({ ...symptoms, [field]: value })
  }

  return (
    <div className="w-full space-y-5">
      <label className="block text-sm font-semibold text-gray-700">
        💬 Description des symptômes
      </label>

      <div>
        <label className="block text-sm text-gray-600 mb-1">
          ⏱️ Depuis combien de temps ?
        </label>
        <select
          value={symptoms.duration}
          onChange={(e) => handleChange('duration', e.target.value)}
          className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">-- Sélectionner --</option>
          <option value="less_week">Moins d&apos;une semaine</option>
          <option value="one_month">1 à 4 semaines</option>
          <option value="three_months">1 à 3 mois</option>
          <option value="more_three">Plus de 3 mois</option>
        </select>
      </div>

      <div>
        <label className="block text-sm text-gray-600 mb-2">😣 Niveau de douleur</label>
        <div className="flex gap-2">
          {[
            { value: 'none', label: '😌 Aucune' },
            { value: 'mild', label: '😐 Légère' },
            { value: 'moderate', label: '😟 Modérée' },
            { value: 'severe', label: '😫 Intense' },
          ].map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => handleChange('pain', opt.value)}
              className={`flex-1 py-2 px-1 rounded-xl text-xs font-medium border transition-colors
                ${
                  symptoms.pain === opt.value
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
                }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm text-gray-600 mb-2">🔍 Autres symptômes</label>
        <div className="grid grid-cols-2 gap-3">
          {[
            { field: 'itching', emoji: '🔴', label: 'Démangeaisons' },
            { field: 'bleeding', emoji: '🩸', label: 'Saignement' },
            { field: 'growing', emoji: '📈', label: 'En croissance' },
            { field: 'changing', emoji: '🔄', label: "Change d'aspect" },
          ].map((item) => (
            <label
              key={item.field}
              className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-colors
                ${
                  symptoms[item.field]
                    ? 'bg-blue-50 border-blue-400'
                    : 'bg-white border-gray-300 hover:border-blue-300'
                }`}
            >
              <input
                type="checkbox"
                checked={symptoms[item.field] || false}
                onChange={(e) => handleChange(item.field, e.target.checked)}
                className="accent-blue-600 w-4 h-4"
              />
              <span className="text-sm text-gray-700">
                {item.emoji} {item.label}
              </span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm text-gray-600 mb-1">
          📝 Informations complémentaires (optionnel)
        </label>
        <textarea
          value={symptoms.description}
          onChange={(e) => handleChange('description', e.target.value)}
          placeholder="Ex : la tache est apparue après un coup de soleil, elle est de couleur brune..."
          rows={3}
          className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
        />
      </div>
    </div>
  )
}