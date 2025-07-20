'use client';

import NotesViewer from './NotesViewer';
import VideoViewer from './VideoViewer';

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

interface ContentViewerProps {
    modalType: 'notes' | 'video' | null;
    modalContent: FileData | null;
    isLoading: boolean;
}

export default function ContentViewer({ modalType, modalContent, isLoading }: ContentViewerProps) {
    if (!modalType || !modalContent) {
        return (
            <div className="text-gray-500 text-center py-8">
                <div className="text-4xl mb-4">📁</div>
                <p>No content to display</p>
            </div>
        );
    }

    const data = modalContent.data || [];

    if (modalType === 'notes') {
        return <NotesViewer data={data} isLoading={isLoading} />;
    }

    if (modalType === 'video') {
        return <VideoViewer data={data} isLoading={isLoading} />;
    }

    return (
        <div className="text-gray-500 text-center py-8">
            <div className="text-4xl mb-4">❓</div>
            <p>Unknown content type</p>
        </div>
    );
} 