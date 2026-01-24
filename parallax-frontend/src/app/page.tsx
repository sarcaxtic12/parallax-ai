'use client'

import { useState, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Search, ArrowRight, Sparkles, MessageSquarePlus } from 'lucide-react'
import { useAnalyze } from '@/lib/hooks'
import { LoadingAnimation } from '@/components/ui/loading'
import { BiasMeter } from '@/components/bias-meter'
import { NarrativeCards } from '@/components/narrative-cards'
import { SourcesSection } from '@/components/sources-section'
import { ArticleOverview } from '@/components/article-overview'
import { ChatInterface } from '@/components/chat-interface'
import type { AnalysisResponse } from '@/lib/api'

export default function HomePage() {
    const [topic, setTopic] = useState('')
    const [loadingStep, setLoadingStep] = useState(0)
    const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null)

    const analyzeMutation = useAnalyze()

    useEffect(() => {
        if (analyzeMutation.isPending) {
            setLoadingStep(0)
            const timer1 = setTimeout(() => setLoadingStep(1), 2000)
            const timer2 = setTimeout(() => setLoadingStep(2), 5000)
            return () => {
                clearTimeout(timer1)
                clearTimeout(timer2)
            }
        } else if (analyzeMutation.isSuccess) {
            setLoadingStep(3)
        }
    }, [analyzeMutation.isPending, analyzeMutation.isSuccess])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!topic.trim() || analyzeMutation.isPending) return

        setAnalysisData(null)
        setLoadingStep(0)

        try {
            const result = await analyzeMutation.mutateAsync(topic.trim())
            setAnalysisData(result)
        } catch (error) {
            console.error('Analysis failed:', error)
        }
    }

    const handleReset = () => {
        setTopic('')
        setAnalysisData(null)
        setLoadingStep(0)
        analyzeMutation.reset()
    }

    const showResults = analysisData && !analyzeMutation.isPending

    // Initial Search View
    return (
        <div className="min-h-screen flex flex-col relative overflow-hidden">
            {/* Logo */}
            <header className="absolute top-0 left-0 p-6 z-50">
                <div
                    className="flex items-center gap-3 cursor-pointer transition-opacity hover:opacity-80"
                    onClick={handleReset}
                >
                    <h1 className="text-3xl font-brand tracking-tight text-white/90">
                        parallax
                    </h1>
                </div>
            </header>

            <AnimatePresence mode="wait">
                {!showResults ? (
                    <motion.div
                        key="search"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0, y: -20, filter: "blur(10px)" }}
                        transition={{ duration: 0.5 }}
                        className="flex-1 flex flex-col items-center justify-center px-4 -mt-20"
                    >
                        <div className="w-full max-w-2xl text-center space-y-8">
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 }}
                            >
                                <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 ice-text-shadow">
                                    What's the narrative?
                                </h2>
                                <p className="text-lg text-white/50">
                                    Discover how different sources frame the same story.
                                </p>
                            </motion.div>

                            <form onSubmit={handleSubmit}>
                                <div className="glass-input flex h-16 w-full items-center gap-4 rounded-full px-6 transition-all hover:shadow-[0_0_30px_rgba(255,255,255,0.1)]">
                                    <Search className="w-6 h-6 text-white/60" />
                                    <input
                                        type="text"
                                        value={topic}
                                        onChange={(e) => setTopic(e.target.value)}
                                        placeholder="Enter a topic to research..."
                                        disabled={analyzeMutation.isPending}
                                        className="flex-1 bg-transparent text-lg font-light text-white placeholder-white/40 focus:outline-none"
                                        autoFocus
                                    />
                                    <button
                                        type="submit"
                                        disabled={!topic.trim() || analyzeMutation.isPending}
                                        className="glass-button flex items-center justify-center rounded-full p-3 disabled:opacity-30 hover:scale-105 transition-transform"
                                    >
                                        {analyzeMutation.isPending ? (
                                            <Sparkles className="w-5 h-5 animate-pulse" />
                                        ) : (
                                            <ArrowRight className="w-5 h-5" />
                                        )}
                                    </button>
                                </div>
                            </form>

                            {analyzeMutation.isPending && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="mt-12"
                                >
                                    <LoadingAnimation step={loadingStep} />
                                </motion.div>
                            )}
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="results"
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                        className="h-screen flex flex-col overflow-hidden"
                    >
                        {/* Fixed Header */}
                        <header className="flex-shrink-0 p-4 border-b border-white/5 bg-black/20 backdrop-blur-xl z-50 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div
                                    className="cursor-pointer transition-opacity hover:opacity-80"
                                    onClick={handleReset}
                                >
                                    <h1 className="text-2xl font-brand tracking-tight text-white/90">
                                        parallax
                                    </h1>
                                </div>
                                <span className="text-white/30 text-sm ml-4">|</span>
                                <span className="text-white/50 text-sm">{analysisData?.topic}</span>
                            </div>

                            <button
                                onClick={handleReset}
                                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 text-sm transition-colors border border-white/5"
                            >
                                <MessageSquarePlus className="w-4 h-4" />
                                <span className="hidden sm:inline">New Chat</span>
                            </button>
                        </header>

                        {/* Split Content */}
                        <div className="flex-1 flex overflow-hidden">
                            {/* Left Panel - Report */}
                            <div className="w-full lg:w-1/2 h-full overflow-y-auto custom-scrollbar border-r border-white/5 bg-black/5">
                                <div className="p-6 lg:p-10 space-y-6 w-full">
                                    {/* Report Header */}
                                    <div>
                                        <p className="text-white/40 text-xs uppercase tracking-widest mb-2">
                                            Research Report
                                        </p>
                                        <h2 className="text-2xl font-bold text-white ice-text-shadow">
                                            {analysisData?.topic}
                                        </h2>
                                        <div className="flex items-center gap-2 mt-2">
                                            <span className="px-2 py-0.5 rounded-md bg-white/10 text-white/60 text-xs font-medium">
                                                {analysisData?.sources_count} Sources
                                            </span>
                                            <span className="text-white/30 text-xs">GPT-OSS 120B</span>
                                        </div>
                                    </div>

                                    <div className="glass-panel rounded-2xl p-5">
                                        <BiasMeter data={analysisData?.bias_counts || { Left: 0, Center: 0, Right: 0 }} delay={0} />
                                    </div>

                                    <NarrativeCards data={analysisData?.narratives || { Left: '', Right: '' }} delay={0} />

                                    <ArticleOverview
                                        topic={analysisData?.topic || ''}
                                        narratives={analysisData?.narratives || { Left: '', Right: '' }}
                                        delay={0}
                                    />

                                    <SourcesSection sources={analysisData?.sources || []} delay={0} />
                                </div>
                            </div>

                            {/* Right Panel - Chat */}
                            <div className="hidden lg:flex w-1/2 h-full flex-col overflow-hidden bg-black/10">
                                <ChatInterface
                                    topic={analysisData?.topic || ''}
                                    initialQuery={topic}
                                    onNewAnalysis={setTopic}
                                />
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
