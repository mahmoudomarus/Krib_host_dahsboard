import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { supabase } from '../utils/supabase/client'

// API Configuration - Always use HTTPS in production
const getApiBaseUrl = () => {
  if (typeof window === 'undefined') return 'https://api.host.krib.ae/api'
  
  const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  
  if (isDevelopment) {
    return import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
  }
  
  // Production - always HTTPS
  return 'https://api.host.krib.ae/api'
}

const API_BASE_URL = getApiBaseUrl()

if (process.env.NODE_ENV === 'development') {
  console.log('[API] Configuration:', {
    hostname: window.location.hostname,
    apiUrl: API_BASE_URL,
    isDevelopment: window.location.hostname === 'localhost'
  })
}

interface User {
  id: string
  email: string
  name: string
  phone?: string
  avatar_url?: string
  settings?: {
    notifications?: {
      bookings?: boolean
      marketing?: boolean
      system_updates?: boolean
    }
    preferences?: {
      currency?: string
      timezone?: string
      language?: string
    }
  }
  total_revenue?: number
  created_at?: string
}

interface Property {
  id: string
  title: string
  description?: string
  address: string
  city: string
  state: string
  country: string
  property_type: string
  bedrooms: number
  bathrooms: number
  max_guests: number
  price_per_night: number
  amenities: string[]
  images: string[]
  status: 'draft' | 'active' | 'inactive' | 'suspended'
  rating?: number
  review_count?: number
  booking_count?: number
  total_revenue?: number
  views_count?: number
  featured?: boolean
  created_at: string
  updated_at: string
}

interface Booking {
  id: string
  property_id: string
  property_title?: string
  property_city?: string
  property_state?: string
  guest_name: string
  guest_email: string
  guest_phone?: string
  check_in: string
  check_out: string
  nights: number
  guests: number
  total_amount: number
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed' | 'no_show'
  payment_status: 'pending' | 'processing' | 'succeeded' | 'failed' | 'paid' | 'refunded' | 'partially_refunded'
  special_requests?: string
  booking_source?: string
  created_at: string
}

interface Analytics {
  total_properties: number
  total_bookings: number
  total_revenue: number
  occupancy_rate: number
  monthly_revenue: Array<{
    month_year: string
    revenue: number
    bookings: number
  }>
  property_performance: Array<{
    property_id: string
    property_title: string
    total_revenue: number
    booking_count: number
    avg_rating: number
    review_count: number
    occupancy_rate: number
  }>
}

interface AppContextType {
  // Auth state
  user: User | null
  isLoading: boolean
  
  // Data state
  properties: Property[]
  bookings: Booking[]
  analytics: Analytics | null
  
  // Auth methods
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, name: string) => Promise<void>
  signInWithGoogle: () => Promise<void>
  signOut: () => Promise<void>
  
  // Property methods
  createProperty: (propertyData: Partial<Property>) => Promise<Property>
  updateProperty: (id: string, propertyData: Partial<Property>) => Promise<Property>
  deleteProperty: (id: string) => Promise<void>
  loadProperties: () => Promise<void>
  generateAIDescription: (propertyData: Partial<Property>) => Promise<string>
  
  // Booking methods
  loadBookings: () => Promise<void>
  updateBooking: (id: string, bookingData: Partial<Booking>) => Promise<Booking>
  
  // Analytics methods
  getAnalytics: (refresh?: boolean) => Promise<any>
  
  // Financial methods
  getFinancialSummary: (period?: string) => Promise<any>
  getBankAccounts: () => Promise<any>
  addBankAccount: (accountData: any) => Promise<any>
  requestPayout: (amount: number) => Promise<any>
  getTransactions: (limit?: number) => Promise<any>
  updatePayoutSettings: (settings: any) => Promise<any>
  
  // Stripe Connect methods
  createStripeAccount: () => Promise<any>
  getStripeOnboardingLink: () => Promise<any>
  getStripeAccountStatus: () => Promise<any>
  getStripeDashboardLink: () => Promise<any>
  getHostPayouts: () => Promise<any>
  
  // Settings methods
  getUserProfile: () => Promise<User>
  updateUserProfile: (updates: Partial<User>) => Promise<User>
  updateUserSettings: (settings: any) => Promise<void>
  changePassword: (currentPassword: string, newPassword: string, confirmPassword: string) => Promise<void>
  getUserNotifications: () => Promise<any>
  updateUserNotifications: (notifications: any) => Promise<void>
  
  // UAE Location methods
  getUAEEmirates: () => Promise<any>
  getEmirateAreas: (emirate: string) => Promise<string[]>
  getPopularLocations: () => Promise<string[]>
  searchLocations: (query: string) => Promise<any>
  validateLocation: (emirate: string, area?: string) => Promise<any>
  getUAEAmenities: () => Promise<string[]>
  getUAEPropertyTypes: () => Promise<any>
  
  // Superhost methods
  checkSuperhostEligibility: () => Promise<any>
  getSuperhostStatus: () => Promise<any>
  requestSuperhostVerification: (requestMessage?: string) => Promise<any>
  
  // API method
  apiCall: (endpoint: string, method?: string, body?: any) => Promise<any>
}

