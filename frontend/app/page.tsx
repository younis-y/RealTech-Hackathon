'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    persona: 'student',
    budget: 1000,
    locationType: 'rent',
    destination: 'UCL',
    maxAreas: 5
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await fetch('/api/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      // Store results in sessionStorage and navigate
      sessionStorage.setItem('recommendations', JSON.stringify(data))
      router.push('/results')
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to get recommendations. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Veo
          </h1>
          <p className="text-xl text-gray-600">
            AI-Powered Housing Recommendations for London
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Persona Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                I am a...
              </label>
              <select
                value={formData.persona}
                onChange={(e) => setFormData({ ...formData, persona: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="student">Student</option>
                <option value="parent">Parent</option>
                <option value="developer">Property Developer</option>
              </select>
            </div>

            {/* Budget */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Budget (£/month)
              </label>
              <input
                type="number"
                value={formData.budget}
                onChange={(e) => setFormData({ ...formData, budget: parseInt(e.target.value) })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min="500"
                max="5000"
                step="50"
              />
            </div>

            {/* Location Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Looking to...
              </label>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="rent"
                    checked={formData.locationType === 'rent'}
                    onChange={(e) => setFormData({ ...formData, locationType: e.target.value })}
                    className="mr-2"
                  />
                  Rent
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="buy"
                    checked={formData.locationType === 'buy'}
                    onChange={(e) => setFormData({ ...formData, locationType: e.target.value })}
                    className="mr-2"
                  />
                  Buy
                </label>
              </div>
            </div>

            {/* Destination */}
            {formData.persona === 'student' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  University/Destination
                </label>
                <select
                  value={formData.destination}
                  onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="UCL">UCL (University College London)</option>
                  <option value="Imperial">Imperial College London</option>
                  <option value="KCL">King's College London</option>
                  <option value="LSE">London School of Economics</option>
                </select>
              </div>
            )}

            {/* Max Areas */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of recommendations: {formData.maxAreas}
              </label>
              <input
                type="range"
                value={formData.maxAreas}
                onChange={(e) => setFormData({ ...formData, maxAreas: parseInt(e.target.value) })}
                className="w-full"
                min="3"
                max="10"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-4 px-6 rounded-lg font-semibold text-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Finding recommendations...' : 'Get Recommendations'}
            </button>
          </form>

          {/* Info */}
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>Powered by AI • Real London data • Transparent scoring</p>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-3 gap-4 mt-8 text-center">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-2xl mb-2">🏘️</div>
            <div className="text-sm font-medium">Real Data</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-2xl mb-2">🤖</div>
            <div className="text-sm font-medium">AI Explanations</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-2xl mb-2">📊</div>
            <div className="text-sm font-medium">Transparent Scores</div>
          </div>
        </div>
      </div>
    </main>
  )
}
