'use client';

interface VideoViewerProps {
    data: any[];
    isLoading: boolean;
}

export default function VideoViewer({ data, isLoading }: VideoViewerProps) {
    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent"></div>
                <span className="ml-3 text-gray-600">Loading video...</span>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="text-gray-500 text-center py-8">
                <div className="text-4xl mb-4">🎬</div>
                <p>No video content available</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {data.map((page: any, index: number) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="text-sm font-medium text-gray-700">Frame {index + 1}</h3>
                        <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded">
                            {page.images?.length || 0} frames
                        </span>
                    </div>
                    
                    {page.images && page.images.length > 0 ? (
                        <div className="space-y-3">
                            {page.images.map((image: string, imgIndex: number) => (
                                <div key={imgIndex} className="bg-white rounded-lg p-2 shadow-sm">
                                    <div className="relative">
                                        <img 
                                            src={`data:image/png;base64,${image}`}
                                            alt={`Video Frame ${index + 1} - ${imgIndex + 1}`}
                                            className="w-full h-auto rounded-lg"
                                            loading="lazy"
                                        />
                                        <div className="absolute top-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                                            Frame {imgIndex + 1}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-gray-400 text-center py-6 bg-white rounded-lg">
                            <div className="text-2xl mb-2">🎥</div>
                            <p className="text-sm">No video frames available</p>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
} 