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

export interface AnalysisProgress {
    phase: 'discovery' | 'scraping' | 'analysis'
    progress: number
    message?: string
    current?: number
    total?: number
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

/**
 * Run analysis with Server-Sent Events progress updates.
 * onProgress is called with phase, progress 0-100, and optional message/current/total.
 */
export async function analyzeTopicWithProgress(
    topic: string,
    onProgress: (p: AnalysisProgress) => void
): Promise<AnalysisResponse> {
    const response = await fetch(`${API_URL}/api/analyze/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')
    const decoder = new TextDecoder()
    let buffer = ''
    let result: AnalysisResponse | null = null
    let errorDetail: string | null = null
    while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.slice(6))
                    if (data.event === 'progress') {
                        onProgress({
                            phase: data.phase,
                            progress: data.progress ?? 0,
                            message: data.message,
                            current: data.current,
                            total: data.total,
                        })
                    } else if (data.event === 'result') {
                        result = data.data
                    } else if (data.event === 'error') {
                        errorDetail = data.detail ?? 'Analysis failed'
                    }
                } catch (_) {}
            }
        }
    }
    if (errorDetail) throw new Error(errorDetail)
    if (!result) throw new Error('Analysis failed')
    return result
}

export async function checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_URL}/api/health`)

    if (!response.ok) {
        return { status: 'error', database: 'error', scraper: 'error' }
    }

    return response.json()
}
