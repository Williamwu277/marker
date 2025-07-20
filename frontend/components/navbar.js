'use client';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useAuth0 } from '@auth0/auth0-react';

export default function Navbar() {
  const pathname = usePathname();
  const { loginWithRedirect, logout, isAuthenticated } = useAuth0();

  return (
    <nav className={`fixed z-50 top-0 w-full bg-white/80 backdrop-blur-sm`}>
      <div className={`${pathname === '/dashboard' ? 'max-w-[90rem]' : 'max-w-7xl'} mx-auto px-4 sm:px-6 lg:px-8`}>
        <div className="flex justify-between items-center h-20 relative">
          {/* Logo on the left */}
          <div className="flex items-center">
            <Image
              src="/marker-logo-transparent.png"
              alt="Marker Logo"
              width={200}
              height={200}
              className="w-48 h-48"
            />
          </div>

          {/* Navigation links in the center */}
          {pathname !== '/dashboard' && (
            <div className="hidden md:flex items-center space-x-8 absolute left-1/2 transform -translate-x-1/2">
              <a href="#demo" className="text-foreground hover:text-primary transition-colors">Demo</a>
              <a href="#features" className="text-foreground hover:text-primary transition-colors">Features</a>
              <a href="#how-it-works" className="text-foreground hover:text-primary transition-colors">How it Works</a>
              <a href="#get-started-now" className="text-foreground hover:text-primary transition-colors">Get Started</a>
            </div>
          )}

          {/* Auth Button */}
          <div className="flex items-center">
            {!isAuthenticated ? (
              <button
                onClick={() => loginWithRedirect()}
                className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-secondary transition-colors"
              >
                Login
              </button>
            ) : (
              <button
                onClick={() => logout({ returnTo: window.location.origin })}
                className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-secondary transition-colors"
              >
                Logout
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
// Note: The above code assumes you have the necessary Auth0 setup in your Next.js application.
// Make sure to replace the logo path with your actual logo image path.