import { useState, useEffect } from 'react'
import { useApp } from '../contexts/AppContext'
import { Card } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'
import { Textarea } from './ui/textarea'
import { Award, CheckCircle2, XCircle, Clock, TrendingUp, Star, Users, Target } from 'lucide-react'

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
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-krib-lime border-t-transparent"></div>
        </div>
      </div>
    )
  }

  const metrics = eligibility?.metrics

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Superhost Verification</h1>
          <p className="text-muted-foreground">
            Become a verified superhost and stand out to guests
          </p>
        </div>
        {status?.is_superhost && (
          <Badge className="bg-krib-lime text-krib-dark-teal px-4 py-2 text-lg">
            <Award className="w-5 h-5 mr-2" />
            Superhost
          </Badge>
        )}
      </div>

      {status?.status === 'pending' && (
        <Card className="p-6 bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800">
          <div className="flex items-start gap-4">
            <Clock className="w-8 h-8 text-yellow-600 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-100">
                Verification Pending
              </h3>
              <p className="text-yellow-800 dark:text-yellow-200 mt-1">
                Your superhost request is being reviewed by our team. You'll be notified once it's processed.
              </p>
              {status.pending_request?.created_at && (
                <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-2">
                  Requested on {new Date(status.pending_request.created_at).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>
        </Card>
      )}

      {status?.status === 'rejected' && status.pending_request?.rejection_reason && (
        <Card className="p-6 bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800">
          <div className="flex items-start gap-4">
            <XCircle className="w-8 h-8 text-red-600 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 dark:text-red-100">
                Request Not Approved
              </h3>
              <p className="text-red-800 dark:text-red-200 mt-1">
                {status.pending_request.rejection_reason}
              </p>
              <p className="text-sm text-red-700 dark:text-red-300 mt-2">
                Keep improving your metrics and try again later.
              </p>
            </div>
          </div>
        </Card>
      )}

      <div className="grid md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Target className="w-6 h-6 text-blue-600 dark:text-blue-300" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Properties</p>
              <p className="text-2xl font-bold">{metrics?.total_properties || 0}</p>
              <p className="text-xs text-muted-foreground">Minimum: 1</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
              <Users className="w-6 h-6 text-green-600 dark:text-green-300" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Bookings</p>
              <p className="text-2xl font-bold">{metrics?.total_bookings || 0}</p>
              <p className="text-xs text-muted-foreground">Minimum: 5</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <Star className="w-6 h-6 text-yellow-600 dark:text-yellow-300" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Avg Rating</p>
              <p className="text-2xl font-bold">{metrics?.average_rating?.toFixed(1) || '0.0'}</p>
              <p className="text-xs text-muted-foreground">Minimum: 4.5</p>
            </div>
          </div>
        </Card>
      </div>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Response Rate</span>
              <span className="text-sm text-muted-foreground">{metrics?.response_rate?.toFixed(1) || 0}%</span>
            </div>
            <Progress value={metrics?.response_rate || 0} className="h-2" />
            <p className="text-xs text-muted-foreground mt-1">Minimum: 90%</p>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Cancellation Rate</span>
              <span className="text-sm text-muted-foreground">{metrics?.cancellation_rate?.toFixed(1) || 0}%</span>
            </div>
            <Progress 
              value={100 - (metrics?.cancellation_rate || 0)} 
              className="h-2"
            />
            <p className="text-xs text-muted-foreground mt-1">Maximum: 5%</p>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Total Revenue</span>
              <span className="text-sm text-muted-foreground">AED {metrics?.total_revenue?.toFixed(2) || '0.00'}</span>
            </div>
          </div>
        </div>
      </Card>

      {!status?.is_superhost && status?.status !== 'pending' && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">
            {eligibility?.eligible ? 'Request Verification' : 'Eligibility Requirements'}
          </h3>

          {eligibility?.eligible ? (
            <div className="space-y-4">
              <div className="flex items-start gap-3 p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
                <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                <div>
                  <p className="font-medium text-green-900 dark:text-green-100">
                    Congratulations! You're eligible for superhost status
                  </p>
                  <p className="text-sm text-green-800 dark:text-green-200 mt-1">
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
                  rows={4}
                  maxLength={500}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  {requestMessage.length}/500 characters
                </p>
              </div>

              <Button
                onClick={handleRequestVerification}
                disabled={submitting}
                className="w-full bg-krib-lime text-krib-dark-teal hover:bg-krib-lime/90"
              >
                {submitting ? 'Submitting...' : 'Request Superhost Verification'}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-start gap-3 p-4 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800">
                <TrendingUp className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
                <div>
                  <p className="font-medium text-blue-900 dark:text-blue-100">
                    Keep growing to unlock superhost status
                  </p>
                  <p className="text-sm text-blue-800 dark:text-blue-200 mt-1">
                    Complete the requirements below to become eligible.
                  </p>
                </div>
              </div>

              {eligibility?.reasons && eligibility.reasons.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">What you need to work on:</p>
                  <ul className="space-y-2">
                    {eligibility.reasons.map((reason, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                        <XCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                        <span>{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </Card>
      )}

      {status?.is_superhost && (
        <Card className="p-6 bg-gradient-to-r from-krib-lime/20 to-krib-lime/10">
          <div className="flex items-start gap-4">
            <Award className="w-12 h-12 text-krib-lime flex-shrink-0" />
            <div>
              <h3 className="text-xl font-bold text-foreground">You're a Superhost!</h3>
              <p className="text-muted-foreground mt-2">
                Your properties are now marked with a superhost badge, helping you stand out to guests.
              </p>
              {status.approved_at && (
                <p className="text-sm text-muted-foreground mt-2">
                  Verified on {new Date(status.approved_at).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

