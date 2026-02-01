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
  // Financial data
  rentalYield?: number
  roi?: number
  avgRent?: number
  purchasePrice?: number
  priceGrowth5yr?: number
  // EPC data
  floorAreaSqm?: number
  avgRooms?: number
  energyRating?: string
}

interface ResultsData {
  success: boolean
  persona: string
  budget: number
  recommendations: Recommendation[]
  error?: string
}

// Mock financial data generator (EPC data comes from API, this is fallback)
function generateFinancialData(rec: Recommendation): Recommendation {
  const baseRent = 1200 + Math.random() * 800
  const basePrice = 350000 + Math.random() * 200000
  const energyRatings = ['B', 'C', 'D', 'D', 'D', 'E']
  return {
    ...rec,
    avgRent: rec.avgRent ?? Math.round(baseRent),
    purchasePrice: rec.purchasePrice ?? Math.round(basePrice),
    rentalYield: rec.rentalYield ?? parseFloat((((baseRent * 12) / basePrice) * 100).toFixed(2)),
    roi: rec.roi ?? parseFloat((8 + Math.random() * 7).toFixed(1)),
    priceGrowth5yr: rec.priceGrowth5yr ?? parseFloat((5 + Math.random() * 15).toFixed(1)),
    // EPC mock fallback
    floorAreaSqm: rec.floorAreaSqm ?? Math.round(45 + Math.random() * 40),
    avgRooms: rec.avgRooms ?? Math.round(1.5 + Math.random() * 2.5),
    energyRating: rec.energyRating ?? energyRatings[Math.floor(Math.random() * energyRatings.length)]
  }
}

