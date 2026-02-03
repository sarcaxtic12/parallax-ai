'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, User, Bot, Sparkles, Loader2 } from 'lucide-react'

interface Message {
    id: string
    role: 'user' | 'assistant'
    text: string
    timestamp: number
}

interface ChatInterfaceProps {
    topic: string
    initialQuery: string
    onNewAnalysis: (topic: string) => void
    // Report context for chat
    leftNarrative?: string
    rightNarrative?: string
    overview?: string
}

export function ChatInterface({ topic, initialQuery, onNewAnalysis, leftNarrative, rightNarrative, overview }: ChatInterfaceProps) {
    const [input, setInput] = useState('')
    const [messages, setMessages] = useState<Message[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    // Initial message based on topic
    useEffect(() => {
        if (topic && messages.length === 0) {
            setMessages([
                {
                    id: 'init-1',
                    role: 'user',
                    text: `Analyze this topic: ${topic}`,
                    timestamp: Date.now()
                },
                {
                    id: 'init-2',
                    role: 'assistant',
                    text: `I've analyzed the narratives around "${topic}". You can see the detailed report on the left. What specific questions do you have about the coverage?`,
                    timestamp: Date.now() + 1000
                }
            ])
        }
    }, [topic, messages.length])

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim() || isLoading) return

        const userMsg = input.trim()
        setInput('')

        // Add User Message
        const newMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            text: userMsg,
            timestamp: Date.now()
        }
        setMessages(prev => [...prev, newMsg])
        setIsLoading(true)

        try {
            // Call API with report context
            // Only include sources for the first user follow-up (when messages size is equal to initial 2) to optimize tokens
            const isFirstFollowup = messages.length === 2

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic,
                    query: userMsg,
                    left_narrative: leftNarrative,
                    right_narrative: rightNarrative,
                    overview: overview,
                    include_sources: isFirstFollowup
                })
            })

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                throw new Error(errorData.detail || 'Chat failed')
            }

            const data = await response.json()

            // Add Assistant Message
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                text: data.answer,
                timestamp: Date.now()
            }])

        } catch (error) {
            console.error(error)
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                text: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
                timestamp: Date.now()
            }])
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="flex flex-col h-full min-h-0">
            {/* Messages Area - Scrollable */}
            <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar p-6 space-y-4">
                <AnimatePresence mode="popLayout">
                    {messages.map((msg) => (
                        <motion.div
                            key={msg.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            {msg.role === 'assistant' && (
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg">
                                    <Bot className="w-4 h-4 text-white" />
                                </div>
                            )}

                            <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${msg.role === 'user'
                                ? 'bg-indigo-600/80 text-white rounded-br-sm'
                                : 'bg-white/10 text-slate-200 rounded-bl-sm border border-white/10 backdrop-blur-sm'
                                }`}>
                                <p className="leading-relaxed text-sm">{msg.text}</p>
                            </div>

                            {msg.role === 'user' && (
                                <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center flex-shrink-0 border border-white/10">
                                    <User className="w-4 h-4 text-white/70" />
                                </div>
                            )}
                        </motion.div>
                    ))}
                </AnimatePresence>

                {/* Loading Animation */}
                {isLoading && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex gap-3 justify-start"
                    >
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg">
                            <Bot className="w-4 h-4 text-white animate-pulse" />
                        </div>
                        <div className="bg-white/10 rounded-2xl px-4 py-3 rounded-bl-sm border border-white/10 backdrop-blur-sm">
                            <div className="flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full bg-white/50 animate-bounce" style={{ animationDelay: '0ms' }} />
                                <span className="w-2 h-2 rounded-full bg-white/50 animate-bounce" style={{ animationDelay: '150ms' }} />
                                <span className="w-2 h-2 rounded-full bg-white/50 animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area - Fixed at Bottom */}
            <div className="flex-shrink-0 mt-auto p-4 border-t border-white/5 bg-black/30 backdrop-blur-xl">
                <form onSubmit={handleSend} className="relative">
                    <div className="glass-input flex h-14 w-full items-center gap-3 rounded-full px-5 transition-all hover:shadow-[0_0_30px_rgba(255,255,255,0.1)] border border-white/20 bg-white/10 backdrop-blur-2xl shadow-2xl">
                        <User className="w-5 h-5 text-white/50" />
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask about the report..."
                            className="flex-1 bg-transparent text-sm font-normal text-white placeholder-white/30 focus:outline-none"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="glass-button flex items-center justify-center rounded-full p-2 disabled:opacity-30 hover:scale-105 transition-transform"
                        >
                            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
