'use client'

import { motion } from 'framer-motion'
import type { BiasCount } from '@/lib/api'

interface BiasMeterProps {
    data: BiasCount
    delay?: number
}

export function BiasMeter({ data, delay = 0 }: BiasMeterProps) {
    const total = data.Left + data.Center + data.Right

    // Calculate bias score (0 = far left, 50 = center, 100 = far right)
    const leftWeight = data.Left
    const rightWeight = data.Right
    const biasScore = total > 0 ? 50 + ((rightWeight - leftWeight) / total) * 50 : 50
    const biasLabel = biasScore > 55 ? `Leans Right (+${Math.round(biasScore - 50)})` :
        biasScore < 45 ? `Leans Left (${Math.round(biasScore - 50)})` : 'Neutral'

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay }}
            className="space-y-6"
        >
            {/* Header with Badge */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex flex-col">
                    <h2 className="text-lg font-semibold text-white tracking-wide ice-text-shadow">
                        Aggregate Bias Score
                    </h2>
                    <p className="text-sm text-white/50">
                        Based on {total} analyzed sources
                    </p>
                </div>
                <div className="flex items-center gap-2 rounded-lg bg-stone-500/10 px-3 py-1.5 border border-stone-400/20 shadow-[0_0_10px_rgba(255,255,255,0.05)] min-w-[140px] justify-center">
                    <div className="h-2 w-2 rounded-full bg-stone-400 animate-pulse shadow-[0_0_8px_rgba(168,162,158,0.8)] flex-shrink-0"></div>
                    <span className="text-sm font-medium text-stone-200 text-center">
                        {biasLabel}
                    </span>
                </div>
            </div>

            {/* Bias Bar */}
            <div className="relative pt-6 pb-2">
                {/* Track */}
                <div className="relative h-3 w-full rounded-full bg-white/5 ring-1 ring-white/10">
                    <div className="absolute inset-0 rounded-full opacity-40 bg-gradient-to-r from-slate-400 via-white/5 to-stone-400 blur-[2px]"></div>
                    <div className="absolute inset-0 rounded-full opacity-60 bg-gradient-to-r from-slate-500 via-transparent to-stone-500"></div>

                    {/* Scale markers */}
                    <div className="absolute top-1/2 left-0 h-4 w-[1px] -translate-y-1/2 bg-white/30"></div>
                    <div className="absolute top-1/2 left-1/2 h-5 w-[1px] -translate-y-1/2 bg-white/50 shadow-[0_0_5px_white]"></div>
                    <div className="absolute top-1/2 right-0 h-4 w-[1px] -translate-y-1/2 bg-white/30"></div>

                    {/* Position indicator */}
                    <motion.div
                        initial={{ left: '50%' }}
                        animate={{ left: `${biasScore}%` }}
                        transition={{ duration: 0.8, delay: delay + 0.2, ease: [0.25, 0.46, 0.45, 0.94] }}
                        className="absolute top-1/2 h-6 w-6 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white bg-white/20 backdrop-blur-md shadow-[0_0_15px_rgba(255,255,255,0.6)]"
                    >
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: delay + 0.5 }}
                            className="absolute top-[-26px] left-1/2 -translate-x-1/2 whitespace-nowrap text-xs font-bold text-white bg-white/10 px-2 py-0.5 rounded-full border border-white/10 backdrop-blur-sm"
                        >
                            {Math.round(biasScore)}%
                        </motion.div>
                    </motion.div>
                </div>

                {/* Labels */}
                <div className="mt-3 relative h-4 text-xs font-semibold text-white/40 uppercase tracking-widest">
                    <span className="absolute left-0 text-slate-400/80">Liberal</span>
                    <span className="absolute left-1/2 -translate-x-1/2">Neutral</span>
                    <span className="absolute right-0 text-stone-400/80">Conservative</span>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-3 gap-4 mt-6">
                {[
                    { key: 'Left', label: 'Left', count: data.Left, color: '#94a3b8' },
                    { key: 'Center', label: 'Center', count: data.Center, color: '#e2e8f0' },
                    { key: 'Right', label: 'Right', count: data.Right, color: '#a8a29e' },
                ].map((item, index) => (
                    <motion.div
                        key={item.key}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.4, delay: delay + 0.4 + (index * 0.1) }}
                        className="text-center p-4 rounded-xl border bg-white/5 border-white/10"
                    >
                        <span
                            className="text-sm font-medium uppercase tracking-wide"
                            style={{ color: item.color }}
                        >
                            {item.label}
                        </span>
                        <p
                            className="text-3xl font-bold mt-2"
                            style={{ color: item.color }}
                        >
                            {item.count}
                        </p>
                        <p className="text-white/40 text-sm mt-1">
                            {total > 0 ? ((item.count / total) * 100).toFixed(0) : 0}%
                        </p>
                    </motion.div>
                ))}
            </div>
        </motion.div>
    )
}
