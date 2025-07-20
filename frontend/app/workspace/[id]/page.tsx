'use client';

import { useState, useEffect } from 'react';
import { use } from 'react';
import Link from 'next/link';
import Image from 'next/image';

interface TextBlock {
    bounding_box: [number, number][];
    text: string;
}

interface PageData {
    image: string;
    dimensions: [number, number];
    text_blocks: TextBlock[];
}

interface FileData {
    success: boolean;
    file_id: string;
    file_name: string;
    data: PageData[];
    video_bytes?: string;
}

interface RelatedContent {
    id: string;
    type: 'video' | 'note';
    title: string;
    timestamp?: string;
    description: string;
    thumbnail: string;
}

interface Problem {
    id: string;
    number: number;
    text: string;
    relatedContent: RelatedContent[];
}

export default function Workspace({ params }: { params: Promise<{ id: string }> }) {
    const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
    const [currentPage, setCurrentPage] = useState(0);
    const [fileData, setFileData] = useState<FileData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [clickedBlock, setClickedBlock] = useState<number>(-1);
    const [imageRef, setImageRef] = useState<HTMLImageElement | null>(null);
    const resolvedParams = use(params);
    const [searchResults, setSearchResults] = useState<any>(null);

    // Fetch file data from backend
    useEffect(() => {
        const fetchFileData = async () => {
            try {
                setLoading(true);
                const response = await fetch('http://localhost:5099/get_file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        file_id: resolvedParams.id
                    }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data: FileData = await response.json();
                setFileData(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch PDF or PNG data');
            } finally {
                setLoading(false);
            }
        };

        fetchFileData();
    }, [resolvedParams.id]);

    const handleProblemClick = (problem: Problem) => {
        setSelectedProblem(problem);
    };

    const handleBlockClick = async (blockIndex: number) => {
    setClickedBlock(blockIndex);

    const blockText = fileData?.data[currentPage].text_blocks[blockIndex].text;

    if (!blockText) return;

    try {
        const response = await fetch('http://localhost:5099/search_embeddings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: blockText,
                file_id: resolvedParams.id
            }),
        });

        if (!response.ok) {
            throw new Error(`Search failed: ${response.status}`);
        }

        const data = await response.json();
        setSearchResults(data); // Store it for display

    } catch (err) {
        console.error("Error sending block text:", err);
    }
};

   };

    // Calculate relative positions for the interactive elements
    const getBlockStyle = (boundingBox: [number, number][], imageDimensions: [number, number]) => {
        const [originalWidth, originalHeight] = imageDimensions;

        // Find the bounding rectangle
        const xCoords = boundingBox.map(point => point[0]);
        const yCoords = boundingBox.map(point => point[1]);

        const minX = Math.min(...xCoords) - 10;
        const maxX = Math.max(...xCoords) + 10;
        const minY = Math.min(...yCoords) - 10;
        const maxY = Math.max(...yCoords) + 10;

        // Convert to percentages for responsive positioning
        const left = (minX / originalWidth) * 100;
        const top = (minY / originalHeight) * 100;
        const blockWidth = ((maxX - minX) / originalWidth) * 100;
        const blockHeight = ((maxY - minY) / originalHeight) * 100;

        return {
            position: 'absolute' as const,
            left: `${left}%`,
            top: `${top}%`,
            width: `${blockWidth}%`,
            height: `${blockHeight}%`,
            borderRadius: '10px',
        };
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-notebook flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-foreground/70">Loading worksheet...</p>
                </div>
            </div>
        );
    }

    if (error || !fileData) {
        return (
            <div className="min-h-screen bg-notebook flex items-center justify-center">
                <div className="text-center">
                    <div className="text-4xl mb-4">❌</div>
                    <p className="text-foreground/70 mb-4">Failed to load worksheet</p>
                    <p className="text-sm text-foreground/50">{error}</p>
                    <Link href="/dashboard" className="mt-4 inline-block bg-primary text-white px-4 py-2 rounded hover:bg-secondary transition-colors">
                        Back to Dashboard
                    </Link>
                </div>
            </div>
        );
    }

    const currentPageData = fileData.data[currentPage];
    const totalPages = fileData.data.length;

    return (
        <div className="min-h-screen bg-notebook">
            {/* Header */}
            <header className="bg-white border-b border-primary/20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-20">
                        <div className="flex items-center space-x-4">
                            <Image
                                src="/marker-logo-transparent.png"
                                alt="Marker Logo"
                                width={200}
                                height={200}
                                className="w-40 h-40"
                            />
                        </div>
                        <div className="flex items-center space-x-4">
                            <h1 className="text-lg font-semibold text-foreground">{fileData.file_name}</h1>
                        </div>
                        <div className="flex items-center space-x-2">
                            <Link href="/dashboard" className="flex items-center space-x-2 text-foreground hover:text-primary transition-colors">
                                <span>Back to Dashboard</span>
                                <span>→</span>
                            </Link>
                        </div>
                    </div>
                </div>
            </header>

            <div className="flex h-[calc(100vh-4rem)]">
                {/* File Viewer / Worksheet Area */}
                <div className="flex-1 p-6 overflow-auto">
                    <div className="max-w-4xl mx-auto">
                        {/* File Viewer */}
                        <div className="bg-white rounded-xl shadow-lg border border-primary/20 mb-6">
                            <div className="p-6 border-b border-primary/20">
                                <div className="flex items-center justify-between">
                                    <h2 className="text-xl font-semibold text-foreground">{fileData.file_name}</h2>
                                    <div className="flex items-center space-x-2">
                                        <button
                                            onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                                            disabled={currentPage === 0}
                                            className="px-3 py-1 rounded bg-primary/10 text-primary hover:bg-primary/20 transition-colors disabled:opacity-50"
                                        >
                                            Previous
                                        </button>
                                        <span className="text-sm text-foreground/60">{currentPage + 1}/{totalPages}</span>
                                        <button
                                            onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
                                            disabled={currentPage === totalPages - 1}
                                            className="px-3 py-1 rounded bg-primary/10 text-primary hover:bg-primary/20 transition-colors disabled:opacity-50"
                                        >
                                            Next
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div className="p-8 bg-paper rounded-b-xl">
                                {/* Image Container with Interactive Elements */}
                                <div className="relative inline-block">
                                    <img
                                        ref={setImageRef}
                                        src={`data:image/png;base64,${currentPageData.image}`}
                                        alt={`Page ${currentPage + 1}`}
                                        className="max-w-full h-auto"
                                        style={{
                                            maxWidth: '100%',
                                            height: 'auto'
                                        }}
                                    />

                                    {/* Interactive Text Blocks */}
                                    {currentPageData.text_blocks.map((block, index) => (
                                        <div
                                            key={index}
                                            onClick={() => handleBlockClick(index)}
                                            className={`absolute cursor-pointer transition-all duration-200 hover:bg-primary/20 ${clickedBlock === index ? 'bg-primary/50' : 'bg-transparent'
                                                }`}
                                            style={getBlockStyle(block.bounding_box, currentPageData.dimensions)}
                                            title={block.text}
                                        />
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Related Content Sidebar */}
                <div className="w-100 bg-white border-l border-primary/20 overflow-auto">
                    <div className="p-6">
                        <h3 className="text-lg font-semibold text-foreground mb-4">
                            Memory Museum
                        </h3>

                        <div className="space-y-4">
                            {currentPageData.text_blocks.map((block, index) => (
                                <div
                                    key={index}
                                    className={`p-3 rounded-lg border cursor-pointer transition-all ${clickedBlock === index}
                                            ? 'border-red-500 bg-red-50'
                                            : 'border-primary/20 hover:border-primary/40'
                                        }`}
                                    onClick={() => handleBlockClick(index)}
                                >
                                    <div className="flex items-start space-x-2">
                                        <div className={`w-4 h-4 rounded-full flex-shrink-0 mt-1 ${clickedBlock === index ? 'bg-red-500' : 'bg-primary/20'
                                            }`}></div>
                                        <div className="flex-1">
                                            <p className="text-sm text-foreground/80 leading-relaxed">
                                                {block.text}
                                            </p>
                                            <p className="text-xs text-foreground/50 mt-1">
                                                Block {index + 1}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
} 