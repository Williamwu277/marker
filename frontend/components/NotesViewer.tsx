'use client';

interface NotesViewerProps {
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
}

export default function NotesViewer({ data, isLoading }: NotesViewerProps) {
    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent"></div>
                <span className="ml-3 text-gray-600">Loading notes...</span>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="text-gray-500 text-center py-8">
                <div className="text-4xl mb-4">📄</div>
                <p>No notes content available</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {data.map((page: any, index: number) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="text-sm font-medium text-gray-700">Page {index + 1}</h3>
                    </div>
                    <div className="bg-white rounded-lg p-2 shadow-sm">
                        <img 
                            src={`data:image/png;base64,${page.image}`}
                            alt={`Page ${index + 1} - Image ${index + 1}`}
                            className="w-full h-auto rounded-lg"
                            loading="lazy"
                        />
                    </div>
                    
                </div>
            ))}
        </div>
    );
} 