export function Footer() {
    return (
        <footer className="w-full py-6 mt-auto border-t border-white/5 bg-black/20 backdrop-blur-sm">
            <div className="mx-auto max-w-7xl px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-white/30">
                <div className="flex items-center gap-2">
                    <span className="font-medium">Parallax AI</span>
                    <span className="w-1 h-1 rounded-full bg-white/20" />
                    <span>v2.0.0</span>
                </div>
                <div className="flex items-center gap-2">
                    <span>Designed & Developed by Hyder Ahmed</span>
                    <span className="hidden md:inline">|</span>
                    <span className="hidden md:inline">© 2026 All Rights Reserved</span>
                </div>
            </div>
        </footer>
    )
}
