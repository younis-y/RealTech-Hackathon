import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    // maxAreas defaults to 5 so a request that omits it does not throw.
    const { persona, budget, locationType, destination, maxAreas = 5 } = body

    // Path to Python script (relative to project root)
    const pythonScript = path.join(process.cwd(), '..', 'demo_pipeline.py')

    // Build Python command arguments
    const args = [
      pythonScript,
      '--persona', persona,
      '--budget', budget.toString(),
      '--type', locationType,
      '--destination', destination || 'UCL',
      '--max-areas', maxAreas.toString(),
      '--no-explanations' // Skip explanations for faster response in demo
    ]

    // Execute Python script
    const result = await executePython(args)

    // Parse Python output (this is simplified - in production you'd want structured JSON output)
    const recommendations = parsePythonOutput(result)

    return NextResponse.json({
      success: true,
      persona,
      budget,
      recommendations
    })

  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { error: 'Failed to generate recommendations' },
      { status: 500 }
    )
  }
}

function executePython(args: string[]): Promise<string> {
  return new Promise((resolve, reject) => {
    const python = spawn('python', args)
    let output = ''
    let errorOutput = ''

    python.stdout.on('data', (data) => {
      output += data.toString()
    })

    python.stderr.on('data', (data) => {
      errorOutput += data.toString()
    })

    python.on('close', (code) => {
      if (code === 0) {
        resolve(output)
      } else {
        reject(new Error(`Python script exited with code ${code}: ${errorOutput}`))
      }
    })

    python.on('error', (error) => {
      reject(error)
    })
  })
}

function parsePythonOutput(output: string): any[] {
  // This is a simplified parser for demo purposes
  // In production, you'd modify the Python script to output JSON directly

  const recommendations = []
  const lines = output.split('\n')

  let currentRec: any = null

  for (const line of lines) {
    // Parse recommendation rank and name
    const rankMatch = line.match(/#(\d+)\.\s+([^(]+)\(([^)]+)\)\s+-\s+Score:\s+([\d.]+)/)
    if (rankMatch) {
      if (currentRec) {
        recommendations.push(currentRec)
      }
      currentRec = {
        rank: parseInt(rankMatch[1]),
        name: rankMatch[2].trim(),
        areaCode: rankMatch[3],
        score: parseFloat(rankMatch[4]),
        factors: {},
        strengths: [],
        weaknesses: []
      }
    }

    // Parse factor scores
    const factorMatch = line.match(/\s+(\w+)\s*:\s*(\d+)\/100/)
    if (factorMatch && currentRec) {
      currentRec.factors[factorMatch[1]] = parseInt(factorMatch[2])
    }

    // Parse strengths. The '+' must stay escaped: /\[+\]/ would mean
    // "one or more '[' then ']'" and never match '[+] Strengths:'.
    const strengthMatch = line.match(/\[\+\] Strengths:\s+(.+)/)
    if (strengthMatch && currentRec) {
      currentRec.strengths = strengthMatch[1].split(',').map(s => s.trim())
    }

    // Parse weaknesses
    const weaknessMatch = line.match(/\[-\] Weaknesses:\s+(.+)/)
    if (weaknessMatch && currentRec) {
      currentRec.weaknesses = weaknessMatch[1].split(',').map(s => s.trim())
    }
  }

  if (currentRec) {
    recommendations.push(currentRec)
  }

  return recommendations.slice(0, 3) // Return top 3
}
