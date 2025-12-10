import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
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
  const [booking, setBooking] = useState<BookingDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    fetchBookingDetails()
  }, [bookingId])

  const fetchBookingDetails = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://api.host.krib.ae'}/api/guest/bookings/${bookingId}`)
      
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
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://api.host.krib.ae'}/api/guest/bookings/${bookingId}/checkout`, {
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

  if (booking.payment_status === 'paid') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="pt-6 text-center">
            <div className="text-green-500 text-4xl mb-4">✓</div>
            <h2 className="text-xl font-semibold mb-2">Payment Complete</h2>
            <p className="text-muted-foreground">This booking has already been paid.</p>
            <p className="mt-4 text-sm">Confirmation sent to: {booking.guest_email}</p>
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

