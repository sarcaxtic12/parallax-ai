'use client'

import { motion } from 'framer-motion'
import { Globe, Gavel } from 'lucide-react'
import type { Narratives } from '@/lib/api'

interface NarrativeCardsProps {
    data: Narratives
    delay?: number
}

export function NarrativeCards({ data, delay = 0 }: NarrativeCardsProps) {
    const cards = [
        {
            key: 'Left',
            title: 'Liberal Perspective',
            content: data.Left,
            icon: Globe,
            glowClass: 'border-glow-slate',
            bgGlow: 'bg-slate-400/20',
            bgGlowHover: 'group-hover:bg-slate-300/25',
            iconBg: 'bg-slate-500/10',
            iconRing: 'ring-slate-400/30',
            iconGlow: 'shadow-[0_0_15px_rgba(148,163,184,0.1)]',
            textColor: 'text-slate-300',
            labelColor: 'text-slate-400/90',
            contentColor: 'text-slate-200/90',
            tagBg: 'bg-slate-500/10',
            tagBorder: 'border-slate-500/20',
            tagText: 'text-slate-200',
        },
        {
            key: 'Right',
            title: 'Conservative Perspective',
            content: data.Right,
            icon: Gavel,
            glowClass: 'border-glow-stone',
            bgGlow: 'bg-stone-400/20',
            bgGlowHover: 'group-hover:bg-stone-300/25',
            iconBg: 'bg-stone-500/10',
            iconRing: 'ring-stone-400/30',
            iconGlow: 'shadow-[0_0_15px_rgba(168,162,158,0.1)]',
            textColor: 'text-stone-300',
            labelColor: 'text-stone-400/90',
            contentColor: 'text-stone-200/90',
            tagBg: 'bg-stone-500/10',
            tagBorder: 'border-stone-500/20',
            tagText: 'text-stone-200',
        },
    ]

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {cards.map((card, index) => {
                const Icon = card.icon
                return (
                    <motion.div
                        key={card.key}
                        initial={{ opacity: 0, x: index === 0 ? -20 : 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{
                            duration: 0.6,
                            delay: delay + (index * 0.15),
                            ease: [0.25, 0.46, 0.45, 0.94]
                        }}
                        className={`glass-panel group relative flex flex-col justify-between overflow-hidden rounded-2xl p-6 transition-all duration-300 ${card.glowClass}`}
                    >
                        {/* Decorative glow orb */}
                        <div className={`absolute -right-20 -top-20 h-64 w-64 rounded-full ${card.bgGlow} blur-[70px] transition-all duration-500 ${card.bgGlowHover} group-hover:blur-[60px]`} />

                        <div className="relative z-10">
                            {/* Header */}
                            <div className="mb-5 flex items-center gap-3">
                                <div className={`flex h-12 w-12 items-center justify-center rounded-full ${card.iconBg} ${card.textColor} ring-1 ring-inset ${card.iconRing} ${card.iconGlow}`}>
                                    <Icon className="w-6 h-6" />
                                </div>
                                <h3 className="text-2xl font-bold text-white drop-shadow-sm">
                                    {card.title}
                                </h3>
                            </div>

                            {/* Content */}
                            <div className="space-y-4">
                                <div>
                                    <p className={`mb-2 text-xs font-bold uppercase tracking-widest ${card.labelColor}`}>
                                        Core Narrative
                                    </p>
                                    {card.content ? (
                                        <p className={`text-base leading-relaxed ${card.contentColor} font-light`}>
                                            {card.content}
                                        </p>
                                    ) : (
                                        <p className="text-white/40 text-base">
                                            No narrative data available
                                        </p>
                                    )}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )
            })}
        </div>
    )
}