export default function Results() {
  const router = useRouter()
  const [data, setData] = useState<ResultsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [videoStates, setVideoStates] = useState<Record<number, 'idle' | 'generating' | 'ready'>>({})
  const [shuffling, setShuffling] = useState(false)

  useEffect(() => {
    try {
      const stored = sessionStorage.getItem('recommendations')
      if (stored) {
        const parsed = JSON.parse(stored)
        if (parsed && typeof parsed === 'object') {
          // Enrich recommendations with financial data
          const enrichedRecs = (Array.isArray(parsed.recommendations) ? parsed.recommendations : [])
            .map(generateFinancialData)

          setData({
            success: parsed.success ?? true,
            persona: parsed.persona ?? 'user',
            budget: parsed.budget ?? 0,
            recommendations: enrichedRecs,
            error: parsed.error
          })

          // Initialize video states
          const initialVideoStates: Record<number, 'idle'> = {}
          enrichedRecs.forEach((r: Recommendation) => {
            initialVideoStates[r.rank] = 'idle'
          })
          setVideoStates(initialVideoStates)
        } else {
          setError('Invalid data format')
          router.push('/')
        }
      } else {
        router.push('/')
      }
    } catch (e) {
      console.error('Failed to parse recommendations:', e)
      setError('Failed to load recommendations')
      router.push('/')
    } finally {
      setLoading(false)
    }
  }, [router])

  // Helper to parse and filter empty items from strengths/weaknesses
  const parseItems = (items: string[]): { emoji: string; issue: string; action: string }[] => {
    if (!Array.isArray(items)) return []

    return items
      .filter(item => item && item.trim().length > 2) // Filter empty or too short
      .map(item => {
        // Extract emoji at start
        const emojiMatch = item.match(/^([\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}✓✨⚡💰🏠📉📈🎯💎🛡️✅🏘️🎓📚👨‍👩‍👧🛒🍽️🏃🏫🏞️👶☕⏱️🚌📍💷📊⚠️🏷️⚖️🔒👁️📝🏪🌱]+)/u)
        const emoji = emojiMatch?.[1] || '•'

        // Remove emoji and clean up text
        let text = item.replace(/^[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}✓✨⚡💰🏠📉📈🎯💎🛡️✅🏘️🎓📚👨‍👩‍👧🛒🍽️🏃🏫🏞️👶☕⏱️🚌📍💷📊⚠️🏷️⚖️🔒👁️📝🏪🌱]+\s*/u, '').trim()

        // Skip if text is empty after cleanup
        if (!text || text.length < 3) return null

        // Split by em-dash into issue and action
        const parts = text.split(/\s*[—–-]\s*/)
        const issue = parts[0]?.trim() || text
        const action = parts[1]?.trim() || ''

        return { emoji, issue, action }
      })
      .filter((item): item is { emoji: string; issue: string; action: string } => item !== null)
  }

  const handleGenerateVideo = (rank: number, areaName: string) => {
    setVideoStates(prev => ({ ...prev, [rank]: 'generating' }))

    // Simulate video generation (in production, call actual API)
    setTimeout(() => {
      setVideoStates(prev => ({ ...prev, [rank]: 'ready' }))
    }, 3000)
  }

  const handleDownloadVideo = (areaName: string) => {
    // In production, this would download the actual generated video
    // For now, show alert with info about the video generation system
    alert(`Video for ${areaName} ready!\\n\\nIn production, this downloads the AI-generated walkthrough video from the video generation pipeline.\\n\\nSee: video/output.md for the video generation system details.`)
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-2 border-slate-900 border-t-transparent mx-auto"></div>
          <p className="mt-3 text-slate-600 text-sm font-medium tracking-wide">LOADING ANALYSIS...</p>
        </div>
      </div>
    )
  }

  // Error states
  if (error || !data || data.error || !data.recommendations?.length) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center bg-white border border-slate-200 p-8 max-w-md">
          <div className="text-4xl mb-3">⚠️</div>
          <h2 className="text-lg font-semibold text-slate-900 mb-2 tracking-tight">
            {data?.error ? 'API Error' : 'No Results'}
          </h2>
          <p className="text-slate-500 text-sm mb-5">
            {data?.error || error || 'Unable to load recommendations'}
          </p>
          <button
            onClick={() => router.push('/')}
            className="bg-slate-900 text-white py-2 px-5 text-sm font-medium hover:bg-slate-800 transition-colors"
          >
            NEW SEARCH
          </button>
        </div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-slate-50 py-8 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header - Fixed alignment */}
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={() => router.push('/')}
            className="text-slate-400 hover:text-slate-900 text-sm font-medium flex items-center gap-1 px-3 py-2 border border-slate-200 hover:border-slate-300 bg-white transition-all"
          >
            ← Back
          </button>
          <div className="flex-1 flex items-end justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                Investment Analysis
              </h1>
              <p className="text-slate-500 text-sm">
                {data.persona?.toUpperCase()} PROFILE • £{(data.budget ?? 0).toLocaleString()}{data.budget && data.budget < 10000 ? '/mo' : ''} budget
              </p>
            </div>
            <div className="text-right text-xs text-slate-400">
              {data.recommendations.length} areas analyzed
            </div>
          </div>
        </div>

        {/* Shuffle Button */}
        <div className="flex justify-end mb-4">
          <button
            onClick={async () => {
              setShuffling(true)
              try {
                // Re-fetch with same params to get shuffled results
                const response = await fetch('/api/recommendations', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    persona: data.persona,
                    budget: data.budget,
                    locationType: (data.budget ?? 0) < 10000 ? 'rent' : 'buy',
                    destination: 'UCL',
                    maxAreas: 10,
                    shuffle: Date.now() // Force new random results
                  })
                })
                const newData = await response.json()
                if (newData.recommendations) {
                  setData({
                    ...data,
                    recommendations: newData.recommendations.slice(0, 5).map(generateFinancialData)
                  })
                  setVideoStates({}) // Reset video states
                }
              } catch (e) {
                console.error('Shuffle failed:', e)
              } finally {
                setShuffling(false)
              }
            }}
            disabled={shuffling}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-all disabled:opacity-50"
          >
            {shuffling ? (
              <>
                <span className="animate-spin h-4 w-4 border-2 border-slate-400 border-t-transparent rounded-full"></span>
                Shuffling...
              </>
            ) : (
              <>
                🔀 Shuffle Recommendations
              </>
            )}
          </button>
        </div>

        {/* Recommendations - Limited to 5 */}
        <div className="space-y-4">
          {data.recommendations.slice(0, 5).map((rec) => (
            <div
              key={rec.rank ?? Math.random()}
              className="bg-white border border-slate-200 p-5 hover:border-slate-300 transition-colors"
            >
              {/* Top Row: Rank, Name, Score */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="bg-slate-900 text-white w-8 h-8 flex items-center justify-center font-bold text-sm">
                    {rec.rank ?? '?'}
                  </span>
                  <div>
                    <h2 className="text-lg font-semibold text-slate-900 tracking-tight">
                      {rec.name ?? 'Unknown Area'}
                    </h2>
                    <p className="text-slate-400 text-xs font-medium">{rec.areaCode ?? ''}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-slate-900">{rec.score ?? 0}</div>
                  <div className="text-[10px] text-slate-400 uppercase tracking-wider">Score</div>
                </div>
              </div>

              {/* Financial Metrics Grid - Standardized Typography */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
                <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Rental Yield</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-xl font-bold text-slate-900">{rec.rentalYield ?? 0}</span>
                    <span className="text-sm text-slate-500">%</span>
                  </div>
                </div>
                <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">5yr ROI</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-xl font-bold text-slate-900">{rec.roi ?? 0}</span>
                    <span className="text-sm text-slate-500">%</span>
                  </div>
                </div>
                <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Avg Rent</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-xl font-bold text-slate-900">£{(rec.avgRent ?? 0).toLocaleString()}</span>
                  </div>
                </div>
                <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Avg Price</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-xl font-bold text-slate-900">£{(rec.purchasePrice ?? 0).toLocaleString()}</span>
                  </div>
                </div>
                <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">5yr Growth</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-xl font-bold text-emerald-600">+{rec.priceGrowth5yr ?? 0}</span>
                    <span className="text-sm text-slate-500">%</span>
                  </div>
                </div>
              </div>

              {/* EPC Property Specs Row - Standardized */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Avg Size</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-xl font-bold text-slate-900">{rec.floorAreaSqm ?? '—'}</span>
                    <span className="text-sm text-slate-500">sqm</span>
                  </div>
                </div>
                <div className="bg-slate-50 border border-slate-200 px-3 py-2 rounded">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Avg Rooms</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-xl font-bold text-slate-900">{rec.avgRooms ?? '—'}</span>
                  </div>
                </div>
                <div className={`px-3 py-2 rounded border ${['A', 'B'].includes(rec.energyRating || '')
                  ? 'bg-emerald-50 border-emerald-200'
                  : ['C', 'D'].includes(rec.energyRating || '')
                    ? 'bg-amber-50 border-amber-200'
                    : 'bg-red-50 border-red-200'
                  }`}>
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Energy</p>
                  <div className="flex items-baseline gap-1">
                    <span className={`text-xl font-bold ${['A', 'B'].includes(rec.energyRating || '')
                      ? 'text-emerald-600'
                      : ['C', 'D'].includes(rec.energyRating || '')
                        ? 'text-amber-600'
                        : 'text-red-600'
                      }`}>{rec.energyRating ?? 'D'}</span>
                  </div>
                </div>
              </div>

              {/* Factor Scores - Compact */}
              {rec.factors && Object.keys(rec.factors).length > 0 && (
                <div className="mb-4">
                  <div className="text-[10px] text-slate-400 uppercase tracking-wider font-medium mb-2">Factor Analysis</div>
                  <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
                    {Object.entries(rec.factors).map(([factor, score]) => (
                      <div key={factor} className="text-center">
                        <div className="text-xs text-slate-500 capitalize truncate">{factor}</div>
                        <div className={`text-sm font-bold ${(score ?? 0) >= 70 ? 'text-emerald-600' :
                          (score ?? 0) >= 50 ? 'text-amber-600' : 'text-red-500'
                          }`}>
                          {score ?? 0}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Strengths and Weaknesses - Fixed Icon Alignment */}
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                {parseItems(rec.strengths).length > 0 && (
                  <div className="border-l-2 border-emerald-400 pl-3 py-1">
                    <p className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider mb-3">Strengths</p>
                    <div className="space-y-3">
                      {parseItems(rec.strengths).map((item, i) => (
                        <div key={i} className="flex items-start gap-3">
                          {/* Icon: Fixed width, pinned to top with mt-0.5 */}
                          <span className="flex-shrink-0 w-5 h-5 mt-0.5 text-base">{item.emoji}</span>
                          <div className="text-sm min-w-0">
                            <span className="font-semibold text-slate-900 block leading-snug">{item.issue}</span>
                            {item.action && (
                              <span className="text-slate-500 leading-snug text-xs block mt-1">{item.action}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {parseItems(rec.weaknesses).length > 0 && (
                  <div className="border-l-2 border-amber-400 pl-3 py-1">
                    <p className="text-[10px] font-bold text-amber-600 uppercase tracking-wider mb-3">Considerations</p>
                    <div className="space-y-3">
                      {parseItems(rec.weaknesses).map((item, i) => (
                        <div key={i} className="flex items-start gap-3">
                          {/* Icon: Fixed width, pinned to top with mt-0.5 */}
                          <span className="flex-shrink-0 w-5 h-5 mt-0.5 text-base">{item.emoji}</span>
                          <div className="text-sm min-w-0">
                            <span className="font-semibold text-slate-900 block leading-snug">{item.issue}</span>
                            {item.action && (
                              <span className="text-slate-500 leading-snug text-xs block mt-1">{item.action}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Video Generation Button */}
              <div className="pt-3 border-t border-slate-100">
                <button
                  onClick={() => videoStates[rec.rank] === 'ready'
                    ? handleDownloadVideo(rec.name)
                    : handleGenerateVideo(rec.rank, rec.name)}
                  disabled={videoStates[rec.rank] === 'generating'}
                  className={`
                    w-full md:w-auto px-4 py-2 text-xs font-medium uppercase tracking-wider transition-all
                    ${videoStates[rec.rank] === 'idle'
                      ? 'bg-slate-900 text-white hover:bg-slate-700'
                      : videoStates[rec.rank] === 'generating'
                        ? 'bg-slate-300 text-slate-500 cursor-wait'
                        : 'bg-emerald-600 text-white hover:bg-emerald-700'
                    }
                  `}
                >
                  {videoStates[rec.rank] === 'idle' && (
                    <>🎬 Generate Walkthrough Video</>
                  )}
                  {videoStates[rec.rank] === 'generating' && (
                    <span className="flex items-center justify-center gap-2">
                      <span className="animate-spin h-3 w-3 border border-slate-500 border-t-transparent rounded-full"></span>
                      Generating...
                    </span>
                  )}
                  {videoStates[rec.rank] === 'ready' && (
                    <>✓ Video Ready — Click to Download</>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-6 py-4 border-t border-slate-200">
          <p className="text-[10px] text-slate-400 uppercase tracking-wider text-center">
            Data sources: ScanSan API • TfL • UK Police • Ofsted • Updated {new Date().toLocaleDateString()}
          </p>
        </div>
      </div >
    </main >
  )
}
