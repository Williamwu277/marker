'use client';

import { useState } from 'react';
import Link from 'next/link';

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

export default function Workspace({ params }: { params: { id: string } }) {
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  // Mock data - in a real app, this would come from the backend
  const problems: Problem[] = [
    {
      id: '1',
      number: 1,
      text: 'Solve for x: 2x + 5 = 13',
      relatedContent: [
        {
          id: 'v1',
          type: 'video',
          title: 'Linear Equations Basics',
          timestamp: '12:34',
          description: 'Introduction to solving linear equations with one variable',
          thumbnail: '📹'
        },
        {
          id: 'n1',
          type: 'note',
          title: 'Linear Equations Notes',
          description: 'Step-by-step guide for solving linear equations',
          thumbnail: '📝'
        }
      ]
    },
    {
      id: '2',
      number: 2,
      text: 'Find the slope of the line y = 3x - 2',
      relatedContent: [
        {
          id: 'v2',
          type: 'video',
          title: 'Slope and Linear Functions',
          timestamp: '8:45',
          description: 'Understanding slope-intercept form and calculating slope',
          thumbnail: '📹'
        }
      ]
    },
    {
      id: '3',
      number: 3,
      text: 'Factor the expression: x² - 4',
      relatedContent: [
        {
          id: 'v3',
          type: 'video',
          title: 'Factoring Polynomials',
          timestamp: '15:22',
          description: 'Difference of squares and factoring techniques',
          thumbnail: '📹'
        },
        {
          id: 'n2',
          type: 'note',
          title: 'Factoring Methods',
          description: 'Complete guide to factoring different types of polynomials',
          thumbnail: '📝'
        }
      ]
    }
  ];

  const handleProblemClick = (problem: Problem) => {
    setSelectedProblem(problem);
  };

  return (
    <div className="min-h-screen bg-notebook">
      {/* Header */}
      <header className="bg-white border-b border-primary/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="flex items-center space-x-2 text-foreground hover:text-primary transition-colors">
                <span>←</span>
                <span>Back to Dashboard</span>
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <h1 className="text-lg font-semibold text-foreground">Linear Equations Worksheet</h1>
              <div className="text-sm text-foreground/60">Page {currentPage} of 3</div>
            </div>
            <div className="flex items-center space-x-2">
              <button className="bg-primary/10 text-primary px-3 py-1 rounded text-sm hover:bg-primary/20 transition-colors">
                Download PDF
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-4rem)]">
        {/* PDF Viewer / Worksheet Area */}
        <div className="flex-1 p-6 overflow-auto">
          <div className="max-w-4xl mx-auto">
            {/* PDF Viewer Placeholder */}
            <div className="bg-white rounded-xl shadow-lg border border-primary/20 mb-6">
              <div className="p-6 border-b border-primary/20">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-foreground">Linear Equations Worksheet</h2>
                  <div className="flex items-center space-x-2">
                    <button 
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                      className="px-3 py-1 rounded bg-primary/10 text-primary hover:bg-primary/20 transition-colors disabled:opacity-50"
                    >
                      Previous
                    </button>
                    <span className="text-sm text-foreground/60">{currentPage}/3</span>
                    <button 
                      onClick={() => setCurrentPage(Math.min(3, currentPage + 1))}
                      disabled={currentPage === 3}
                      className="px-3 py-1 rounded bg-primary/10 text-primary hover:bg-primary/20 transition-colors disabled:opacity-50"
                    >
                      Next
                    </button>
                  </div>
                </div>
              </div>
              
              <div className="p-8 bg-paper min-h-[600px] rounded-b-xl">
                <div className="space-y-6">
                  {problems.map((problem) => (
                    <div
                      key={problem.id}
                      onClick={() => handleProblemClick(problem)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md ${
                        selectedProblem?.id === problem.id
                          ? 'border-primary bg-primary/5'
                          : 'border-primary/20 hover:border-primary/40'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center text-sm font-semibold">
                          {problem.number}
                        </div>
                        <div className="flex-1">
                          <p className="text-foreground font-medium">{problem.text}</p>
                          <div className="mt-2 flex items-center space-x-2">
                            <span className="text-xs text-foreground/60">
                              {problem.relatedContent.length} related content
                            </span>
                            {problem.relatedContent.length > 0 && (
                              <span className="text-xs bg-accent/20 text-accent px-2 py-1 rounded">
                                Click to view
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Related Content Sidebar */}
        <div className="w-80 bg-white border-l border-primary/20 overflow-auto">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">
              {selectedProblem ? `Problem ${selectedProblem.number} - Related Content` : 'Select a problem to view related content'}
            </h3>
            
            {selectedProblem ? (
              <div className="space-y-4">
                {selectedProblem.relatedContent.map((content) => (
                  <div key={content.id} className="bg-notebook rounded-lg p-4 border border-primary/20">
                    <div className="flex items-start space-x-3">
                      <div className="text-2xl">{content.thumbnail}</div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-foreground mb-1">{content.title}</h4>
                        {content.timestamp && (
                          <p className="text-xs text-accent mb-2">Timestamp: {content.timestamp}</p>
                        )}
                        <p className="text-sm text-foreground/70 mb-3">{content.description}</p>
                        <button className="bg-primary text-white px-3 py-1 rounded text-sm hover:bg-secondary transition-colors">
                          {content.type === 'video' ? 'Watch Video' : 'View Notes'}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">📚</div>
                <p className="text-foreground/70">
                  Click on any problem in the worksheet to see related videos and notes
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 