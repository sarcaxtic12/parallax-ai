'use client'

import { motion } from 'framer-motion'
import { type ReactNode } from 'react'

interface GlassCardProps {
    children: ReactNode
    className?: string
    hover?: boolean
    delay?: number
    padding?: 'none' | 'sm' | 'md' | 'lg'
}

const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
}

export function GlassCard({
    children,
    className = '',
    hover = false,
    delay = 0,
    padding = 'md'
}: GlassCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
                duration: 0.5,
                delay,
                ease: [0.25, 0.46, 0.45, 0.94]
            }}
            className={`
        glass-panel rounded-2xl
        ${paddingClasses[padding]}
        ${hover ? 'glass-card-hover cursor-pointer' : ''}
        ${className}
      `}
        >
            {children}
        </motion.div>
    )
}

export function GlassCardHeader({
    children,
    icon: Icon,
    className = ''
}: {
    children: ReactNode
    icon?: React.ComponentType<{ className?: string }>
    className?: string
}) {
    return (
        <div className={`flex items-center gap-3 mb-4 ${className}`}>
            {Icon && (
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/20 text-blue-400 ring-1 ring-inset ring-blue-400/40 shadow-[0_0_15px_rgba(59,130,246,0.2)]">
                    <Icon className="w-5 h-5" />
                </div>
            )}
            <h3 className="text-lg font-semibold tracking-tight text-white">
                {children}
            </h3>
        </div>
    )
}

export function GlassCardContent({
    children,
    className = ''
}: {
    children: ReactNode
    className?: string
}) {
    return (
        <div className={`text-white/70 ${className}`}>
            {children}
        </div>
    )
}
