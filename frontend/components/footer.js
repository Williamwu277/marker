import Image from 'next/image';

export default function Footer() {
  return (
    <footer className="bg-white/80 text-white py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto text-center ">
        <div className="flex items-center justify-center space-x-2 mb-4">
            <Image 
              src="/marker-logo-transparent.png" 
              alt="Marker Logo" 
              width={200} 
              height={200} 
              className="w-48 h-48"
            />
        </div>
        <p className="text-foreground">
          © 2024 Marker. Making math learning interactive and efficient.
        </p>
      </div>
    </footer>
  );
} 