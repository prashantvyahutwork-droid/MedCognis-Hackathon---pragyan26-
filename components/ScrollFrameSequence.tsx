"use client";

import { useRef, useEffect, useState, memo } from "react";
import { useScroll, useTransform } from "framer-motion";

interface ScrollFrameSequenceProps {
    frameCount?: number;
    height?: string;
}

// Use every 4th frame for performance (200 -> 50 frames)
const FRAME_STEP = 4;

function ScrollFrameSequenceInner({ frameCount = 200, height = "300vh" }: ScrollFrameSequenceProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const imagesRef = useRef<(HTMLImageElement | null)[]>([]);
    const [loaded, setLoaded] = useState(false);
    const rafRef = useRef<number>(0);

    const totalUsableFrames = Math.ceil(frameCount / FRAME_STEP);

    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start start", "end end"],
    });

    const frameIndex = useTransform(scrollYProgress, [0, 1], [0, totalUsableFrames - 1]);

    // Load frames in batches for better performance
    useEffect(() => {
        let cancelled = false;
        const images: (HTMLImageElement | null)[] = new Array(totalUsableFrames).fill(null);

        const loadBatch = async (start: number, end: number) => {
            const promises: Promise<void>[] = [];
            for (let i = start; i < Math.min(end, totalUsableFrames); i++) {
                const actualFrame = i * FRAME_STEP + 1;
                if (actualFrame > frameCount) break;
                promises.push(
                    new Promise<void>((resolve) => {
                        const img = new Image();
                        const num = actualFrame.toString().padStart(3, "0");
                        img.src = `/frames/ezgif-frame-${num}.jpg`;
                        img.onload = () => { if (!cancelled) images[i] = img; resolve(); };
                        img.onerror = () => resolve();
                    })
                );
            }
            await Promise.all(promises);
        };

        // Load first 10 frames immediately, rest in background
        const loadAll = async () => {
            await loadBatch(0, 10);
            if (!cancelled) {
                imagesRef.current = [...images];
                setLoaded(true);
            }
            // Load remaining in background
            await loadBatch(10, totalUsableFrames);
            if (!cancelled) imagesRef.current = [...images];
        };

        loadAll();
        return () => { cancelled = true; };
    }, [frameCount, totalUsableFrames]);

    useEffect(() => {
        if (!loaded || !canvasRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d", { alpha: false });
        if (!ctx) return;

        let currentWidth = 0;
        let currentHeight = 0;

        const updateCanvasSize = () => {
            const w = window.innerWidth;
            const h = window.innerHeight;
            if (w !== currentWidth || h !== currentHeight) {
                canvas.width = w;
                canvas.height = h;
                currentWidth = w;
                currentHeight = h;
            }
        };

        updateCanvasSize();
        window.addEventListener("resize", updateCanvasSize);

        let lastRenderedFrame = -1;

        const renderFrame = (index: number) => {
            const roundedIndex = Math.round(index);
            if (roundedIndex === lastRenderedFrame) return; // Skip duplicate renders
            lastRenderedFrame = roundedIndex;

            const img = imagesRef.current[roundedIndex];
            if (!img) return;

            const hRatio = canvas.width / img.width;
            const vRatio = canvas.height / img.height;
            const ratio = Math.max(hRatio, vRatio);
            const cx = (canvas.width - img.width * ratio) / 2;
            const cy = (canvas.height - img.height * ratio) / 2;

            ctx.drawImage(img, 0, 0, img.width, img.height, cx, cy, img.width * ratio, img.height * ratio);
        };

        renderFrame(0);

        const unsubscribe = frameIndex.on("change", (latest) => {
            cancelAnimationFrame(rafRef.current);
            rafRef.current = requestAnimationFrame(() => renderFrame(latest));
        });

        return () => {
            unsubscribe();
            cancelAnimationFrame(rafRef.current);
            window.removeEventListener("resize", updateCanvasSize);
        };
    }, [loaded, frameIndex]);

    return (
        <div ref={containerRef} className="relative z-0" style={{ height }}>
            <div className="sticky top-0 left-0 w-full h-screen overflow-hidden">
                <canvas ref={canvasRef} className="w-full h-full object-cover" />
                {!loaded && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/50 text-white z-10">
                        Loading Animation...
                    </div>
                )}
            </div>
        </div>
    );
}

// Memoize to prevent re-renders from parent state changes (e.g., file upload)
const ScrollFrameSequence = memo(ScrollFrameSequenceInner);
export default ScrollFrameSequence;
