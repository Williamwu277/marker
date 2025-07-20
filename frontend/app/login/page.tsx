'use client'

import { useAuth0 } from '@auth0/auth0-react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function LoginPage() {
  const { user, error, isLoading } = useAuth0()
  const router = useRouter()

  useEffect(() => {
    // Redirect to home/dashboard if already logged in
    if (user) {
      router.push('/')
    }
  }, [user, router])

  if (isLoading) return <p>Loading...</p>
  if (error) return <p>Error: {error.message}</p>

  return (
    <main className="flex flex-col items-center justify-center h-screen text-center">
      <h1 className="text-3xl font-bold mb-6">Welcome to Marker</h1>
      <p className="mb-8 text-gray-600">Please log in to continue</p>
      <a
        href="/api/auth/login"
        className="px-6 py-3 text-white bg-blue-600 rounded hover:bg-blue-700 transition"
      >
        Log In
      </a>
    </main>
  )
}
