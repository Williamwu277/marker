'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';

type ContentType = 'videos' | 'worksheets' | 'notes' | 'overview';

interface ContentItem {
    id: string;
    name: string;
    type: 'video' | 'pdf' | 'png';
    size: string;
    uploadedAt: string;
    thumbnail?: string;
}

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState<ContentType>('overview');
    const [isUploading, setIsUploading] = useState(false);
    const pathname = usePathname();
    /*
        {
            id: '1',
            name: 'Algebra Basics - Chapter 1',
            type: 'video',
            size: '45.2 MB',
            uploadedAt: '2024-01-15',
            thumbnail: '📹'
        },
    */
    const [content, setContent] = useState<ContentItem[]>([]);

    useEffect(() => {
        const fetchFileData = async () => {
            try {
                const response = await fetch('http://localhost:5099/get_all_files', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const newFiles: ContentItem[] = (await response.json()).files;

                setContent(newFiles);
            } catch (err) {
                alert(`Get data overview failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
            }
        };

        fetchFileData();
    }, []);

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>, uploadType: 'video' | 'file') => {
    const files = event.target.files;
    if (!files) return;

    setIsUploading(true);

    try {
        const file = files[0];

        const formData = new FormData();
        formData.append('file', file);
        formData.append('file_name', file.name);

        const uploadUrl = uploadType === 'video' ? 'http://127.0.0.1:5099/upload_video' : 'http://127.0.0.1:5099/upload_file';

        const uploadResponse = await fetch(uploadUrl, {
            method: 'POST',
            body: formData,
        });

        if (!uploadResponse.ok) {
            const errorData = await uploadResponse.json();
            throw new Error(errorData.error || 'Upload failed');
        }

        const uploadResult = await uploadResponse.json();
        console.log('Upload successful:', uploadResult);

        // Build new content item
        const newFile: ContentItem = {
            id: uploadResult.file_id,
            name: file.name,
            type: uploadType === 'video' ? 'video' : file.type.includes('pdf') ? 'pdf' : 'png',
            size: `${(file.size / 1024 / 1024).toFixed(1)} MB`,
            uploadedAt: new Date().toISOString().split('T')[0],
            thumbnail: uploadType === 'video' ? '📹' : '📄',
        };

        setContent(prev => [newFile, ...prev]);
    } catch (error) {
        alert(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
        setIsUploading(false);
    }
};

    const getContentByType = (type: ContentType) => {
        if (type === 'overview') return content;
        if (type === 'videos') return content.filter(item => item.type === 'video');
        if (type === 'worksheets') return content.filter(item => item.type === 'pdf' || item.type === 'png');
        if (type === 'notes') return content.filter(item => item.type === 'pdf' || item.type === 'png');
        return content;
    };

    const renderContentGrid = () => {
        const filteredContent = getContentByType(activeTab);

        if (filteredContent.length === 0) {
            return (
                <div className="text-center py-32">
                    <div className="text-6xl mb-4">📚</div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">No content yet</h3>
                    <p className="text-foreground/70 mb-6">Upload your first file or video to get started</p>
                </div>
            );
        }

        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredContent.map((item) => (
                    <div key={item.id} className="bg-white rounded-xl p-6 shadow-lg border border-primary/10 hover:shadow-xl transition-shadow">
                        <div className="flex items-start justify-between mb-4">
                            <div className="text-3xl">{item.thumbnail}</div>
                            <div className="text-xs text-foreground/60 bg-notebook px-2 py-1 rounded">
                                {item.type.toUpperCase()}
                            </div>
                        </div>
                        <h3 className="font-semibold text-foreground mb-2 line-clamp-2">{item.name}</h3>
                        <div className="text-sm text-foreground/60 space-y-1">
                            <p>Size: {item.size}</p>
                            <p>Uploaded: {item.uploadedAt}</p>
                        </div>
                        <div className="mt-4 flex gap-2">
                            {(item.type === 'pdf' || item.type === 'png') && (
                                <Link
                                    href={`/workspace/${item.id}`}
                                    className="bg-primary text-white px-4 py-2 rounded-lg text-sm hover:bg-secondary transition-colors flex-1 text-center"
                                >
                                    Open Workspace
                                </Link>
                            )}
                            <button className="bg-secondary/10 text-secondary px-4 py-2 rounded-lg text-sm hover:bg-secondary/20 transition-colors">
                                View
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <div className="min-h-screen bg-notebook">
            <div className="flex min-h-screen">
                {/* Sidebar */}
                <aside className="w-64 bg-white border-r border-primary/20 h-screen">
                    <div className="px-6 pb-6">
                        <Image
                            src="/marker-logo-transparent.png"
                            alt="Marker Logo"
                            width={200}
                            height={200}
                            className="w-40 h-40"
                        />
                        <h3 className="text-md font-semibold text-foreground mb-6">Your Library</h3>
                        <nav className="space-y-2">
                            {[
                                { id: 'overview', label: 'Overview', icon: '📊' },
                                { id: 'videos', label: 'Videos', icon: '📹' },
                                { id: 'worksheets', label: 'Worksheets', icon: '📄' },
                                { id: 'notes', label: 'Notes', icon: '📝' }
                            ].map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id as ContentType)}
                                    className={`w-full flex items-center space-x-3 px-4 py-2 rounded-lg text-left transition-colors ${activeTab === tab.id
                                        ? 'bg-primary text-white'
                                        : 'text-foreground hover:bg-primary/10'
                                        }`}
                                >
                                    <span className="text-lg">{tab.icon}</span>
                                    <span className="font-medium">{tab.label}</span>
                                </button>
                            ))}
                        </nav>

                        {/* Upload Section */}
                        <div className="mt-8 pt-6 border-t border-primary/20">
                            <h3 className="text-sm font-semibold text-foreground mb-4">Upload Content</h3>
                            <div className="space-y-3">
                                <label className="block">
                                    <input
                                        type="file"
                                        accept="video/*"
                                        multiple
                                        onChange={(e) => handleFileUpload(e, 'video')}
                                        className="hidden"
                                    />
                                    <div className="bg-primary/10 text-primary px-4 py-2 rounded-lg text-sm hover:bg-primary/20 transition-colors cursor-pointer text-center">
                                        📹 Upload Videos
                                    </div>
                                </label>
                                <label className="block">
                                    <input
                                        type="file"
                                        accept=".pdf, .png"
                                        multiple
                                        onChange={(e) => handleFileUpload(e, 'file')}
                                        className="hidden"
                                    />
                                    <div className="bg-secondary/10 text-secondary px-4 py-2 rounded-lg text-sm hover:bg-secondary/20 transition-colors cursor-pointer text-center">
                                        📄 Upload Files
                                    </div>
                                </label>
                            </div>
                        </div>

                        {/* Logout Section */}
                        <div className="mt-8 pt-6 border-t border-primary/20">
                            <Link
                                href="/"
                                className="w-full flex items-center space-x-3 px-4 py-2 rounded-lg text-left transition-colors text-foreground bg-notebook hover:bg-red-50 hover:text-red-600"
                            >
                                <span className="text-lg">🚪</span>
                                <span className="font-medium">Logout</span>
                            </Link>
                        </div>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="flex-1 px-12 py-16">
                    <div className="max-w-6xl mx-auto">
                        <div className="flex justify-between items-center mb-8">
                            <div>
                                <h1 className="text-3xl font-bold text-foreground mb-2">
                                    {activeTab === 'overview' && 'Your Learning Library'}
                                    {activeTab === 'videos' && 'Videos'}
                                    {activeTab === 'worksheets' && 'Worksheets'}
                                    {activeTab === 'notes' && 'Notes'}
                                </h1>
                                <p className="text-foreground/70">
                                    {activeTab === 'overview' && 'All your uploaded content in one place'}
                                    {activeTab === 'videos' && 'Your math class recordings and lectures'}
                                    {activeTab === 'worksheets' && 'Worksheets and assignments'}
                                    {activeTab === 'notes' && 'Your study notes and materials'}
                                </p>
                            </div>

                            {isUploading && (
                                <div className="flex items-center space-x-2 text-primary">
                                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary border-t-transparent"></div>
                                    <span className="text-sm">Uploading...</span>
                                </div>
                            )}
                        </div>

                        {renderContentGrid()}
                    </div>
                </main>
            </div>
        </div>
    );
} 