import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../utils/supabase/client'

export function AuthCallback() {
  const navigate = useNavigate()
  const [isProcessing, setIsProcessing] = useState(true)

  // Helper function to ensure user profile exists
  const ensureUserProfile = async (user: any) => {
    try {
      // Check if user profile exists
      const { data: existingProfile, error: checkError } = await supabase
        .from('users')
        .select('id')
        .eq('id', user.id)
        .single()

      if (checkError && checkError.code === 'PGRST116') {
        // Profile doesn't exist, create one
        const userName = user.user_metadata?.full_name || 
                        user.user_metadata?.name || 
                        user.email?.split('@')[0] || 
                        'User'
        
        const { error: insertError } = await supabase
          .from('users')
          .insert({
            id: user.id,
            name: userName,
            email: user.email,
            avatar_url: user.user_metadata?.avatar_url || null,
            settings: {
              notifications: { bookings: true, marketing: false, system_updates: true },
              preferences: { currency: 'AED', timezone: 'Asia/Dubai', language: 'English' }
            },
            total_revenue: 0
          })

        if (insertError) {
          console.error('[Auth] Failed to create user profile:', insertError)
        } else {
          console.log('[Auth] Created user profile for:', userName)
        }
      } else if (!checkError && existingProfile) {
        console.log('[Auth] User profile already exists')
      }
    } catch (err) {
      console.error('[Auth] Error checking/creating user profile:', err)
    }
  }

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        if (process.env.NODE_ENV === 'development') {
          console.log('[Auth] Processing OAuth callback')
        }
        setIsProcessing(true)

        // First, try to get the session from the URL hash/fragment
        const { data, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('[Auth] Callback error:', error)
          navigate('/auth?error=' + encodeURIComponent(error.message))
          return
        }

        if (data.session?.user) {
          if (process.env.NODE_ENV === 'development') {
            console.log('[Auth] Authentication successful:', data.session.user.email)
          }
          
          // Ensure user profile exists in users table
          await ensureUserProfile(data.session.user)
          
          // Small delay to ensure everything is processed
          setTimeout(() => {
            navigate('/dashboard', { replace: true })
          }, 500)
        } else {
          if (process.env.NODE_ENV === 'development') {
            console.log('[Auth] No session found, checking URL')
          }
          
          // Try to extract session from URL fragment manually if needed
          const hashParams = new URLSearchParams(window.location.hash.substring(1))
          const accessToken = hashParams.get('access_token')
          
          if (accessToken) {
            // Let Supabase handle the session from the URL
            const { data: sessionData, error: sessionError } = await supabase.auth.getSession()
            
            if (sessionData?.session) {
              navigate('/dashboard', { replace: true })
              return
            }
          }
          
          navigate('/auth', { replace: true })
        }
      } catch (error) {
        console.error('[Auth] Callback error:', error)
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
