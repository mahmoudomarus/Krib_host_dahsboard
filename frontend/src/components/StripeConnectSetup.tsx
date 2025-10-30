import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { Alert, AlertDescription } from "./ui/alert"
import { 
  CheckCircle, 
  AlertCircle, 
  ExternalLink,
  CreditCard,
  Building2,
  Clock
} from "lucide-react"
import { useApp } from "../contexts/AppContext"

interface StripeAccountStatus {
  stripe_account_id?: string
  status: string
  charges_enabled: boolean
  payouts_enabled: boolean
  details_submitted: boolean
  onboarding_completed: boolean
  bank_account_last4?: string
  bank_account_country?: string
  requirements?: {
    currently_due: string[]
    eventually_due: string[]
    past_due: string[]
  }
}

export function StripeConnectSetup() {
  const { 
    createStripeAccount, 
    getStripeOnboardingLink, 
    getStripeAccountStatus,
    getStripeDashboardLink
  } = useApp()
  
  const [accountStatus, setAccountStatus] = useState<StripeAccountStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    loadAccountStatus()
  }, [])

  async function loadAccountStatus() {
    try {
      setLoading(true)
      const status = await getStripeAccountStatus()
      setAccountStatus(status)
    } catch (error: any) {
      if (error.message?.includes('not found') || error.message?.includes('404')) {
        setAccountStatus({ status: 'not_connected', charges_enabled: false, payouts_enabled: false, details_submitted: false, onboarding_completed: false })
      }
    } finally {
      setLoading(false)
    }
  }

  async function handleSetupPayouts() {
    try {
      setProcessing(true)
      
      // Create account if doesn't exist
      if (!accountStatus?.stripe_account_id) {
        await createStripeAccount()
      }
      
      // Get onboarding link
      const { url } = await getStripeOnboardingLink()
      
      // Redirect to Stripe
      window.location.href = url
    } catch (error) {
      console.error('Setup payouts error:', error)
      alert('Failed to start payout setup. Please try again.')
      setProcessing(false)
    }
  }

  async function handleOpenDashboard() {
    try {
      setProcessing(true)
      const { url } = await getStripeDashboardLink()
      window.open(url, '_blank')
    } catch (error) {
      console.error('Open dashboard error:', error)
      alert('Failed to open Stripe dashboard')
    } finally {
      setProcessing(false)
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Payout Setup</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-3">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const getStatusBadge = () => {
    if (!accountStatus) return null
    
    if (accountStatus.payouts_enabled) {
      return <Badge className="bg-green-100 text-green-800"><CheckCircle className="h-3 w-3 mr-1" /> Active</Badge>
    } else if (accountStatus.details_submitted) {
      return <Badge className="bg-blue-100 text-blue-800"><Clock className="h-3 w-3 mr-1" /> Pending Verification</Badge>
    } else {
      return <Badge className="bg-yellow-100 text-yellow-800"><AlertCircle className="h-3 w-3 mr-1" /> Setup Required</Badge>
    }
  }

  const hasRequirements = accountStatus?.requirements && (
    accountStatus.requirements.currently_due.length > 0 ||
    accountStatus.requirements.past_due.length > 0
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Payout Account</span>
          {getStatusBadge()}
        </CardTitle>
        <CardDescription>
          Powered by Stripe - Secure bank account setup for receiving payouts
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {accountStatus?.status === 'not_connected' ? (
          <>
            <Alert>
              <Building2 className="h-4 w-4" />
              <AlertDescription>
                Set up your bank account to receive payouts from bookings. Stripe handles all KYC verification and bank details securely.
              </AlertDescription>
            </Alert>
            <Button onClick={handleSetupPayouts} disabled={processing} className="w-full">
              <CreditCard className="h-4 w-4 mr-2" />
              {processing ? 'Redirecting...' : 'Set Up Payouts'}
            </Button>
          </>
        ) : accountStatus?.payouts_enabled ? (
          <>
            <div className="p-4 border rounded-lg bg-green-50">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="font-medium text-green-900">Payouts Enabled</span>
              </div>
              <p className="text-sm text-green-700">
                Your account is fully verified and ready to receive payouts.
              </p>
              {accountStatus.bank_account_last4 && (
                <p className="text-sm text-green-700 mt-1">
                  Bank account ending in ****{accountStatus.bank_account_last4}
                </p>
              )}
            </div>
            <Button variant="outline" onClick={handleOpenDashboard} disabled={processing} className="w-full">
              <ExternalLink className="h-4 w-4 mr-2" />
              Open Stripe Dashboard
            </Button>
          </>
        ) : (
          <>
            {hasRequirements && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Additional information required to activate payouts. 
                  {accountStatus?.requirements?.past_due && accountStatus.requirements.past_due.length > 0 && (
                    <span className="text-red-600 font-medium"> Action required!</span>
                  )}
                </AlertDescription>
              </Alert>
            )}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                {accountStatus?.details_submitted ? <CheckCircle className="h-4 w-4 text-green-600" /> : <Clock className="h-4 w-4 text-gray-400" />}
                <span>Information submitted</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                {accountStatus?.charges_enabled ? <CheckCircle className="h-4 w-4 text-green-600" /> : <Clock className="h-4 w-4 text-gray-400" />}
                <span>Charges enabled</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                {accountStatus?.payouts_enabled ? <CheckCircle className="h-4 w-4 text-green-600" /> : <Clock className="h-4 w-4 text-gray-400" />}
                <span>Payouts enabled</span>
              </div>
            </div>
            <Button onClick={handleSetupPayouts} disabled={processing} className="w-full">
              {processing ? 'Redirecting...' : 'Continue Setup'}
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  )
}

