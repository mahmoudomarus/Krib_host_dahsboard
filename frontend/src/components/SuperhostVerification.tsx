import { useState, useEffect } from 'react'
import { useApp } from '../contexts/AppContext'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'
import { Textarea } from './ui/textarea'
import { Award, CheckCircle2, XCircle, Clock, TrendingUp, Star, Users, Target, AlertCircle, Home } from 'lucide-react'

interface EligibilityData {
  eligible: boolean
  reasons: string[]
  metrics: {
    total_properties: number
    total_bookings: number
    total_revenue: number
    average_rating: number
    response_rate: number
    cancellation_rate: number
  }
}

interface VerificationStatus {
  is_superhost: boolean
  status: 'regular' | 'pending' | 'approved' | 'rejected'
  requested_at?: string
  approved_at?: string
  pending_request?: {
    id: string
    status: string
    created_at: string
    rejection_reason?: string
  }
}

export function SuperhostVerification() {
  const { checkSuperhostEligibility, getSuperhostStatus, requestSuperhostVerification } = useApp()
  const [loading, setLoading] = useState(true)
  const [eligibility, setEligibility] = useState<EligibilityData | null>(null)
  const [status, setStatus] = useState<VerificationStatus | null>(null)
  const [requestMessage, setRequestMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [eligibilityRes, statusRes] = await Promise.all([
        checkSuperhostEligibility(),
        getSuperhostStatus()
      ])
      setEligibility(eligibilityRes)
      setStatus(statusRes)
    } catch (error) {
      console.error('[Superhost] Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRequestVerification = async () => {
    if (!eligibility?.eligible) return

    try {
      setSubmitting(true)
      await requestSuperhostVerification(requestMessage || undefined)
      await loadData()
      setRequestMessage('')
    } catch (error) {
      console.error('[Superhost] Error requesting verification:', error)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-emerald-500 border-t-transparent"></div>
        </div>
      </div>
    )
  }

  const metrics = eligibility?.metrics

  // Define requirements with their thresholds
  const requirements = [
    {
      label: 'Properties',
      value: metrics?.total_properties || 0,
      required: 1,
      type: 'min',
      icon: Home,
      color: 'blue'
    },
    {
      label: 'Completed Bookings',
      value: metrics?.total_bookings || 0,
      required: 5,
      type: 'min',
      icon: Users,
      color: 'green'
    },
    {
      label: 'Average Rating',
      value: metrics?.average_rating || 0,
      required: 4.5,
      type: 'min',
      icon: Star,
      color: 'yellow',
      format: (v: number) => v.toFixed(1)
    },
    {
      label: 'Response Rate',
      value: metrics?.response_rate || 0,
      required: 90,
      type: 'min',
      icon: Target,
      color: 'purple',
      format: (v: number) => `${v.toFixed(0)}%`
    },
    {
      label: 'Cancellation Rate',
      value: metrics?.cancellation_rate || 0,
      required: 5,
      type: 'max',
      icon: AlertCircle,
      color: 'orange',
      format: (v: number) => `${v.toFixed(1)}%`
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Superhost Verification</h1>
          <p className="text-muted-foreground">
            Become a verified superhost and stand out to guests
          </p>
        </div>
        {status?.is_superhost && (
          <Badge className="bg-emerald-100 text-emerald-800 px-4 py-2 text-lg">
            <Award className="w-5 h-5 mr-2" />
            Superhost
          </Badge>
        )}
      </div>

      {/* Status Alerts */}
      {status?.status === 'pending' && (
        <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <Clock className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
            <p className="font-medium text-amber-900">Verification Pending</p>
            <p className="text-sm text-amber-800 mt-0.5">
              Your request is being reviewed. You'll be notified once it's processed.
              </p>
          </div>
        </div>
      )}

      {status?.status === 'rejected' && status.pending_request?.rejection_reason && (
        <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
            <p className="font-medium text-red-900">Request Not Approved</p>
            <p className="text-sm text-red-800 mt-0.5">{status.pending_request.rejection_reason}</p>
          </div>
        </div>
      )}

      {/* Requirements Card - Single Consolidated View */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Requirements Progress
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {requirements.map((req, index) => {
            const Icon = req.icon
            const isMet = req.type === 'min' 
              ? req.value >= req.required 
              : req.value <= req.required
            const progress = req.type === 'min'
              ? Math.min((req.value / req.required) * 100, 100)
              : Math.max(100 - (req.value / req.required) * 100, 0)
            
            return (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Icon className={`h-4 w-4 ${isMet ? 'text-emerald-500' : 'text-muted-foreground'}`} />
                    <span className="font-medium">{req.label}</span>
            </div>
                  <div className="flex items-center gap-2">
                    <span className={isMet ? 'text-emerald-600 font-medium' : ''}>
                      {req.format ? req.format(req.value) : req.value}
                    </span>
                    <span className="text-muted-foreground">/</span>
                    <span className="text-muted-foreground text-xs">
                      {req.type === 'min' ? 'min' : 'max'} {req.format ? req.format(req.required) : req.required}
                    </span>
                    {isMet ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-muted-foreground" />
                    )}
            </div>
            </div>
            <Progress 
                  value={progress} 
                  className={`h-2 ${isMet ? '[&>div]:bg-emerald-500' : ''}`}
            />
          </div>
            )
          })}

          {/* Revenue - informational only, no requirement */}
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">Total Revenue</span>
              </div>
              <span className="font-medium">AED {metrics?.total_revenue?.toFixed(2) || '0.00'}</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">For your reference (no minimum required)</p>
          </div>
        </CardContent>
      </Card>

      {/* Action Card */}
      {!status?.is_superhost && status?.status !== 'pending' && (
        <Card>
          <CardContent className="pt-6">
          {eligibility?.eligible ? (
            <div className="space-y-4">
                <div className="flex items-start gap-3 p-4 bg-emerald-50 rounded-lg">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <div>
                    <p className="font-medium text-emerald-900">
                      You're eligible for superhost status!
                  </p>
                    <p className="text-sm text-emerald-800 mt-0.5">
                    Submit your request and our team will review it within 2-3 business days.
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Message to Admin (Optional)
                </label>
                <Textarea
                  value={requestMessage}
                  onChange={(e) => setRequestMessage(e.target.value)}
                  placeholder="Tell us why you'd be a great superhost..."
                    rows={3}
                  maxLength={500}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  {requestMessage.length}/500 characters
                </p>
              </div>

              <Button
                onClick={handleRequestVerification}
                disabled={submitting}
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white"
              >
                {submitting ? 'Submitting...' : 'Request Superhost Verification'}
              </Button>
            </div>
          ) : (
              <div className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg">
                <TrendingUp className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-blue-900">Keep growing to unlock superhost status</p>
                  <p className="text-sm text-blue-800 mt-0.5">
                    Complete all requirements above to become eligible for verification.
                  </p>
                </div>
                </div>
              )}
          </CardContent>
        </Card>
      )}

      {/* Superhost Badge */}
      {status?.is_superhost && (
        <Card className="bg-gradient-to-r from-emerald-50 to-emerald-100/50">
          <CardContent className="pt-6">
          <div className="flex items-start gap-4">
              <Award className="w-12 h-12 text-emerald-600 flex-shrink-0" />
            <div>
                <h3 className="text-xl font-bold">You're a Superhost!</h3>
                <p className="text-muted-foreground mt-1">
                Your properties are now marked with a superhost badge, helping you stand out to guests.
              </p>
              {status.approved_at && (
                <p className="text-sm text-muted-foreground mt-2">
                  Verified on {new Date(status.approved_at).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
