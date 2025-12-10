import { useState, useEffect } from 'react'
import { useParams, useLocation } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card'
import { Button } from './ui/button'
import { Separator } from './ui/separator'
import { Badge } from './ui/badge'

interface BookingDetails {
  id: string
  property_title: string
  property_address: string
  check_in: string
  check_out: string
  nights: number
  guests: number
  guest_name: string
  guest_email: string
  total_amount: number
  status: string
  payment_status: string
}

export function GuestPaymentPage() {
  const { bookingId } = useParams<{ bookingId: string }>()
  const location = useLocation()
  const isSuccess = location.pathname.includes('/success')
  const [booking, setBooking] = useState<BookingDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    fetchBookingDetails()
  }, [bookingId])

  const fetchBookingDetails = async () => {
    try {
      // Use direct API URL without /api prefix since VITE_API_URL may include it
      const baseUrl = 'https://api.host.krib.ae'
      const response = await fetch(`${baseUrl}/api/guest/bookings/${bookingId}`)
      
      if (!response.ok) {
        throw new Error('Booking not found')
      }
      
      const data = await response.json()
      setBooking(data.data)
    } catch (err: any) {
      setError(err.message || 'Failed to load booking')
    } finally {
      setLoading(false)
    }
  }

  const handlePayment = async () => {
    if (!booking) return
    
    setProcessing(true)
    try {
      // Create Stripe checkout session
      const baseUrl = 'https://api.host.krib.ae'
      const response = await fetch(`${baseUrl}/api/guest/bookings/${bookingId}/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      const data = await response.json()
      
      if (data.checkout_url) {
        // Redirect to Stripe Checkout
        window.location.href = data.checkout_url
      } else {
        throw new Error('Failed to create checkout session')
      }
    } catch (err: any) {
      setError(err.message || 'Payment failed')
      setProcessing(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin h-8 w-8 border-2 border-emerald-500 border-t-transparent rounded-full"></div>
      </div>
    )
  }

  if (error || !booking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="pt-6 text-center">
            <div className="text-red-500 text-4xl mb-4">⚠️</div>
            <h2 className="text-xl font-semibold mb-2">Booking Not Found</h2>
            <p className="text-muted-foreground">{error || 'This booking does not exist or has expired.'}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Show success page after payment
  if (isSuccess || booking.payment_status === 'paid') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-emerald-50 to-white">
        <Card className="max-w-md w-full mx-4 shadow-lg">
          <CardContent className="pt-8 pb-8 text-center">
            <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-emerald-600 text-3xl">✓</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Booking Confirmed!</h2>
            <p className="text-muted-foreground mb-6">Your payment was successful.</p>
            
            {booking && (
              <div className="bg-gray-50 rounded-lg p-4 text-left mb-6">
                <h3 className="font-semibold mb-2">{booking.property_title}</h3>
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>📅 {new Date(booking.check_in).toLocaleDateString('en-AE', { weekday: 'short', month: 'short', day: 'numeric' })} - {new Date(booking.check_out).toLocaleDateString('en-AE', { weekday: 'short', month: 'short', day: 'numeric' })}</p>
                  <p>👤 {booking.guests} guests</p>
                  <p>💰 AED {booking.total_amount.toLocaleString()}</p>
                </div>
              </div>
            )}
            
            <p className="text-sm text-muted-foreground">
              Confirmation email sent to:<br/>
              <span className="font-medium text-gray-900">{booking?.guest_email}</span>
            </p>
            
            <div className="mt-6 pt-4 border-t">
              <p className="text-xs text-muted-foreground">
                The host has been notified and will be ready for your arrival.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-lg mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Complete Your Booking</h1>
          <p className="text-muted-foreground">Secure payment powered by Stripe</p>
        </div>

        {/* Booking Summary */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">{booking.property_title}</CardTitle>
            <CardDescription>{booking.property_address}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Check-in</span>
              <span className="font-medium">{new Date(booking.check_in).toLocaleDateString('en-AE', { weekday: 'short', month: 'short', day: 'numeric' })}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Check-out</span>
              <span className="font-medium">{new Date(booking.check_out).toLocaleDateString('en-AE', { weekday: 'short', month: 'short', day: 'numeric' })}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Duration</span>
              <span className="font-medium">{booking.nights} nights</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Guests</span>
              <span className="font-medium">{booking.guests} guests</span>
            </div>
            
            <Separator />
            
            <div className="flex justify-between items-center">
              <span className="text-lg font-semibold">Total</span>
              <span className="text-2xl font-bold text-emerald-600">AED {booking.total_amount.toLocaleString()}</span>
            </div>
          </CardContent>
        </Card>

        {/* Guest Info */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">Guest Details</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="font-medium">{booking.guest_name}</p>
            <p className="text-sm text-muted-foreground">{booking.guest_email}</p>
          </CardContent>
        </Card>

        {/* Pay Button */}
        <Button 
          onClick={handlePayment} 
          disabled={processing}
          className="w-full h-12 text-lg bg-emerald-600 hover:bg-emerald-700"
        >
          {processing ? (
            <>
              <span className="animate-spin mr-2">⏳</span>
              Processing...
            </>
          ) : (
            <>Pay AED {booking.total_amount.toLocaleString()}</>
          )}
        </Button>

        {/* Security Note */}
        <p className="text-center text-xs text-muted-foreground mt-4">
          🔒 Secured by Stripe. Your payment information is encrypted.
        </p>
      </div>
    </div>
  )
}