const AppContext = createContext<AppContextType | null>(null)

// API utility functions
class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'APIError'
  }
}

async function makeAPIRequest(endpoint: string, options: RequestInit = {}, retryCount = 0): Promise<any> {
  try {
    // Get the current Supabase session token
    let { data: { session } } = await supabase.auth.getSession()
    
    // Check if session is expired and refresh if needed
    if (session) {
      const now = Date.now() / 1000
      const expiresAt = session.expires_at || 0
      
      if (expiresAt < now + 60) {
        console.log('[API] Token expiring soon, refreshing')
        const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession()
        
        if (refreshError || !refreshData.session) {
          console.error('[API] Token refresh failed:', refreshError)
          throw new APIError(401, 'Session expired')
        }
        
        session = refreshData.session
        localStorage.setItem('auth_token', session.access_token)
      }
    }
    
    const token = session?.access_token
    
    if (!token && retryCount === 0) {
      console.error('[API] No auth token available')
      throw new APIError(401, 'Not authenticated')
    }
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    }

    const fullUrl = `${API_BASE_URL}${endpoint}`
    
    // Only log API calls in development
    if (process.env.NODE_ENV === 'development') {
      console.log('[API Request]', endpoint)
    }
    
    const response = await fetch(fullUrl, config)
    
    // Handle 401 by refreshing token and retrying once
    if (response.status === 401 && retryCount === 0) {
      console.log('[API] 401 error, attempting token refresh')
      
      const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession()
      
      if (refreshError || !refreshData.session) {
        console.error('[API] Token refresh failed:', refreshError)
        throw new APIError(401, 'Authentication failed')
      }
      
      localStorage.setItem('auth_token', refreshData.session.access_token)
      return makeAPIRequest(endpoint, options, retryCount + 1)
    }
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Unknown error' }))
      throw new APIError(response.status, errorData.message || `HTTP ${response.status}`)
    }

    return response.json()
  } catch (error) {
    if (error instanceof APIError) {
      throw error
    }
    
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new APIError(0, 'Network error - please check your connection')
    }
    
    throw error
  }
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [properties, setProperties] = useState<Property[]>([])
  const [bookings, setBookings] = useState<Booking[]>([])
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  
  // Inactivity timeout configuration (30 minutes)
  const INACTIVITY_TIMEOUT = 30 * 60 * 1000
  let inactivityTimer: NodeJS.Timeout | null = null
  let lastActivityTime = Date.now()
  
  async function apiCall(endpoint: string, method: string = 'GET', body?: any): Promise<any> {
    return makeAPIRequest(endpoint, {
      method,
      ...(body && { body: JSON.stringify(body) }),
    })
  }

  // Track user activity
  const resetInactivityTimer = () => {
    lastActivityTime = Date.now()
    
    if (inactivityTimer) {
      clearTimeout(inactivityTimer)
    }
    
    inactivityTimer = setTimeout(async () => {
      console.log('[Auth] Inactivity timeout reached, signing out')
      await signOut()
    }, INACTIVITY_TIMEOUT)
  }

  // Initialize auth state
  useEffect(() => {
    initializeAuth()
  }, [])

  // Track user activity for inactivity timeout
  useEffect(() => {
    if (!user) return

    const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click']
    
    activityEvents.forEach(event => {
      window.addEventListener(event, resetInactivityTimer)
    })

    resetInactivityTimer()

    return () => {
      if (inactivityTimer) {
        clearTimeout(inactivityTimer)
      }
      activityEvents.forEach(event => {
        window.removeEventListener(event, resetInactivityTimer)
      })
    }
  }, [user])

  // Handle page visibility changes to refresh session
  useEffect(() => {
    if (!user) return

    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'visible') {
        console.log('[Auth] Page visible, checking session')
        
        try {
          const { data: { session }, error } = await supabase.auth.getSession()
          
          if (error) {
            console.error('[Auth] Session check error:', error)
            await signOut()
            return
          }

          if (!session) {
            console.log('[Auth] No valid session, signing out')
            await signOut()
            return
          }

          const now = Date.now() / 1000
          const expiresAt = session.expires_at || 0
          
          if (expiresAt < now) {
            console.log('[Auth] Session expired, refreshing')
            const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession()
            
            if (refreshError || !refreshData.session) {
              console.error('[Auth] Session refresh failed:', refreshError)
              await signOut()
              return
            }
            
            console.log('[Auth] Session refreshed successfully')
            localStorage.setItem('auth_token', refreshData.session.access_token)
          }

          resetInactivityTimer()
        } catch (error) {
          console.error('[Auth] Error checking session:', error)
          await signOut()
        }
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [user])

  async function initializeAuth() {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      if (session?.access_token) {
        const now = Date.now() / 1000
        const expiresAt = session.expires_at || 0
        
        if (expiresAt < now) {
          console.log('[Auth] Session expired on init, refreshing')
          const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession()
          
          if (refreshError || !refreshData.session) {
            console.error('[Auth] Session refresh failed on init:', refreshError)
            await supabase.auth.signOut()
            setIsLoading(false)
            return
          }
          
          localStorage.setItem('auth_token', refreshData.session.access_token)
          await getCurrentUser()
        } else {
          localStorage.setItem('auth_token', session.access_token)
          await getCurrentUser()
        }
      }
    } catch (error) {
      console.error('Auth initialization error:', error)
    } finally {
      setIsLoading(false)
    }

    // Listen for auth changes
    supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('[Auth] State change:', event)
      
      if (event === 'SIGNED_IN' && session?.access_token) {
        localStorage.setItem('auth_token', session.access_token)
        await getCurrentUser()
        resetInactivityTimer()
      } else if (event === 'SIGNED_OUT') {
        localStorage.removeItem('auth_token')
        setUser(null)
        setProperties([])
        setBookings([])
        setAnalytics(null)
        if (inactivityTimer) {
          clearTimeout(inactivityTimer)
        }
      } else if (event === 'TOKEN_REFRESHED' && session?.access_token) {
        console.log('[Auth] Token refreshed automatically')
        localStorage.setItem('auth_token', session.access_token)
      }
    })
  }

  async function getCurrentUser() {
    try {
      // Get user data from Supabase session instead of backend
      const { data: { session } } = await supabase.auth.getSession()
      
      if (session?.user) {
        const userName = session.user.user_metadata?.full_name || 
                        session.user.user_metadata?.name || 
                        session.user.email?.split('@')[0] || 
                        'User'
        
        // Ensure user profile exists in users table
        try {
          const { data: existingProfile, error: checkError } = await supabase
            .from('users')
            .select('id, name')
            .eq('id', session.user.id)
            .single()

          if (checkError && checkError.code === 'PGRST116') {
            // Profile doesn't exist, create one
            console.log('[Auth] Creating missing user profile...')
            const { error: insertError } = await supabase
              .from('users')
              .insert({
                id: session.user.id,
                name: userName,
                email: session.user.email,
                avatar_url: session.user.user_metadata?.avatar_url || null,
                settings: {
                  notifications: { bookings: true, marketing: false, system_updates: true },
                  preferences: { currency: 'AED', timezone: 'Asia/Dubai', language: 'English' }
                },
                total_revenue: 0
              })

            if (insertError) {
              console.error('[Auth] Failed to create user profile:', insertError)
            } else {
              console.log('[Auth] User profile created successfully')
            }
          }
        } catch (profileError) {
          console.error('[Auth] Error ensuring user profile:', profileError)
        }

        setUser({
          id: session.user.id,
          email: session.user.email || '',
          name: userName,
          created_at: session.user.created_at
        })
        
        // Automatically load user's properties and bookings when authenticated
        console.log('User authenticated with Supabase:', session.user)
        try {
          await Promise.all([
            loadProperties(),
            loadBookings()
          ])
          console.log('User data loaded successfully')
        } catch (dataError) {
          console.error('Error loading user data:', dataError)
        }
      } else {
        console.log('No Supabase session found')
      }
    } catch (error) {
      console.error('Get current user error:', error)
      localStorage.removeItem('auth_token')
    }
  }

  // Auth methods
  async function signIn(email: string, password: string) {
    try {
      setIsLoading(true)
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })
      
      if (error) throw error
      
      if (data.session?.access_token) {
        localStorage.setItem('auth_token', data.session.access_token)
        await getCurrentUser()
      }
    } catch (error: any) {
      throw new Error(error.message || 'Failed to sign in')
    } finally {
      setIsLoading(false)
    }
  }

  async function signUp(email: string, password: string, name: string) {
    try {
      setIsLoading(true)
      
      // Sign up with Supabase
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { name }
        }
      })
      
      if (error) throw error
      
      if (data.session?.access_token) {
        localStorage.setItem('auth_token', data.session.access_token)
        
        // Create user profile in our backend
        await makeAPIRequest('/auth/signup', {
          method: 'POST',
          body: JSON.stringify({ name, email })
        })
        
        await getCurrentUser()
      }
    } catch (error: any) {
      throw new Error(error.message || 'Failed to sign up')
    } finally {
      setIsLoading(false)
    }
  }

  async function signInWithGoogle() {
    try {
      console.log('Starting Google OAuth...')
      setIsLoading(true)
      
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })
      
      console.log('Google OAuth response:', { data, error })
      
      if (error) {
        console.error('Google OAuth error:', error)
        throw error
      }
      
      // The redirect will happen automatically if successful
      console.log('Google OAuth initiated successfully')
      
    } catch (error: any) {
      console.error('Google sign-in error:', error)
      setIsLoading(false)
      throw new Error(error.message || 'Failed to sign in with Google')
    }
  }

  async function signOut() {
    try {
      await supabase.auth.signOut()
      localStorage.removeItem('auth_token')
      setUser(null)
      setProperties([])
      setBookings([])
      setAnalytics(null)
      window.location.href = '/auth'
    } catch (error) {
      console.error('Sign out error:', error)
      throw error
    }
  }

  // Property methods
  async function createProperty(propertyData: Partial<Property>): Promise<Property> {
    const property = await makeAPIRequest('/properties', {
      method: 'POST',
      body: JSON.stringify(propertyData)
    })
    
    setProperties(prev => [property, ...prev])
    return property
  }

  async function updateProperty(id: string, propertyData: Partial<Property>): Promise<Property> {
    const property = await makeAPIRequest(`/properties/${id}`, {
      method: 'PUT',
      body: JSON.stringify(propertyData)
    })
    
    setProperties(prev => prev.map(p => p.id === id ? property : p))
    return property
  }

  async function deleteProperty(id: string): Promise<void> {
    await makeAPIRequest(`/properties/${id}`, {
      method: 'DELETE'
    })
    
    setProperties(prev => prev.filter(p => p.id !== id))
  }

  async function loadProperties() {
    try {
      const propertiesData = await makeAPIRequest('/properties')
      setProperties(propertiesData)
    } catch (error) {
      console.error('Load properties error:', error)
    }
  }

  async function generateAIDescription(propertyData: Partial<Property>): Promise<string> {
    const requestBody = {
      property_data: propertyData,
      use_anthropic: false  // Default to OpenAI, can be made configurable later
    }
    
    console.log('Sending AI description request:', requestBody)
    
    const response = await makeAPIRequest('/properties/ai/generate-description', {
      method: 'POST',
      body: JSON.stringify(requestBody)
    })
    
    console.log('AI description response:', response)
    return response.description
  }

  // Booking methods
  async function loadBookings() {
    try {
      const bookingsData = await makeAPIRequest('/bookings')
      setBookings(bookingsData)
    } catch (error) {
      console.error('Load bookings error:', error)
    }
  }

  async function updateBooking(id: string, bookingData: Partial<Booking>): Promise<Booking> {
    const booking = await makeAPIRequest(`/bookings/${id}`, {
      method: 'PUT',
      body: JSON.stringify(bookingData)
    })
    
    setBookings(prev => prev.map(b => b.id === id ? booking : b))
    return booking
  }

  // Analytics methods
  async function getAnalytics(refresh: boolean = false) {
    try {
      const url = refresh ? '/analytics?refresh=true' : '/analytics'
      const analyticsData = await makeAPIRequest(url)
      setAnalytics(analyticsData)
      return analyticsData
    } catch (error) {
      console.error('Get analytics error:', error)
      throw error
    }
  }

  // Financial methods
  async function getFinancialSummary(period: string = '30days') {
    try {
      return await makeAPIRequest(`/financials/summary?period=${period}`)
    } catch (error) {
      console.error('Get financial summary error:', error)
      throw error
    }
  }

  async function getBankAccounts() {
    try {
      return await makeAPIRequest('/financials/bank-accounts')
    } catch (error) {
      console.error('Get bank accounts error:', error)
      throw error
    }
  }

  async function addBankAccount(accountData: any) {
    try {
      return await makeAPIRequest('/financials/bank-accounts', {
        method: 'POST',
        body: JSON.stringify(accountData)
      })
    } catch (error) {
      console.error('Add bank account error:', error)
      throw error
    }
  }

  async function requestPayout(amount: number) {
    try {
      return await makeAPIRequest('/financials/payouts/request', {
        method: 'POST',
        body: JSON.stringify({ amount })
      })
    } catch (error) {
      console.error('Request payout error:', error)
      throw error
    }
  }

  async function getTransactions(limit: number = 50) {
    try {
      return await makeAPIRequest(`/financials/transactions?limit=${limit}`)
    } catch (error) {
      console.error('Get transactions error:', error)
      throw error
    }
  }

  async function updatePayoutSettings(settings: any) {
    try {
      return await makeAPIRequest('/financials/payout-settings', {
        method: 'PUT',
        body: JSON.stringify(settings)
      })
    } catch (error) {
      console.error('Update payout settings error:', error)
      throw error
    }
  }

  // Stripe Connect methods
  async function createStripeAccount() {
    try {
      const result = await makeAPIRequest('/v1/stripe/host/create-account', {
        method: 'POST',
        body: JSON.stringify({
          country: 'AE',
          email: user?.email || '',
          business_type: 'company'  // UAE requires 'company' business type
        })
      })
      return result.data
    } catch (error) {
      console.error('Create Stripe account error:', error)
      throw error
    }
  }

  async function getStripeOnboardingLink() {
    try {
      const result = await makeAPIRequest('/v1/stripe/host/onboarding-link', {
        method: 'POST'
      })
      return result.data
    } catch (error) {
      console.error('Get Stripe onboarding link error:', error)
      throw error
    }
  }

  async function getStripeAccountStatus() {
    try {
      const result = await makeAPIRequest('/v1/stripe/host/account-status')
      return result.data
    } catch (error) {
      console.error('Get Stripe account status error:', error)
      throw error
    }
  }

  async function getStripeDashboardLink() {
    try {
      const result = await makeAPIRequest('/v1/stripe/host/dashboard-link', {
        method: 'POST'
      })
      return result.data
    } catch (error) {
      console.error('Get Stripe dashboard link error:', error)
      throw error
    }
  }

  async function getHostPayouts() {
    try {
      const result = await makeAPIRequest('/v1/payouts/host-payouts')
      return result.data
    } catch (error) {
      console.error('Get host payouts error:', error)
      throw error
    }
  }

  // User/Settings methods
  async function getUserProfile(): Promise<User> {
    try {
      return await makeAPIRequest('/users/profile')
    } catch (error) {
      console.error('Get user profile error:', error)
      throw error
    }
  }

  async function updateUserProfile(updates: Partial<User>): Promise<User> {
    try {
      const updatedUser = await makeAPIRequest('/users/profile', {
        method: 'PUT',
        body: JSON.stringify(updates)
      })
      setUser(updatedUser)
      return updatedUser
    } catch (error) {
      console.error('Update user profile error:', error)
      throw error
    }
  }

  async function updateUserSettings(settings: any): Promise<void> {
    try {
      await makeAPIRequest('/users/settings', {
        method: 'PUT',
        body: JSON.stringify(settings)
      })
    } catch (error) {
      console.error('Update user settings error:', error)
      throw error
    }
  }

  async function changePassword(currentPassword: string, newPassword: string, confirmPassword: string): Promise<void> {
    try {
      await makeAPIRequest('/users/change-password', {
        method: 'POST',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: confirmPassword
        })
      })
    } catch (error) {
      console.error('Change password error:', error)
      throw error
    }
  }

  async function getUserNotifications(): Promise<any> {
    try {
      return await makeAPIRequest('/users/notifications')
    } catch (error) {
      console.error('Get user notifications error:', error)
      throw error
    }
  }

  async function updateUserNotifications(notifications: any): Promise<void> {
    try {
      await makeAPIRequest('/users/notifications', {
        method: 'PUT',
        body: JSON.stringify(notifications)
      })
    } catch (error) {
      console.error('Update user notifications error:', error)
      throw error
    }
  }

  // UAE Location Services
  async function getUAEEmirates(): Promise<any> {
    try {
      return await makeAPIRequest('/locations/emirates')
    } catch (error) {
      console.error('Get UAE emirates error:', error)
      throw error
    }
  }

  async function getEmirateAreas(emirate: string): Promise<string[]> {
    try {
      return await makeAPIRequest(`/locations/emirates/${emirate}/areas`)
    } catch (error) {
      console.error('Get emirate areas error:', error)
      throw error
    }
  }

  async function getPopularLocations(): Promise<string[]> {
    try {
      return await makeAPIRequest('/locations/popular')
    } catch (error) {
      console.error('Get popular locations error:', error)
      throw error
    }
  }

  async function searchLocations(query: string): Promise<any> {
    try {
      return await makeAPIRequest(`/locations/search?q=${encodeURIComponent(query)}`)
    } catch (error) {
      console.error('Search locations error:', error)
      throw error
    }
  }

  async function validateLocation(emirate: string, area?: string): Promise<any> {
    try {
      const params = new URLSearchParams({ emirate })
      if (area) params.append('area', area)
      
      return await makeAPIRequest(`/locations/validate?${params.toString()}`)
    } catch (error) {
      console.error('Validate location error:', error)
      throw error
    }
  }

  async function getUAEAmenities(): Promise<string[]> {
    try {
      return await makeAPIRequest('/locations/amenities')
    } catch (error) {
      console.error('Get UAE amenities error:', error)
      throw error
    }
  }

  async function getUAEPropertyTypes(): Promise<any> {
    try {
      return await makeAPIRequest('/locations/property-types')
    } catch (error) {
      console.error('Get UAE property types error:', error)
      throw error
    }
  }

  // Superhost methods
  async function checkSuperhostEligibility(): Promise<any> {
    try {
      return await makeAPIRequest('/superhost/eligibility')
    } catch (error) {
      console.error('Check superhost eligibility error:', error)
      throw error
    }
  }

  async function getSuperhostStatus(): Promise<any> {
    try {
      return await makeAPIRequest('/superhost/status')
    } catch (error) {
      console.error('Get superhost status error:', error)
      throw error
    }
  }

  async function requestSuperhostVerification(requestMessage?: string): Promise<any> {
    try {
      return await makeAPIRequest('/superhost/request', {
        method: 'POST',
        body: JSON.stringify({ request_message: requestMessage })
      })
    } catch (error) {
      console.error('Request superhost verification error:', error)
      throw error
    }
  }

  const contextValue: AppContextType = {
    // State
    user,
    isLoading,
    properties,
    bookings,
    analytics,
    
    // Auth methods
    signIn,
    signUp,
    signInWithGoogle,
    signOut,
    apiCall,
    
    // Property methods
    createProperty,
    updateProperty,
    deleteProperty,
    loadProperties,
    generateAIDescription,
    
    // Booking methods
    loadBookings,
    updateBooking,
    
    // Analytics methods
    getAnalytics,
    
    // Financial methods
    getFinancialSummary,
    getBankAccounts,
    addBankAccount,
    requestPayout,
    getTransactions,
    updatePayoutSettings,
    
    // User/Settings methods
    getUserProfile,
    updateUserProfile,
    updateUserSettings,
    changePassword,
    getUserNotifications,
    updateUserNotifications,
    
    // UAE Location methods
    getUAEEmirates,
    getEmirateAreas,
    getPopularLocations,
    searchLocations,
    validateLocation,
    getUAEAmenities,
    getUAEPropertyTypes,
    
    // Stripe Connect methods
    createStripeAccount,
    getStripeOnboardingLink,
    getStripeAccountStatus,
    getStripeDashboardLink,
    getHostPayouts,
    
    // Superhost methods
    checkSuperhostEligibility,
    getSuperhostStatus,
    requestSuperhostVerification,
  }

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}