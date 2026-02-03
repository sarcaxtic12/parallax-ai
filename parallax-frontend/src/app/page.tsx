'use client'

import { useState, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Search, ArrowRight, Loader2, MessageSquarePlus } from 'lucide-react'
import { LoadingAnimation } from '@/components/ui/loading'
import { BiasMeter } from '@/components/bias-meter'
import { NarrativeCards } from '@/components/narrative-cards'
import { SourcesSection } from '@/components/sources-section'
import { ArticleOverview } from '@/components/article-overview'
import { ChatInterface } from '@/components/chat-interface'
import { Footer } from '@/components/footer'
import { analyzeTopicWithProgress, type AnalysisResponse, type AnalysisProgress } from '@/lib/api'

export default function HomePage() {
    const [topic, setTopic] = useState('')
    const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [analyzeError, setAnalyzeError] = useState<string | null>(null)
    const [progress, setProgress] = useState<AnalysisProgress | null>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!topic.trim() || isAnalyzing) return

        setAnalysisData(null)
        setAnalyzeError(null)
        setProgress(null)
        setIsAnalyzing(true)

        try {
            const result = await analyzeTopicWithProgress(topic.trim(), (p) => setProgress(p))
            setAnalysisData(result)
        } catch (error) {
            console.error('Analysis failed:', error)
            setAnalyzeError(error instanceof Error ? error.message : 'Analysis failed')
        } finally {
            setIsAnalyzing(false)
            setProgress(null)
        }
    }

    const handleReset = () => {
        setTopic('')
        setAnalysisData(null)
        setAnalyzeError(null)
        setProgress(null)
    }

    const showResults = analysisData && !isAnalyzing

    // Toggle body class for results mode (viewport locking)
    useEffect(() => {
        if (showResults) {
            document.body.classList.add('results-mode')
        } else {
            document.body.classList.remove('results-mode')
        }
        return () => {
            document.body.classList.remove('results-mode')
        }
    }, [showResults])

    // Initial Search View
    return (
        <>
            <AnimatePresence mode="wait">
                {!showResults ? (
                    <div className="min-h-screen flex flex-col relative overflow-hidden">
                        {/* Logo */}
                        <header className="absolute top-0 left-0 p-6 z-50 flex-shrink-0">
                            <div
                                className="flex items-center gap-3 cursor-pointer transition-opacity hover:opacity-80"
                                onClick={handleReset}
                            >
                                <h1 className="text-3xl font-brand tracking-tight text-white/90">
                                    parallax
                                </h1>
                            </div>
                        </header>

                        <motion.div
                            key="search"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0, y: -20, filter: "blur(10px)" }}
                            transition={{ duration: 0.5 }}
                            className="flex-1 flex flex-col items-center justify-center min-h-0 px-4 overflow-y-auto"
                        >
                            {/* Centered Content Container */}
                            <div className="w-full max-w-2xl text-center space-y-6 flex flex-col items-center justify-center">
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.2 }}
                                >
                                    <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4 ice-text-shadow">
                                        What's the narrative?
                                    </h2>
                                    <p className="text-base sm:text-lg text-white/50">
                                        Discover how different sources frame the same story.
                                    </p>
                                </motion.div>

                                <form onSubmit={handleSubmit} className="w-full">
                                    <div className="glass-input flex h-14 w-full items-center gap-4 rounded-full px-5 transition-all hover:shadow-[0_0_40px_rgba(255,255,255,0.15)] border border-white/20 bg-white/10 backdrop-blur-2xl shadow-xl">
                                        <Search className="w-5 h-5 text-white/50" />
                                        <input
                                            type="text"
                                            value={topic}
                                            onChange={(e) => setTopic(e.target.value)}
                                            placeholder=""
                                            disabled={isAnalyzing}
                                            className="flex-1 bg-transparent text-lg font-normal text-white focus:outline-none"
                                            autoFocus
                                        />
                                        <button
                                            type="submit"
                                            disabled={!topic.trim() || isAnalyzing}
                                            className="flex items-center justify-center p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors disabled:opacity-30"
                                        >
                                            {isAnalyzing ? (
                                                <Loader2 className="w-5 h-5 animate-spin text-white/70" />
                                            ) : (
                                                <ArrowRight className="w-5 h-5 text-white/70" />
                                            )}
                                        </button>
                                    </div>
                                </form>

                                {(isAnalyzing || analyzeError) && (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="mt-8 w-full flex justify-center flex-shrink-0"
                                    >
                                        <LoadingAnimation
                                            progress={progress?.progress}
                                            phase={progress?.phase}
                                            message={progress?.message}
                                            current={progress?.current}
                                            total={progress?.total}
                                            error={analyzeError}
                                        />
                                    </motion.div>
                                )}
                            </div>
                        </motion.div>

                        <Footer />
                    </div>
                ) : (
                    <motion.div
                        key="results"
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                        className="h-screen flex flex-col overflow-hidden"
                    >
                        {/* Fixed Header */}
                        <header className="flex-shrink-0 px-6 py-4 border-b border-white/5 bg-black/20 backdrop-blur-xl z-50 flex items-center justify-between">
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

                        {/* Split Content - Both panels fill remaining height */}
                        <div className="flex-1 flex min-h-0">
                            {/* Left Panel - Report (independent scroll) */}
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
                                            <span className="text-white/30 text-xs">Llama 3.3 70B</span>
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

                            {/* Right Panel - Chat (independent scroll with fixed input) */}
                            <div className="hidden lg:flex w-1/2 h-full flex-col overflow-hidden bg-black/10">
                                <ChatInterface
                                    topic={analysisData?.topic || ''}
                                    initialQuery={topic}
                                    onNewAnalysis={setTopic}
                                    leftNarrative={analysisData?.narratives?.Left}
                                    rightNarrative={analysisData?.narratives?.Right}
                                    overview={analysisData?.omission_report}
                                />
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    )
}

