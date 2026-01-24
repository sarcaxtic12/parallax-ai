'use client'

import { useMutation, useQuery } from '@tanstack/react-query'
import { analyzeTopic, checkHealth, type AnalysisResponse } from './api'

/**
 * Hook for analyzing a topic
 */
export function useAnalyze() {
    return useMutation<AnalysisResponse, Error, string>({
        mutationFn: analyzeTopic,
    })
}

/**
 * Hook for health check
 */
export function useHealth() {
    return useQuery({
        queryKey: ['health'],
        queryFn: checkHealth,
        refetchInterval: 60000,
        retry: false,
    })
}
