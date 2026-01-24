import type { Config } from 'tailwindcss'

const config: Config = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                "primary": "#e5e5e5",
                "obsidian": "#050505",
                "pewter": "#94a3b8",
                "pewter-dark": "#475569",
                "champagne": "#e5d9b6",
                "champagne-dark": "#a8a29e",
                "glass-fill": "rgba(40, 40, 40, 0.3)",
                "smoke-1": "#27272a",
                "smoke-2": "#1c1917",
            },
            fontFamily: {
                "display": ["Inter", "sans-serif"],
                "brand": ["Bodoni MT Black", "serif"]
            },
            borderRadius: { "DEFAULT": "0.5rem", "lg": "1rem", "xl": "1.5rem", "full": "9999px" },
            boxShadow: {
                "glass": "0 8px 32px 0 rgba(0, 0, 0, 0.5)",
                "glow-pewter": "0 0 25px rgba(148, 163, 184, 0.15)",
                "glow-champagne": "0 0 25px rgba(229, 217, 182, 0.15)",
                "glow-white": "0 0 20px rgba(255, 255, 255, 0.1)",
            }
        },
    },
    plugins: [],
}

export default config
