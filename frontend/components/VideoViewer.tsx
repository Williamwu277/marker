'use client';

interface VideoViewerProps {
    data: FileData[];
    isLoading: boolean;
}

interface FileData {
    success: boolean;
    file_id: string;
    file_name: string;
    file_type: string;
    size: string;
    uploaded_at: string;
    data: any[];
    text_summary?: string;
    file_usage?: string;
    video_bytes?: string;
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
        <div className="space-y-6">
            {data.map((file: FileData, index: number) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h3 className="text-lg font-medium text-gray-700">{file.file_name}</h3>
                            <p className="text-sm text-gray-500">
                                Size: {file.size} • Uploaded: {new Date(file.uploaded_at).toLocaleDateString()}
                            </p>
                        </div>
                        <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded">
                            {file.file_type}
                        </span>
                    </div>
                    
                    {file.video_bytes ? (
                        <div className="bg-white rounded-lg p-2 shadow-sm">
                            <video 
                                controls
                                className="w-full h-auto rounded-lg"
                                preload="metadata"
                            >
                                <source 
                                    src={`data:video/mp4;base64,${file.video_bytes}`} 
                                    type="video/mp4" 
                                />
                                Your browser does not support the video tag.
                            </video>
                        </div>
                    ) : (
                        <div className="text-gray-400 text-center py-8 bg-white rounded-lg">
                            <div className="text-3xl mb-3">🎥</div>
                            <p className="text-sm">No video data available</p>
                            <p className="text-xs text-gray-300 mt-1">Video bytes not found</p>
                        </div>
                    )}

                    {file.text_summary && (
                        <div className="mt-4 bg-white rounded-lg p-3 shadow-sm">
                            <h4 className="text-sm font-medium text-gray-700 mb-2">Summary</h4>
                            <p className="text-sm text-gray-600">{file.text_summary}</p>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
} 