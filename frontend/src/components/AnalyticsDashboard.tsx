import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { Progress } from "./ui/progress"
import { Alert, AlertDescription, AlertTitle } from "./ui/alert"
import { TrendingUp, TrendingDown, DollarSign, Calendar, Users, Star, Eye, Heart, Target, Brain, Download, BarChart3, PieChart, AlertTriangle, CheckCircle, Zap, MapPin, Clock, Activity } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart as RechartsPieChart, Pie, Cell, AreaChart, Area, ComposedChart, Scatter, ScatterChart } from "recharts"
import { useApp } from "../contexts/AppContext"

// Real forecast data will be loaded from API

// All market data will be loaded from real Dubai market API

export function AnalyticsDashboard() {
  const { getAnalytics } = useApp()
  const [analyticsData, setAnalyticsData] = useState<any>(null)
  const [selectedPeriod, setSelectedPeriod] = useState("12months")
  const [loading, setLoading] = useState(true)
  const [marketInsights, setMarketInsights] = useState<any>(null)
  const [forecastData, setForecastData] = useState<any>(null)

  useEffect(() => {
    const loadAnalytics = async () => {
      setLoading(true)
      try {
        console.log('Loading analytics data...')
        const data = await getAnalytics()
        console.log('Analytics data received:', data)
        setAnalyticsData(data)
        
        // Extract market insights and forecast from the analytics data
        if (data.market_insights) {
          setMarketInsights(data.market_insights)
        }
        if (data.forecast) {
          setForecastData(data.forecast)
        }
      } catch (error) {
        console.error('Failed to load analytics:', error)
        console.error('Error details:', error.message, error.status)
        // Set some default data so the page isn't completely empty
        setAnalyticsData({
          totalRevenue: 0,
          totalBookings: 0,
          totalProperties: 0,
          occupancyRate: 0,
          monthlyData: [],
          propertyPerformance: []
        })
      } finally {
        setLoading(false)
      }
    }

    loadAnalytics()
  }, [selectedPeriod])

  const exportReport = () => {
    // Mock export functionality
    const data = {
      period: selectedPeriod,
      revenue: analyticsData?.totalRevenue || 0,
      bookings: analyticsData?.totalBookings || 0,
      properties: analyticsData?.totalProperties || 0,
      occupancyRate: analyticsData?.occupancyRate || 0,
      forecast: forecastData,
      marketComparison: marketComparisonData,
      generatedAt: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `analytics-report-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-64"></div>
          <div className="grid gap-4 md:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-muted rounded"></div>
            ))}
          </div>
          <div className="h-96 bg-muted rounded"></div>
        </div>
      </div>
    )
  }

  const revenueData = analyticsData?.monthlyData || []
  const propertyPerformance = analyticsData?.propertyPerformance || []
  
  const topMetrics = [
    {
      title: "Total Revenue",
      value: `$${analyticsData?.totalRevenue?.toLocaleString() || '0'}`,
      change: "+12.5%",
      trend: "up",
      icon: DollarSign,
      color: "text-green-600"
    },
    {
      title: "Total Bookings",
      value: analyticsData?.totalBookings?.toString() || '0',
      change: "+8.3%",
      trend: "up",
      icon: Calendar,
      color: "text-blue-600"
    },
    {
      title: "Average Rating",
      value: "4.8",
      change: "+0.2",
      trend: "up",
      icon: Star,
      color: "text-yellow-600"
    },
    {
      title: "Occupancy Rate",
      value: `${analyticsData?.occupancyRate || 0}%`,
      change: "-2.1%",
      trend: "down",
      icon: Users,
      color: "text-purple-600"
    }
  ]

  const occupancyData = [
    { name: 'Occupied', value: analyticsData?.occupancyRate || 0, color: '#22c55e' },
    { name: 'Available', value: 100 - (analyticsData?.occupancyRate || 0), color: '#e5e7eb' }
  ]

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="mb-2">Advanced Analytics</h1>
          <p className="text-muted-foreground">
            AI-powered insights and market intelligence for your rental business.
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={exportReport} variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7days">Last 7 days</SelectItem>
              <SelectItem value="30days">Last 30 days</SelectItem>
              <SelectItem value="3months">Last 3 months</SelectItem>
              <SelectItem value="12months">Last 12 months</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* AI Insights Alert */}
      <Alert>
        <Brain className="h-4 w-4" />
        <AlertTitle>AI Insights</AlertTitle>
        <AlertDescription>
          Based on market analysis, you could increase revenue by 18% by optimizing pricing for the next 30 days.
        </AlertDescription>
      </Alert>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {topMetrics.map((metric) => (
          <Card key={metric.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm">{metric.title}</CardTitle>
              <metric.icon className={`h-4 w-4 ${metric.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
              <div className="flex items-center text-xs text-muted-foreground">
                {metric.trend === 'up' ? (
                  <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
                ) : (
                  <TrendingDown className="h-3 w-3 text-red-600 mr-1" />
                )}
                {metric.change} from last period
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="revenue" className="space-y-4">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="revenue">Revenue</TabsTrigger>
          <TabsTrigger value="forecast">Forecast</TabsTrigger>
          <TabsTrigger value="market">Market</TabsTrigger>
          <TabsTrigger value="pricing">Pricing</TabsTrigger>
          <TabsTrigger value="competition">Competition</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="occupancy">Occupancy</TabsTrigger>
        </TabsList>

        <TabsContent value="revenue" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-7">
            <Card className="md:col-span-4">
              <CardHeader>
                <CardTitle>Revenue Trend Analysis</CardTitle>
                <CardDescription>Revenue performance with trend analysis and predictions</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`$${value}`, 'Revenue']} />
                    <Line 
                      type="monotone" 
                      dataKey="revenue" 
                      stroke="#2563eb" 
                      strokeWidth={2}
                      dot={{ fill: '#2563eb' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="md:col-span-3">
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
                <CardDescription>Key performance indicators</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">This Month</span>
                    <span className="font-medium">$7,100</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Last Month</span>
                    <span className="font-medium">$5,900</span>
                  </div>
                  <div className="flex justify-between text-green-600">
                    <span className="text-sm">Growth</span>
                    <span className="font-medium">+20.3%</span>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h4 className="font-medium">Revenue Quality Score</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Diversification</span>
                      <span>85%</span>
                    </div>
                    <Progress value={85} className="h-2" />
                    <div className="flex justify-between text-sm">
                      <span>Stability</span>
                      <span>92%</span>
                    </div>
                    <Progress value={92} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="forecast" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Dubai Market Forecast</CardTitle>
                <CardDescription>Real Dubai seasonal patterns and revenue predictions</CardDescription>
              </CardHeader>
              <CardContent>
                {forecastData?.forecast_data ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={forecastData.forecast_data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip formatter={(value, name) => [`AED ${value}`, 'Forecasted Revenue']} />
                      <Area 
                        type="monotone" 
                        dataKey="forecasted_revenue" 
                        stroke="#10b981" 
                        fill="#10b981"
                        fillOpacity={0.3}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    Loading forecast data...
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Dubai Market Insights</CardTitle>
                <CardDescription>Real market predictions and seasonal trends</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <h4 className="font-medium">Next Quarter Forecast</h4>
                  <div className="text-2xl font-bold text-green-600">
                    AED {forecastData?.next_quarter_revenue?.toLocaleString() || '0'}
                  </div>
                  <div className="text-sm text-muted-foreground">Based on Dubai seasonality</div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">Confidence Level</h4>
                  <div className="flex items-center gap-2">
                    <Progress value={forecastData?.confidence || 0} className="flex-1" />
                    <span className="text-sm font-medium">{forecastData?.confidence || 0}%</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">Peak Period</h4>
                  <div className="text-sm">
                    <strong>{forecastData?.peak_period || 'Winter Season'}</strong>
                  </div>
                </div>

                {forecastData?.insights && (
                  <Alert>
                    <Target className="h-4 w-4" />
                    <AlertDescription>
                      {forecastData.insights.seasonal_impact}
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="market" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Dubai Market Performance</CardTitle>
                <CardDescription>Your performance vs Dubai market standards</CardDescription>
              </CardHeader>
              <CardContent>
                {marketInsights ? (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium">Market Position</span>
                        <Badge variant={marketInsights.competitive_position <= 3 ? "default" : "secondary"}>
                          #{marketInsights.competitive_position} in area
                        </Badge>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Your Performance: {marketInsights.performance_vs_market}%</span>
                        <span className="text-muted-foreground">vs Market Average</span>
                      </div>
                    </div>

                    {marketInsights.area_insights && (
                      <div className="space-y-2">
                        <h4 className="font-medium">Area: {marketInsights.area_insights.area}</h4>
                        <div className="text-sm text-muted-foreground">
                          <p>Tier: {marketInsights.area_insights.tier}</p>
                          <p>Primary Demand: {marketInsights.area_insights.primary_demand}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-muted-foreground">Loading market data...</div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Dubai Seasonal Trends</CardTitle>
                <CardDescription>Real Dubai seasonal demand patterns</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <h4 className="font-medium">Market Health Score</h4>
                  <div className="flex items-center gap-2">
                    <div className="text-2xl font-bold text-green-600">
                      {marketInsights?.market_health_score || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">/ 100</div>
                  </div>
                  <Progress value={marketInsights?.market_health_score || 0} className="h-2" />
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">Dubai Seasonal Demand</h4>
                  <div className="grid grid-cols-1 gap-2 text-sm">
                    <div className="flex justify-between">
                      <span>Winter Peak (Dec-Feb)</span>
                      <span className="font-medium text-green-600">+50%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Winter High (Mar, Nov)</span>
                      <span className="font-medium text-blue-600">+30%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Shoulder (Apr, Oct)</span>
                      <span className="font-medium">Normal</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Summer Low (May-Sep)</span>
                      <span className="font-medium text-red-600">-30%</span>
                    </div>
                  </div>
                </div>

                <Alert>
                  <TrendingUp className="h-4 w-4" />
                  <AlertDescription>
                    Dubai winter season (Dec-Mar) offers premium pricing opportunities with 40-50% higher demand.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="pricing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Dynamic Pricing Optimization</CardTitle>
              <CardDescription>AI-suggested pricing adjustments based on demand, events, and competition</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-7 gap-2 text-sm font-medium text-muted-foreground">
                  <div>Date</div>
                  <div>Current</div>
                  <div>Suggested</div>
                  <div>Potential Lift</div>
                  <div>Demand</div>
                  <div>Events</div>
                  <div>Action</div>
                </div>
                {pricingOptimizationData.map((day) => {
                  const lift = ((day.suggested - day.current) / day.current * 100).toFixed(1)
                  return (
                    <div key={day.date} className="grid grid-cols-7 gap-2 items-center py-2 border-b">
                      <div className="text-sm font-medium">{day.date}</div>
                      <div className="text-sm">${day.current}</div>
                      <div className="text-sm font-medium text-green-600">${day.suggested}</div>
                      <div className={`text-sm font-medium ${parseFloat(lift) > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {parseFloat(lift) > 0 ? '+' : ''}{lift}%
                      </div>
                      <div>
                        <Badge variant={
                          day.demand === 'Very High' ? 'destructive' :
                          day.demand === 'High' ? 'default' :
                          day.demand === 'Medium' ? 'secondary' : 'outline'
                        }>
                          {day.demand}
                        </Badge>
                      </div>
                      <div className="text-xs">
                        {day.events.length > 0 ? day.events.join(', ') : 'None'}
                      </div>
                      <div>
                        <Button size="sm" variant="outline">Apply</Button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="competition" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Competitive Analysis</CardTitle>
                <CardDescription>Track nearby properties and their performance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {competitorAnalysis.map((competitor) => (
                    <div key={competitor.name} className="p-3 border rounded-lg space-y-2">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-sm">{competitor.name}</p>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <MapPin className="h-3 w-3" />
                            <span>{competitor.distance} miles away</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">${competitor.rate}/night</p>
                          <div className="flex items-center gap-1 text-xs">
                            <Star className="h-3 w-3 fill-current text-yellow-500" />
                            <span>{competitor.rating}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span>Occupancy</span>
                        <span className="font-medium">{competitor.bookings}%</span>
                      </div>
                      <Progress value={competitor.bookings} className="h-1" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Competitive Position</CardTitle>
                <CardDescription>Your ranking and opportunities</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <h4 className="font-medium">Market Position</h4>
                  <div className="text-2xl font-bold text-blue-600">#2</div>
                  <div className="text-sm text-muted-foreground">out of 12 nearby properties</div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">Price Competitiveness</h4>
                  <div className="text-sm">
                    <div className="flex justify-between">
                      <span>vs Avg Market Rate</span>
                      <span className="font-medium text-green-600">+5.2%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>vs Direct Competitors</span>
                      <span className="font-medium text-red-600">-8.1%</span>
                    </div>
                  </div>
                </div>

                <Alert>
                  <Zap className="h-4 w-4" />
                  <AlertDescription>
                    Increase rates by $15-20 to match premium competitors while maintaining bookings.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <div className="grid gap-4">
            {insightsData.map((insight, index) => (
              <Card key={index}>
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className={`p-2 rounded-full ${
                      insight.type === 'opportunity' ? 'bg-green-100 text-green-600' :
                      insight.type === 'warning' ? 'bg-yellow-100 text-yellow-600' :
                      'bg-blue-100 text-blue-600'
                    }`}>
                      <insight.icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold">{insight.title}</h3>
                        <div className="flex gap-2">
                          <Badge variant="outline">Impact: {insight.impact}</Badge>
                          <Badge variant="outline">Effort: {insight.effort}</Badge>
                        </div>
                      </div>
                      <p className="text-muted-foreground">{insight.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            <Card>
              <CardHeader>
                <CardTitle>Demand Patterns</CardTitle>
                <CardDescription>Booking demand by time and day type</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={demandPatternsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="weekday" fill="#2563eb" name="Weekday" />
                    <Bar dataKey="weekend" fill="#10b981" name="Weekend" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="occupancy" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Overall Occupancy</CardTitle>
                <CardDescription>Current occupancy rate across all properties</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <RechartsPieChart>
                    <Pie
                      data={occupancyData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      dataKey="value"
                    >
                      {occupancyData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value}%`, '']} />
                  </RechartsPieChart>
                </ResponsiveContainer>
                <div className="flex justify-center mt-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold">{analyticsData?.occupancyRate || 0}%</p>
                    <p className="text-sm text-muted-foreground">Occupied</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Occupancy Insights</CardTitle>
                <CardDescription>Performance metrics and optimization recommendations</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Peak Season</span>
                    <span className="font-medium">Jun - Aug (89%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Low Season</span>
                    <span className="font-medium">Jan - Mar (62%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Average Stay</span>
                    <span className="font-medium">3.2 nights</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Booking Lead Time</span>
                    <span className="font-medium">28 days</span>
                  </div>
                </div>
                
                <div className="pt-4 border-t">
                  <h4 className="font-medium mb-2">AI Recommendations</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Implement dynamic pricing to increase low-season occupancy</li>
                    <li>• Offer 7+ day discounts to increase average stay</li>
                    <li>• Target last-minute bookings with flash sales</li>
                    <li>• Consider corporate partnerships for midweek bookings</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}