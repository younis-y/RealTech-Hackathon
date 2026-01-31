'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

interface Recommendation {
  rank: number
  name: string
  areaCode: string
  score: number
  factors: Record<string, number>
  strengths: string[]
  weaknesses: string[]
}

interface ResultsData {
  success: boolean
  persona: string
  budget: number
  recommendations: Recommendation[]
}

export default function Results() {
  const router = useRouter()
  const [data, setData] = useState<ResultsData | null>(null)

  useEffect(() => {
    const stored = sessionStorage.getItem('recommendations')
    if (stored) {
      setData(JSON.parse(stored))
    } else {
      router.push('/')
    }
  }, [router])

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading recommendations...</p>
        </div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <button
            onClick={() => router.push('/')}
            className="text-blue-600 hover:text-blue-700 mb-4"
          >
            ← New Search
          </button>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Your Recommendations
          </h1>
          <p className="text-gray-600">
            Top areas for {data.persona}s with budget £{data.budget.toLocaleString()}/month
          </p>
        </div>

        {/* Recommendations */}
        <div className="space-y-6">
          {data.recommendations.map((rec) => (
            <div
              key={rec.rank}
              className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-shadow"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg">
                      #{rec.rank}
                    </span>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        {rec.name}
                      </h2>
                      <p className="text-gray-500">{rec.areaCode}</p>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold text-blue-600">
                    {rec.score}
                  </div>
                  <div className="text-sm text-gray-500">Overall Score</div>
                </div>
              </div>

              {/* Factor Scores */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">
                  Factor Breakdown:
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.entries(rec.factors).map(([factor, score]) => (
                    <div key={factor} className="bg-gray-50 rounded-lg p-3">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium text-gray-700 capitalize">
                          {factor}
                        </span>
                        <span className="text-sm font-bold text-gray-900">
                          {score}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            score >= 70
                              ? 'bg-green-500'
                              : score >= 50
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                          style={{ width: `${score}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Strengths and Weaknesses */}
              <div className="grid md:grid-cols-2 gap-4">
                {rec.strengths.length > 0 && (
                  <div className="bg-green-50 rounded-lg p-4">
                    <h4 className="font-semibold text-green-900 mb-2">
                      ✓ Strengths
                    </h4>
                    <ul className="space-y-1">
                      {rec.strengths.map((strength, i) => (
                        <li key={i} className="text-sm text-green-800 capitalize">
                          • {strength}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {rec.weaknesses.length > 0 && (
                  <div className="bg-red-50 rounded-lg p-4">
                    <h4 className="font-semibold text-red-900 mb-2">
                      ! Weaknesses
                    </h4>
                    <ul className="space-y-1">
                      {rec.weaknesses.map((weakness, i) => (
                        <li key={i} className="text-sm text-red-800 capitalize">
                          • {weakness}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Info Footer */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            Data from UK Police, OpenStreetMap, and AI analysis • Updated in real-time
          </p>
        </div>
      </div>
    </main>
  )
}
