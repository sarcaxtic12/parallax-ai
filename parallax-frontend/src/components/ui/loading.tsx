'use client'

import { motion, AnimatePresence } from 'framer-motion'
import {
    Search,
    Database,
    Brain,
    CheckCircle2,
    AlertCircle,
    Loader2
} from 'lucide-react'

interface LoadingProps {
    step: number
    error?: string | null
}

const steps = [
    {
        icon: Search,
        message: 'Scanning Global Sources...',
        subtext: 'Discovering relevant news articles via SerpAPI'
    },
    {
        icon: Database,
        message: 'Ingesting Data...',
        subtext: 'High-concurrency scraping via Go microservice'
    },
    {
        icon: Brain,
        message: 'Synthesizing Narratives...',
        subtext: 'Analyzing bias patterns with Llama 3.3 70B'
    },
    {
        icon: CheckCircle2,
        message: 'Analysis Complete',
        subtext: 'Results ready'
    },
]

export function LoadingAnimation({ step, error }: LoadingProps) {
    const currentStep = steps[Math.min(step, steps.length - 1)]
    const Icon = currentStep.icon

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
                        key={step}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-6"
                    >
                        {/* Animated Icon Container */}
                        <div className="relative w-20 h-20 mx-auto">
                            <motion.div
                                className="absolute inset-0 rounded-full bg-neon-cyan/20"
                                animate={{
                                    scale: [1, 1.2, 1],
                                    opacity: [0.5, 0.2, 0.5],
                                }}
                                transition={{
                                    duration: 2,
                                    repeat: Infinity,
                                    ease: 'easeInOut',
                                }}
                            />
                            <div className="absolute inset-0 flex items-center justify-center">
                                {step < 3 ? (
                                    <Loader2 className="w-10 h-10 text-neon-cyan animate-spin" />
                                ) : (
                                    <Icon className="w-10 h-10 text-green-400" />
                                )}
                            </div>
                        </div>

                        {/* Status Text */}
                        <div>
                            <p className="text-xl font-semibold text-white">
                                {currentStep.message}
                            </p>
                            <p className="text-white/50 text-sm mt-2">
                                {currentStep.subtext}
                            </p>
                        </div>

                        {/* Progress Steps */}
                        <div className="flex justify-center gap-2 pt-4">
                            {steps.slice(0, -1).map((_, i) => (
                                <motion.div
                                    key={i}
                                    className={`h-1 rounded-full transition-all duration-300 ${i <= step
                                            ? 'w-8 bg-neon-cyan'
                                            : 'w-4 bg-white/20'
                                        }`}
                                    animate={i === step ? { opacity: [0.5, 1, 0.5] } : {}}
                                    transition={{ duration: 1.5, repeat: Infinity }}
                                />
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    )
}
