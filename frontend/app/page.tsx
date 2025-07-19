import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-notebook to-paper">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-primary/20 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">M</span>
              </div>
              <span className="text-xl font-bold text-primary">Marker</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-foreground hover:text-primary transition-colors">Features</a>
              <a href="#how-it-works" className="text-foreground hover:text-primary transition-colors">How it Works</a>
              <Link href="/dashboard" className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-secondary transition-colors">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-8">
            <h1 className="text-5xl md:text-7xl font-bold text-foreground mb-6">
              Transform Your
              <span className="block text-primary">Math Learning</span>
            </h1>
            <p className="text-xl md:text-2xl text-foreground/80 max-w-3xl mx-auto leading-relaxed">
              Upload your math videos, worksheets, and notes. Click on any problem to instantly find related content across all your materials.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <Link href="/dashboard" className="bg-primary text-white px-8 py-4 rounded-xl text-lg font-semibold hover:bg-secondary transition-all transform hover:scale-105 shadow-lg">
              Start Learning Now
            </Link>
            <button className="border-2 border-primary text-primary px-8 py-4 rounded-xl text-lg font-semibold hover:bg-primary hover:text-white transition-all">
              Watch Demo
            </button>
          </div>

          {/* Hero Visual */}
          <div className="relative max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-2xl p-8 transform rotate-1">
              <div className="bg-notebook rounded-xl p-6 border-2 border-primary/20">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  </div>
                  <span className="text-sm text-foreground/60">Worksheet.pdf</span>
                </div>
                <div className="space-y-3">
                  <div className="bg-paper rounded p-3 border-l-4 border-primary">
                    <p className="text-sm text-foreground/80">1. Solve for x: 2x + 5 = 13</p>
                  </div>
                  <div className="bg-paper rounded p-3 border-l-4 border-accent">
                    <p className="text-sm text-foreground/80">2. Find the slope of the line y = 3x - 2</p>
                  </div>
                  <div className="bg-paper rounded p-3 border-l-4 border-secondary">
                    <p className="text-sm text-foreground/80">3. Factor the expression: x² - 4</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="absolute -top-4 -right-4 bg-white rounded-xl shadow-lg p-4 transform -rotate-2">
              <div className="text-center">
                <div className="w-8 h-8 bg-primary rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white text-sm">▶</span>
                </div>
                <p className="text-xs text-foreground/60">Related Video</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 px-4 sm:px-6 lg:px-8 bg-white/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-foreground mb-4">Everything You Need to Excel in Math</h2>
            <p className="text-xl text-foreground/70 max-w-2xl mx-auto">
              Our platform connects all your learning materials in one interactive workspace
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-8 shadow-lg border border-primary/10">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <span className="text-2xl">📹</span>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-4">Upload Videos</h3>
              <p className="text-foreground/70">
                Upload your math class recordings and lectures. Our system automatically indexes key moments for easy reference.
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-lg border border-primary/10">
              <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-6">
                <span className="text-2xl">📄</span>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-4">Add Worksheets</h3>
              <p className="text-foreground/70">
                Upload PDF worksheets and assignments. Click on any problem to find related video explanations and notes.
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-lg border border-primary/10">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-6">
                <span className="text-2xl">📝</span>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-4">Organize Notes</h3>
              <p className="text-foreground/70">
                Keep your handwritten notes and study materials organized. Link them directly to specific problems and concepts.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-foreground mb-4">How It Works</h2>
            <p className="text-xl text-foreground/70 max-w-2xl mx-auto">
              Three simple steps to transform your math learning experience
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                1
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-4">Upload Your Materials</h3>
              <p className="text-foreground/70">
                Upload your math videos, worksheets, and notes to your personal workspace.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-secondary text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                2
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-4">Click on Problems</h3>
              <p className="text-foreground/70">
                Open any worksheet and click on individual problems to see related content.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-accent text-foreground rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                3
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-4">Learn Efficiently</h3>
              <p className="text-foreground/70">
                Instantly access relevant video explanations and notes for each problem.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-primary">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Ready to Transform Your Math Learning?</h2>
          <p className="text-xl text-white/90 mb-8">
            Join thousands of students who are already learning more efficiently with Marker.
          </p>
          <Link href="/dashboard" className="bg-white text-primary px-8 py-4 rounded-xl text-lg font-semibold hover:bg-gray-100 transition-all transform hover:scale-105 shadow-lg inline-block">
            Get Started Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-foreground text-white py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-6 h-6 bg-gradient-to-br from-primary to-secondary rounded flex items-center justify-center">
              <span className="text-white font-bold text-sm">M</span>
            </div>
            <span className="text-lg font-bold">Marker</span>
          </div>
          <p className="text-white/70">
            © 2024 Marker. Making math learning interactive and efficient.
          </p>
        </div>
      </footer>
    </div>
  );
}
