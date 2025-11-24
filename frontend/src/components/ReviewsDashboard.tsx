import { useState, useEffect } from "react"
import { Star, MessageSquare, TrendingUp, Filter, ChevronDown } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { Textarea } from "./ui/textarea"
import { ScrollArea } from "./ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select"
import { useApp } from "../contexts/AppContext"

interface Review {
  id: string
  booking_id: string
  property_id: string
  guest_id: string
  guest_name: string | null
  rating: number
  cleanliness_rating: number | null
  communication_rating: number | null
  checkin_rating: number | null
  accuracy_rating: number | null
  location_rating: number | null
  value_rating: number | null
  comment: string | null
  host_response: string | null
  created_at: string
  responded_at: string | null
  property_title: string | null
}

interface ReviewStats {
  total_reviews: number
  average_rating: number
  pending_responses: number
  ratings_breakdown: {
    "5": number
    "4": number
    "3": number
    "2": number
    "1": number
  }
}

export function ReviewsDashboard() {
  const { user } = useApp()
  const [reviews, setReviews] = useState<Review[]>([])
  const [stats, setStats] = useState<ReviewStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedProperty, setSelectedProperty] = useState<string>("all")
  const [properties, setProperties] = useState<Array<{ id: string; title: string }>>([])
  const [respondingTo, setRespondingTo] = useState<string | null>(null)
  const [responseText, setResponseText] = useState("")
  const [page, setPage] = useState(1)
  const [totalReviews, setTotalReviews] = useState(0)

  const loadProperties = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'https://api.host.krib.ae/api'}/properties`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            'Content-Type': 'application/json'
          }
        }
      )
      if (response.ok) {
        const data = await response.json()
        setProperties(data || [])
      }
    } catch (error) {
      console.error('Failed to load properties:', error)
    }
  }

  const loadReviews = async () => {
    if (!user) return
    
    try {
      setLoading(true)
      const propertyParam = selectedProperty !== "all" ? `&property_id=${selectedProperty}` : ""
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'https://api.host.krib.ae/api'}/v1/reviews?page=${page}&page_size=20${propertyParam}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            'Content-Type': 'application/json'
          }
        }
      )
      
      if (response.ok) {
        const data = await response.json()
        setReviews(data.reviews || [])
        setTotalReviews(data.total || 0)
      }
    } catch (error) {
      console.error('Failed to load reviews:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    if (!user) return
    
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'https://api.host.krib.ae/api'}/v1/reviews/stats`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            'Content-Type': 'application/json'
          }
        }
      )
      
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  const submitResponse = async (reviewId: string) => {
    if (!responseText.trim() || responseText.length < 10) {
      alert("Response must be at least 10 characters")
      return
    }
    
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'https://api.host.krib.ae/api'}/v1/reviews/${reviewId}/respond`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ response: responseText })
        }
      )
      
      if (response.ok) {
        setRespondingTo(null)
        setResponseText("")
        loadReviews()
        loadStats()
      } else {
        alert("Failed to submit response")
      }
    } catch (error) {
      console.error('Failed to submit response:', error)
      alert("Failed to submit response")
    }
  }

  useEffect(() => {
    loadProperties()
    loadStats()
  }, [user])

  useEffect(() => {
    loadReviews()
  }, [user, selectedProperty, page])

  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"
            }`}
          />
        ))}
      </div>
    )
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    })
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reviews</h1>
          <p className="text-muted-foreground">Manage and respond to guest reviews</p>
        </div>
      </div>

      {stats && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Reviews</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_reviews}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Rating</CardTitle>
              <Star className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.average_rating.toFixed(1)}</div>
              <div className="flex mt-2">{renderStars(stats.average_rating)}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Responses</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.pending_responses}</div>
              {stats.pending_responses > 0 && (
                <p className="text-xs text-muted-foreground mt-1">Needs your attention</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Rating Distribution</CardTitle>
              <Filter className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                {Object.entries(stats.ratings_breakdown).reverse().map(([rating, count]) => (
                  <div key={rating} className="flex items-center gap-2 text-sm">
                    <span className="w-3">{rating}</span>
                    <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-yellow-400"
                        style={{ 
                          width: `${stats.total_reviews > 0 ? (count / stats.total_reviews) * 100 : 0}%` 
                        }}
                      />
                    </div>
                    <span className="text-muted-foreground w-8 text-right">{count}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>All Reviews</CardTitle>
              <CardDescription>View and respond to guest feedback</CardDescription>
            </div>
            <Select value={selectedProperty} onValueChange={setSelectedProperty}>
              <SelectTrigger className="w-[250px]">
                <SelectValue placeholder="Filter by property" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Properties</SelectItem>
                {properties.map(property => (
                  <SelectItem key={property.id} value={property.id}>
                    {property.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading reviews...
            </div>
          ) : reviews.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <MessageSquare className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p className="text-lg">No reviews yet</p>
              <p className="text-sm">Reviews from guests will appear here</p>
            </div>
          ) : (
            <div className="space-y-4">
              {reviews.map(review => (
                <Card key={review.id}>
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold">
                              {review.guest_name || "Guest"}
                            </span>
                            {review.property_title && (
                              <>
                                <span className="text-muted-foreground">•</span>
                                <span className="text-sm text-muted-foreground">
                                  {review.property_title}
                                </span>
                              </>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            {renderStars(review.rating)}
                            <span className="text-sm text-muted-foreground">
                              {formatDate(review.created_at)}
                            </span>
                          </div>
                        </div>
                        {!review.host_response && (
                          <Badge variant="secondary">Pending Response</Badge>
                        )}
                      </div>

                      {review.comment && (
                        <p className="text-sm text-muted-foreground">{review.comment}</p>
                      )}

                      {review.cleanliness_rating && (
                        <div className="grid grid-cols-3 gap-4 pt-2 border-t">
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Cleanliness</p>
                            {renderStars(review.cleanliness_rating)}
                          </div>
                          {review.communication_rating && (
                            <div>
                              <p className="text-xs text-muted-foreground mb-1">Communication</p>
                              {renderStars(review.communication_rating)}
                            </div>
                          )}
                          {review.location_rating && (
                            <div>
                              <p className="text-xs text-muted-foreground mb-1">Location</p>
                              {renderStars(review.location_rating)}
                            </div>
                          )}
                        </div>
                      )}

                      {review.host_response && (
                        <div className="bg-accent/50 p-4 rounded-lg">
                          <p className="text-sm font-semibold mb-2">Your Response</p>
                          <p className="text-sm text-muted-foreground">{review.host_response}</p>
                          {review.responded_at && (
                            <p className="text-xs text-muted-foreground mt-2">
                              Responded on {formatDate(review.responded_at)}
                            </p>
                          )}
                        </div>
                      )}

                      {!review.host_response && (
                        <div>
                          {respondingTo === review.id ? (
                            <div className="space-y-2">
                              <Textarea
                                placeholder="Write your response (min 10 characters)..."
                                value={responseText}
                                onChange={(e) => setResponseText(e.target.value)}
                                rows={4}
                              />
                              <div className="flex gap-2">
                                <Button
                                  onClick={() => submitResponse(review.id)}
                                  disabled={responseText.length < 10}
                                >
                                  Submit Response
                                </Button>
                                <Button
                                  variant="outline"
                                  onClick={() => {
                                    setRespondingTo(null)
                                    setResponseText("")
                                  }}
                                >
                                  Cancel
                                </Button>
                              </div>
                            </div>
                          ) : (
                            <Button
                              variant="outline"
                              onClick={() => setRespondingTo(review.id)}
                            >
                              Respond to Review
                            </Button>
                          )}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}

              {totalReviews > 20 && (
                <div className="flex justify-center gap-2 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Previous
                  </Button>
                  <span className="flex items-center px-4 text-sm text-muted-foreground">
                    Page {page} of {Math.ceil(totalReviews / 20)}
                  </span>
                  <Button
                    variant="outline"
                    onClick={() => setPage(p => p + 1)}
                    disabled={page >= Math.ceil(totalReviews / 20)}
                  >
                    Next
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

