'use client'

import { motion } from 'framer-motion'
import { BookOpen } from 'lucide-react'
import type { Narratives } from '@/lib/api'

interface ArticleOverviewProps {
    topic: string
    narratives: Narratives
    delay?: number
}

export function ArticleOverview({ topic, narratives, delay = 0 }: ArticleOverviewProps) {
    // Generate a synthesized article overview from the narratives
    const generateArticle = (): string => {
        const leftNarrative = narratives.Left || ''
        const rightNarrative = narratives.Right || ''

        if (!leftNarrative && !rightNarrative) {
            return `Analysis of "${topic}" is currently in progress. Check back for a comprehensive overview synthesized from multiple perspectives.`
        }

        // Create a balanced overview combining both perspectives
        let article = `The topic of "${topic}" has generated significant discourse across the media landscape, with distinct perspectives emerging from different sources.\n\n`

        if (leftNarrative) {
            article += `Progressive-leaning sources emphasize ${leftNarrative.toLowerCase()}\n\n`
        }

        if (rightNarrative) {
            article += `Conservative-leaning sources highlight ${rightNarrative.toLowerCase()}\n\n`
        }

        article += `This analysis synthesizes multiple viewpoints to provide a balanced understanding of the current narrative landscape surrounding this topic.`

        return article
    }

    const articleContent = generateArticle()

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay }}
            className="glass-panel rounded-2xl p-6"
        >
            {/* Header */}
            <div className="flex items-center gap-3 mb-6">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10 ring-1 ring-white/20">
                    <BookOpen className="w-5 h-5 text-white/80" />
                </div>
                <div>
                    <h3 className="text-lg font-semibold text-white ice-text-shadow">
                        Overview
                    </h3>
                    <p className="text-sm text-white/50">
                        Synthesized from analyzed sources
                    </p>
                </div>
            </div>

            {/* Article Content */}
            <div className="article-content">
                {articleContent.split('\n\n').map((paragraph, index) => (
                    <p key={index} className="text-white/80 leading-relaxed">
                        {paragraph}
                    </p>
                ))}
            </div>
        </motion.div>
    )
}
