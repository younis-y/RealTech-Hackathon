'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

interface FormData {
  persona: 'student' | 'parent' | 'developer'
  budget: number
  locationType: 'rent' | 'buy'
  destination: string
  // Conditional fields
  minBedrooms?: number
  schoolProximity?: boolean
  targetYield?: number
  propertyCondition?: 'any' | 'turnkey' | 'renovation'
}

export default function Home() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState<FormData>({
    persona: 'student',
    budget: 1500,
    locationType: 'rent',
    destination: 'UCL',
    minBedrooms: 2,
    schoolProximity: true,
    targetYield: 5,
    propertyCondition: 'any'
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await fetch('/api/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          maxAreas: 5 // Default to 5 results
        })
      })

      const data = await response.json()
      sessionStorage.setItem('recommendations', JSON.stringify(data))
      router.push('/results')
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to get recommendations. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Format budget display
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  // Dynamic budget config based on rent/buy
  const budgetConfig = formData.locationType === 'rent'
    ? { label: 'Max Monthly Rent', min: 800, max: 4000, step: 100, suffix: '/mo' }
    : { label: 'Max Property Price', min: 200000, max: 1500000, step: 25000, suffix: '' }

  return (
    <main className="min-h-screen bg-slate-50 py-8 px-4">
      <div className="max-w-xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight mb-1">
            Veo
          </h1>
          <p className="text-slate-500 text-sm">
            AI-Powered London Property Matching
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white border border-slate-200 p-6">
          <form onSubmit={handleSubmit} className="space-y-5">

            {/* RENT / BUY Toggle - TOP, PROMINENT */}
            <div>
              <div className="grid grid-cols-2 gap-0 border border-slate-200 rounded-none overflow-hidden">
                <button
                  type="button"
                  onClick={() => setFormData({
                    ...formData,
                    locationType: 'rent',
                    budget: 1500 // Reset to sensible rent default
                  })}
                  className={`py-3 text-sm font-semibold uppercase tracking-wider transition-all ${formData.locationType === 'rent'
                      ? 'bg-slate-900 text-white'
                      : 'bg-white text-slate-500 hover:bg-slate-50'
                    }`}
                >
                  Rent
                </button>
                <button
                  type="button"
                  onClick={() => setFormData({
                    ...formData,
                    locationType: 'buy',
                    budget: 450000 // Reset to sensible buy default
                  })}
                  className={`py-3 text-sm font-semibold uppercase tracking-wider transition-all ${formData.locationType === 'buy'
                      ? 'bg-slate-900 text-white'
                      : 'bg-white text-slate-500 hover:bg-slate-50'
                    }`}
                >
                  Buy
                </button>
              </div>
            </div>

            {/* Persona Selection - Visual Cards */}
            <div>
              <label className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider mb-2">
                I am a...
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: 'student', icon: '🎓', label: 'Student' },
                  { id: 'parent', icon: '👨‍👩‍👧', label: 'Parent' },
                  { id: 'developer', icon: '🏢', label: 'Developer' }
                ].map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, persona: p.id as FormData['persona'] })}
                    className={`py-3 px-2 border text-center transition-all ${formData.persona === p.id
                        ? 'border-slate-900 bg-slate-50'
                        : 'border-slate-200 hover:border-slate-300'
                      }`}
                  >
                    <div className="text-xl mb-1">{p.icon}</div>
                    <div className={`text-xs font-medium ${formData.persona === p.id ? 'text-slate-900' : 'text-slate-500'
                      }`}>
                      {p.label}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Budget - with £ icon and dynamic label */}
            <div>
              <label className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider mb-2">
                {budgetConfig.label}
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-lg font-medium">
                  £
                </span>
                <input
                  type="text"
                  value={formData.budget.toLocaleString()}
                  onChange={(e) => {
                    const val = parseInt(e.target.value.replace(/,/g, '')) || 0
                    setFormData({ ...formData, budget: Math.min(budgetConfig.max, Math.max(budgetConfig.min, val)) })
                  }}
                  className="w-full pl-8 pr-12 py-3 border border-slate-200 text-lg font-semibold text-slate-900 focus:outline-none focus:border-slate-400"
                />
                {budgetConfig.suffix && (
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">
                    {budgetConfig.suffix}
                  </span>
                )}
              </div>
              {/* Budget quick buttons */}
              <div className="flex gap-2 mt-2">
                {(formData.locationType === 'rent'
                  ? [1000, 1500, 2000, 2500]
                  : [300000, 450000, 600000, 800000]
                ).map((val) => (
                  <button
                    key={val}
                    type="button"
                    onClick={() => setFormData({ ...formData, budget: val })}
                    className={`flex-1 py-1.5 text-xs border transition-all ${formData.budget === val
                        ? 'border-slate-900 bg-slate-900 text-white'
                        : 'border-slate-200 text-slate-500 hover:border-slate-300'
                      }`}
                  >
                    {formatCurrency(val)}
                  </button>
                ))}
              </div>
            </div>

            {/* CONDITIONAL FIELDS based on persona */}

            {/* Student: University destination */}
            {formData.persona === 'student' && (
              <div>
                <label className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider mb-2">
                  University / Workplace
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">📍</span>
                  <select
                    value={formData.destination}
                    onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                    className="w-full pl-9 pr-4 py-3 border border-slate-200 text-slate-900 focus:outline-none focus:border-slate-400 appearance-none bg-white"
                  >
                    <option value="UCL">UCL (University College London)</option>
                    <option value="Imperial">Imperial College London</option>
                    <option value="KCL">King's College London</option>
                    <option value="LSE">London School of Economics</option>
                    <option value="Queen Mary">Queen Mary University</option>
                    <option value="City">City, University of London</option>
                  </select>
                </div>
              </div>
            )}

            {/* Parent: Bedrooms + School Proximity */}
            {formData.persona === 'parent' && (
              <>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider mb-2">
                      Min Bedrooms
                    </label>
                    <div className="flex border border-slate-200">
                      {[1, 2, 3, 4].map((num) => (
                        <button
                          key={num}
                          type="button"
                          onClick={() => setFormData({ ...formData, minBedrooms: num })}
                          className={`flex-1 py-2.5 text-sm font-medium transition-all ${formData.minBedrooms === num
                              ? 'bg-slate-900 text-white'
                              : 'bg-white text-slate-500 hover:bg-slate-50'
                            }`}
                        >
                          {num}+
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider mb-2">
                      Good Schools Nearby
                    </label>
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, schoolProximity: !formData.schoolProximity })}
                      className={`w-full py-2.5 text-sm font-medium border transition-all ${formData.schoolProximity
                          ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                          : 'border-slate-200 bg-white text-slate-500'
                        }`}
                    >
                      {formData.schoolProximity ? '✓ Required' : 'Not Required'}
                    </button>
                  </div>
                </div>
              </>
            )}

            {/* Developer: Yield Target + Property Condition */}
            {formData.persona === 'developer' && (
              <>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider mb-2">
                      Target Yield (%)
                    </label>
                    <div className="flex border border-slate-200">
                      {[4, 5, 6, 7].map((num) => (
                        <button
                          key={num}
                          type="button"
                          onClick={() => setFormData({ ...formData, targetYield: num })}
                          className={`flex-1 py-2.5 text-sm font-medium transition-all ${formData.targetYield === num
                              ? 'bg-slate-900 text-white'
                              : 'bg-white text-slate-500 hover:bg-slate-50'
                            }`}
                        >
                          {num}%+
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider mb-2">
                      Condition
                    </label>
                    <select
                      value={formData.propertyCondition}
                      onChange={(e) => setFormData({ ...formData, propertyCondition: e.target.value as FormData['propertyCondition'] })}
                      className="w-full py-2.5 px-3 border border-slate-200 text-sm text-slate-700 focus:outline-none focus:border-slate-400 appearance-none bg-white"
                    >
                      <option value="any">Any Condition</option>
                      <option value="turnkey">Turnkey Ready</option>
                      <option value="renovation">Needs Work</option>
                    </select>
                  </div>
                </div>
              </>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-slate-900 text-white py-3.5 text-sm font-semibold uppercase tracking-wider hover:bg-slate-800 transition-colors disabled:bg-slate-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></span>
                  Finding Properties...
                </>
              ) : (
                <>Find My Properties →</>
              )}
            </button>

            {/* Micro-copy */}
            <p className="text-center text-[10px] text-slate-400 uppercase tracking-wider">
              Free • No account required • Instant results
            </p>
          </form>
        </div>

        {/* Trust badges */}
        <div className="flex justify-center gap-6 mt-6 text-[10px] text-slate-400 uppercase tracking-wider">
          <span>🔒 Secure</span>
          <span>📊 Real Data</span>
          <span>🤖 AI-Powered</span>
        </div>

        {/* Fun Fact / Loading Easter Egg */}
        <div className="mt-8 p-4 bg-white border border-slate-200">
          <p className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Did you know?</p>
          <p className="text-xs text-slate-600">
            23-24 Leinster Gardens in Bayswater looks like two grand terraced houses — but they're fake!
            Just 5-foot thick brick facades built in the 1860s to hide Underground ventilation shafts.
            The windows are painted on!
          </p>
        </div>
      </div>
    </main>
  )
}
