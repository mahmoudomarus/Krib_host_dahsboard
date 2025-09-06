import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../utils/supabase/client'

export function AuthCallback() {
  const navigate = useNavigate()
  const [isProcessing, setIsProcessing] = useState(true)

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        console.log('🔄 Processing OAuth callback...')
        setIsProcessing(true)

        // First, try to get the session from the URL hash/fragment
        const { data, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('❌ Auth callback error:', error)
          navigate('/auth?error=' + encodeURIComponent(error.message))
          return
        }

        if (data.session?.user) {
          console.log('✅ Authentication successful:', data.session.user.email)
          console.log('🚀 Redirecting to dashboard...')
          
          // Small delay to ensure everything is processed
          setTimeout(() => {
            navigate('/dashboard', { replace: true })
          }, 500)
        } else {
          console.log('❌ No session found after OAuth, checking URL...')
          
          // Try to extract session from URL fragment manually if needed
          const hashParams = new URLSearchParams(window.location.hash.substring(1))
          const accessToken = hashParams.get('access_token')
          
          if (accessToken) {
            console.log('🔍 Found access token in URL, attempting to set session...')
            // Let Supabase handle the session from the URL
            const { data: sessionData, error: sessionError } = await supabase.auth.getSession()
            
            if (sessionData?.session) {
              console.log('✅ Session established from URL token')
              navigate('/dashboard', { replace: true })
              return
            }
          }
          
          console.log('❌ No valid session found, redirecting to auth')
          navigate('/auth', { replace: true })
        }
      } catch (error) {
        console.error('❌ Auth callback error:', error)
        navigate('/auth?error=' + encodeURIComponent('Authentication failed'), { replace: true })
      } finally {
        setIsProcessing(false)
      }
    }

    // Wait a moment for the URL to be fully loaded
    const timer = setTimeout(handleAuthCallback, 100)
    
    return () => clearTimeout(timer)
  }, [navigate])

  return (
    <div className="min-h-screen flex items-center justify-center krib-auth-real-estate-background">
      <div className="text-center bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-krib-lime border-t-transparent mx-auto mb-6"></div>
        <p className="text-white text-lg font-semibold hero-text-shadow">
          {isProcessing ? 'Completing authentication...' : 'Redirecting to dashboard...'}
        </p>
        <p className="text-white/70 text-sm mt-2 hero-text-shadow">
          Please wait while we sign you in
        </p>
      </div>
    </div>
  )
}
