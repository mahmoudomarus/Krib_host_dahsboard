import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { supabase } from '../utils/supabase/client'
import { projectId, publicAnonKey } from '../utils/supabase/info'

interface User {
  id: string
  email: string
  name: string
}

interface Property {
  id: string
  title: string
  location: string
  propertyType: string
  bedrooms: number
  bathrooms: number
  maxGuests: number
  price: number
  description: string
  images: string[]
  amenities: string[]
  status: string
  createdAt: string
  bookings: number
  revenue: number
  rating: number
  reviews: number
}

interface Booking {
  id: string
  property: string
  propertyId: string
  guest: {
    name: string
    email: string
    phone: string
  }
  checkIn: string
  checkOut: string
  nights: number
  guests: number
  amount: number
  status: 'confirmed' | 'pending' | 'cancelled' | 'completed'
  bookingDate: string
  specialRequests?: string
}

interface AppContextType {
  user: User | null
  isLoading: boolean
  properties: Property[]
  bookings: Booking[]
  signIn: (email: string, password: string) => Promise<boolean>
  signUp: (email: string, password: string, name: string) => Promise<boolean>
  signInWithGoogle: () => Promise<boolean>
  signOut: () => Promise<void>
  createProperty: (propertyData: any) => Promise<Property | null>
  updateProperty: (id: string, updates: any) => Promise<Property | null>
  loadProperties: () => Promise<void>
  loadBookings: () => Promise<void>
  updateBooking: (id: string, updates: any) => Promise<boolean>
  getAnalytics: () => Promise<any>
}

const AppContext = createContext<AppContextType | undefined>(undefined)

const SERVER_URL = `https://${projectId}.supabase.co/functions/v1/make-server-3c640fc2`

export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [properties, setProperties] = useState<Property[]>([])
  const [bookings, setBookings] = useState<Booking[]>([])
  const [accessToken, setAccessToken] = useState<string | null>(null)

  useEffect(() => {
    checkExistingSession()
  }, [])

  const checkExistingSession = async () => {
    try {
      const { data: { session }, error } = await supabase.auth.getSession()
      if (session?.access_token) {
        setAccessToken(session.access_token)
        await loadUserProfile(session.access_token)
      }
    } catch (error) {
      console.log('Session check error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadUserProfile = async (token: string) => {
    try {
      const response = await fetch(`${SERVER_URL}/user/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUser(data.profile)
        await loadProperties()
        await loadBookings()
      }
    } catch (error) {
      console.log('Load user profile error:', error)
    }
  }

  const signIn = async (email: string, password: string): Promise<boolean> => {
    try {
      console.log('Attempting to sign in with:', { email, password: password.replace(/./g, '*') })
      
      const { data: { session }, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) {
        console.log('Supabase sign in error:', error)
        console.log('Error details:', {
          message: error.message,
          status: error.status,
          name: error.name
        })
        return false
      }

      if (session?.access_token) {
        console.log('Sign in successful, got access token')
        setAccessToken(session.access_token)
        await loadUserProfile(session.access_token)
        return true
      }

      console.log('No session or access token received')
      return false
    } catch (error) {
      console.log('Sign in process error:', error)
      return false
    }
  }

  const signUp = async (email: string, password: string, name: string): Promise<boolean> => {
    try {
      const response = await fetch(`${SERVER_URL}/signup`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${publicAnonKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password, name })
      })

      if (response.ok) {
        // After successful signup, sign the user in
        return await signIn(email, password)
      }

      const errorData = await response.json()
      console.log('Sign up error:', errorData)
      return false
    } catch (error) {
      console.log('Sign up process error:', error)
      return false
    }
  }

  const signInWithGoogle = async () => {
    try {
      const { data: { session }, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          scopes: 'openid email profile',
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })

      if (error) {
        console.log('Sign in with Google error:', error)
        
        // Provide helpful error message for common OAuth setup issues
        if (error.message.includes('provider is not enabled') || error.message.includes('Invalid provider')) {
          throw new Error('Google authentication is not properly configured. Please check the setup instructions.')
        }
        
        return false
      }

      // For OAuth, the session might not be immediately available
      // The user will be redirected and the session will be established after callback
      return true
    } catch (error) {
      console.log('Sign in with Google process error:', error)
      throw error // Re-throw to show specific error message
    }
  }

  const signOut = async () => {
    try {
      await supabase.auth.signOut()
      setUser(null)
      setAccessToken(null)
      setProperties([])
      setBookings([])
    } catch (error) {
      console.log('Sign out error:', error)
    }
  }

  const createProperty = async (propertyData: any): Promise<Property | null> => {
    if (!accessToken) return null

    try {
      const response = await fetch(`${SERVER_URL}/properties`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(propertyData)
      })

      if (response.ok) {
        const data = await response.json()
        setProperties(prev => [...prev, data.property])
        return data.property
      }

      const errorData = await response.json()
      console.log('Create property error:', errorData)
      return null
    } catch (error) {
      console.log('Create property process error:', error)
      return null
    }
  }

  const updateProperty = async (id: string, updates: any): Promise<Property | null> => {
    if (!accessToken) return null

    try {
      const response = await fetch(`${SERVER_URL}/properties/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      })

      if (response.ok) {
        const data = await response.json()
        setProperties(prev => prev.map(p => p.id === id ? data.property : p))
        return data.property
      }

      const errorData = await response.json()
      console.log('Update property error:', errorData)
      return null
    } catch (error) {
      console.log('Update property process error:', error)
      return null
    }
  }

  const loadProperties = async () => {
    if (!accessToken) return

    try {
      const response = await fetch(`${SERVER_URL}/properties`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setProperties(data.properties)
      } else {
        const errorData = await response.json()
        console.log('Load properties error:', errorData)
      }
    } catch (error) {
      console.log('Load properties process error:', error)
    }
  }

  const loadBookings = async () => {
    if (!accessToken) return

    try {
      const response = await fetch(`${SERVER_URL}/bookings`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setBookings(data.bookings)
      } else {
        const errorData = await response.json()
        console.log('Load bookings error:', errorData)
      }
    } catch (error) {
      console.log('Load bookings process error:', error)
    }
  }

  const updateBooking = async (id: string, updates: any): Promise<boolean> => {
    if (!accessToken) return false

    try {
      const response = await fetch(`${SERVER_URL}/bookings/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      })

      if (response.ok) {
        const data = await response.json()
        setBookings(prev => prev.map(b => b.id === id ? data.booking : b))
        return true
      }

      const errorData = await response.json()
      console.log('Update booking error:', errorData)
      return false
    } catch (error) {
      console.log('Update booking process error:', error)
      return false
    }
  }

  const getAnalytics = async () => {
    if (!accessToken) return null

    try {
      const response = await fetch(`${SERVER_URL}/analytics`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        return data
      }

      const errorData = await response.json()
      console.log('Get analytics error:', errorData)
      return null
    } catch (error) {
      console.log('Get analytics process error:', error)
      return null
    }
  }

  return (
    <AppContext.Provider value={{
      user,
      isLoading,
      properties,
      bookings,
      signIn,
      signUp,
      signInWithGoogle,
      signOut,
      createProperty,
      updateProperty,
      loadProperties,
      loadBookings,
      updateBooking,
      getAnalytics
    }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}