'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useEffect, useState } from 'react'
import {
    Search,
    Database,
    Brain,
    CheckCircle2,
    AlertCircle,
    Loader2
} from 'lucide-react'

interface LoadingProps {
    step?: number
    error?: string | null
    /** Real progress 0-100 from server (overrides step when set) */
    progress?: number
    phase?: 'discovery' | 'scraping' | 'analysis'
    message?: string
    current?: number
    total?: number
}

const steps = [
    {
        icon: Search,
        message: 'Scanning Global Sources...',
        subtext: 'Discovering diverse perspectives'
    },
    {
        icon: Database,
        message: 'Reading Articles...',
        subtext: 'Processing content from multiple sources'
    },
    {
        icon: Brain,
        message: 'Analyzing Perspectives...',
        subtext: 'Synthesizing viewpoints and detecting bias'
    },
    {
        icon: CheckCircle2,
        message: 'Analysis Complete',
        subtext: 'Report ready'
    },
]

const phaseConfig: Record<string, { message: string; subtext: string; icon: typeof Search }> = {
    discovery: { message: 'Scanning Global Sources...', subtext: 'Discovering diverse perspectives', icon: Search },
    scraping: { message: 'Reading Articles...', subtext: 'Processing content from multiple sources', icon: Database },
    analysis: { message: 'Analyzing Perspectives...', subtext: 'Synthesizing viewpoints and detecting bias', icon: Brain },
}

export function LoadingAnimation({ step = 0, error, progress, phase, message, current, total }: LoadingProps) {
    const useRealProgress = typeof progress === 'number'
    const fallbackStep = steps[Math.min(step, steps.length - 1)]
    const phaseStep = phase && phaseConfig[phase] ? phaseConfig[phase] : null
    const displayMessage = message ?? (phaseStep?.message ?? fallbackStep.message)
    const displaySubtext = (useRealProgress && total != null && current != null && phase === 'scraping')
        ? `Article ${current} of ${total}`
        : (phaseStep?.subtext ?? fallbackStep.subtext)

    // When stuck in "analysis" at ~90%+, crawl the bar toward 98% so the user sees movement (~1% every 2s)
    const [crawlPct, setCrawlPct] = useState<number | null>(null)
    const serverPct = useRealProgress ? Math.min(100, Math.max(0, progress)) : (step / 3) * 100
    const isAnalysisStalled = phase === 'analysis' && serverPct >= 90 && serverPct < 98
    useEffect(() => {
        if (!isAnalysisStalled) {
            setCrawlPct(null)
            return
        }
        setCrawlPct(serverPct)
        const target = 98
        const start = serverPct
        const duration = 20000 // 20s to crawl from current to 98%
        const startTime = Date.now()
        const tick = () => {
            const elapsed = Date.now() - startTime
            const t = Math.min(1, elapsed / duration)
            const eased = 1 - (1 - t) * (1 - t) // ease-out quad
            const value = start + (target - start) * eased
            setCrawlPct(value)
            if (t < 1) requestAnimationFrame(tick)
        }
        const id = requestAnimationFrame(tick)
        return () => cancelAnimationFrame(id)
    }, [phase, serverPct, isAnalysisStalled])
    const pct = isAnalysisStalled && crawlPct != null ? crawlPct : serverPct

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="glass-card p-8 w-full max-w-md mx-auto text-center"
        >
            <AnimatePresence mode="wait">
                {error ? (
                    <motion.div
                        key="error"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-4"
                    >
                        <div className="w-16 h-16 mx-auto rounded-full bg-red-500/20 flex items-center justify-center">
                            <AlertCircle className="w-8 h-8 text-red-400" />
                        </div>
                        <div>
                            <p className="text-red-400 font-medium">Analysis Failed</p>
                            <p className="text-white/50 text-sm mt-1">{error}</p>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key={pct}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-6"
                    >
                        {/* Improved Spacing: Only show checkmark space when complete, otherwise minimal spacer */}
                        {pct >= 95 ? (
                            <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
                                <CheckCircle2 className="w-12 h-12 text-green-400" aria-hidden />
                            </div>
                        ) : (
                            <div className="h-2" />
                        )}

                        <div>
                            <p className="text-xl font-semibold text-white">{displayMessage}</p>
                        </div>

                        {/* Progress bar: visible track + filled bar */}
                        <div className="w-full rounded-full h-3 overflow-hidden bg-white/15 border border-white/10 shadow-inner">
                            <motion.div
                                className="h-full rounded-full min-w-[4px] bg-neon-cyan shadow-[0_0_12px_rgba(34,211,238,0.5)]"
                                initial={false}
                                animate={{ width: `${Math.max(2, pct)}%` }}
                                transition={{ duration: 0.5, ease: 'easeOut' }}
                            />
                        </div>
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-white/50">{displaySubtext}</span>
                            <span className="text-neon-cyan font-semibold tabular-nums">{Math.round(pct)}%</span>
                        </div>
                        {isAnalysisStalled && (
                            <p className="text-white/40 text-xs">This step can take a minute—LLM is synthesizing narratives.</p>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    )
}
