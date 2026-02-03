/**
 * API Client for Parallax AI Backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Types
export interface BiasCount {
    Left: number
    Center: number
    Right: number
}

export interface Narratives {
    Left: string
    Right: string
}

export interface Source {
    url: string
    title?: string
    source?: string
    bias?: string
}

export interface AnalysisResponse {
    success: boolean
    topic: string
    bias_counts: BiasCount
    narratives: Narratives
    omission_report: string
    sources_count: number
    sources?: Source[]
}

export interface HealthResponse {
    status: string
    database: string
    scraper: string
}

// API Functions
export async function analyzeTopic(topic: string): Promise<AnalysisResponse> {
    const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
    })

    if (!response.ok) {
        const fallback =
            response.status === 502 || response.status === 503
                ? 'Service temporarily unavailable. Please try again in a minute.'
                : 'Analysis failed'
        const error = await response.json().catch(() => ({ detail: fallback }))
        throw new Error(error.detail || fallback)
    }

    return response.json()
}

export async function checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_URL}/api/health`)

    if (!response.ok) {
        return { status: 'error', database: 'error', scraper: 'error' }
    }

    return response.json()
}
