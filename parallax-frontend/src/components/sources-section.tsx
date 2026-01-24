'use client'

import { motion } from 'framer-motion'
import { ExternalLink, Newspaper } from 'lucide-react'

interface Source {
    url: string
    title?: string
    source?: string
    bias?: string
}

interface SourcesSectionProps {
    sources: Source[]
    delay?: number
}

export function SourcesSection({ sources, delay = 0 }: SourcesSectionProps) {
    // Extract domain from URL for display
    const getDomain = (url: string): string => {
        try {
            const domain = new URL(url).hostname.replace('www.', '')
            return domain
        } catch {
            return url
        }
    }

    // Generate a title from URL if not provided
    const getTitle = (source: Source): string => {
        if (source.title) return source.title
        return getDomain(source.url)
    }

    if (!sources || sources.length === 0) {
        return null
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay }}
            className="glass-panel rounded-2xl p-6"
        >
            <div className="flex items-center gap-3 mb-6">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10 ring-1 ring-white/20">
                    <Newspaper className="w-5 h-5 text-white/80" />
                </div>
                <div>
                    <h3 className="text-lg font-semibold text-white ice-text-shadow">
                        Sources
                    </h3>
                    <p className="text-sm text-white/50">
                        {sources.length} source{sources.length !== 1 ? 's' : ''} analyzed
                    </p>
                </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
                {sources.map((source, index) => (
                    <motion.a
                        key={source.url}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: delay + 0.1 + (index * 0.05) }}
                        className="source-link group"
                    >
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate group-hover:text-white">
                                {getTitle(source)}
                            </p>
                            <p className="text-xs text-white/40 truncate">
                                {getDomain(source.url)}
                            </p>
                        </div>
                        <ExternalLink className="w-4 h-4 text-white/40 group-hover:text-white/80 transition-colors flex-shrink-0" />
                    </motion.a>
                ))}
            </div>
        </motion.div>
    )
}
