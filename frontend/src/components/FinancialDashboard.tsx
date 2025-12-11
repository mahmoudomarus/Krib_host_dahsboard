import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { Alert, AlertDescription } from "./ui/alert"
import { 
  DollarSign, 
  TrendingUp, 
  Banknote,
  AlertCircle,
  CheckCircle,
  Clock,
  CreditCard
} from "lucide-react"
import { useApp } from "../contexts/AppContext"
import { StripeConnectSetup } from "./StripeConnectSetup"

interface FinancialSummary {
  total_balance: number
  pending_earnings: number
  total_earnings: number
  total_payouts: number
  platform_fees: number
  recent_transactions: any[]
  payout_frequency: string
  next_payout_date?: string
}

interface BankAccount {
  id: string
  account_holder_name: string
  bank_name: string
  account_number_last4: string
  account_type: string
  is_primary: boolean
  is_verified: boolean
  verification_status: string
}

interface Payout {
  id: string
  amount: number
  status: string
  bank_account_id: string
  bank_info?: any
  requested_at: string
  completed_at?: string
  estimated_arrival?: string
  failure_reason?: string
}

export function FinancialDashboard() {
  const { 
    getFinancialSummary, 
    getHostPayouts
  } = useApp()
  const [summary, setSummary] = useState<FinancialSummary | null>(null)
  const [payouts, setPayouts] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadFinancialData()
  }, [])

  async function loadFinancialData() {
    try {
      setLoading(true)
      
      const [summaryData, payoutsData] = await Promise.all([
        getFinancialSummary().catch(() => ({ total_balance: 0, pending_earnings: 0, total_earnings: 0, total_payouts: 0, platform_fees: 0, recent_transactions: [] })),
        getHostPayouts().catch(() => ({ payouts: [], total_paid: 0, total_pending: 0, total_in_transit: 0 }))
      ])
      
      setSummary(summaryData)
      setPayouts(payoutsData)
      
    } catch (error) {
      console.error('Failed to load financial data:', error)
    } finally {
      setLoading(false)
    }
  }


  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'processing': return 'bg-blue-100 text-blue-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'failed': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4" />
      case 'processing': return <Clock className="h-4 w-4" />
      case 'pending': return <AlertCircle className="h-4 w-4" />
      case 'failed': return <AlertCircle className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  if (loading) {
    return (
      <div className=" space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className=" space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Financial Dashboard</h1>
        <p className="text-muted-foreground">
          Manage your earnings, payouts, and financial settings
        </p>
      </div>

      {/* Financial Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Earnings</CardTitle>
            <DollarSign className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">AED {payouts?.total_pending.toFixed(2) || '0.00'}</div>
            <p className="text-xs text-muted-foreground">Awaiting payout</p>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Earnings</CardTitle>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">AED {summary?.total_earnings.toFixed(2) || '0.00'}</div>
            <p className="text-xs text-muted-foreground">All time earnings</p>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Payouts</CardTitle>
            <Banknote className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">AED {payouts?.total_paid.toFixed(2) || '0.00'}</div>
            <p className="text-xs text-muted-foreground">Money transferred</p>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Platform Fees</CardTitle>
            <CreditCard className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">AED {summary?.platform_fees.toFixed(2) || '0.00'}</div>
            <p className="text-xs text-muted-foreground">Fees paid</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="payouts" className="w-full">
        <TabsList className="w-full justify-start border-b rounded-none h-auto p-0 bg-transparent">
          <TabsTrigger 
            value="payouts"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-4 py-3"
          >
            Payouts
          </TabsTrigger>
          <TabsTrigger 
            value="transactions"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-4 py-3"
          >
            Transactions
          </TabsTrigger>
          <TabsTrigger 
            value="settings"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-4 py-3"
          >
            Settings
          </TabsTrigger>
        </TabsList>

        {/* Payouts Tab */}
        <TabsContent value="payouts" className="space-y-4 pt-4">
          <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg text-sm text-muted-foreground">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>Payouts are automatically processed 1 day after guest checkout. Platform fee: 15%</span>
          </div>

          {/* Payout History */}
          <Card>
            <CardHeader>
              <CardTitle>Payout History</CardTitle>
              <CardDescription>Your recent payouts and transfers</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {payouts?.payouts && payouts.payouts.length > 0 ? (
                  payouts.payouts.map((payout: any) => (
                    <div key={payout.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(payout.status)}
                          <span className="font-medium">AED {payout.amount.toFixed(2)}</span>
                          <Badge className={getStatusColor(payout.status)}>
                            {payout.status}
                          </Badge>
                        </div>
                        <p className="text-sm font-medium">{payout.property_title || 'Property payout'}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(payout.initiated_at).toLocaleDateString()}
                          {payout.completed_at && ` • Completed ${new Date(payout.completed_at).toLocaleDateString()}`}
                        </p>
                        {payout.failure_message && (
                          <p className="text-sm text-red-600">{payout.failure_message}</p>
                        )}
                      </div>
                      <div className="text-right text-sm">
                        {payout.platform_fee && (
                          <p className="text-muted-foreground">Platform fee: AED {payout.platform_fee.toFixed(2)}</p>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-muted-foreground text-center py-4">No payouts yet</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Transactions Tab */}
        <TabsContent value="transactions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Transactions</CardTitle>
              <CardDescription>Your earning transactions from bookings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {summary?.recent_transactions.length ? (
                  summary.recent_transactions.map((transaction) => (
                    <div key={transaction.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                      <div className="space-y-1">
                        <p className="font-medium">{transaction.property_title}</p>
                        <p className="text-sm text-muted-foreground">
                          {transaction.guest_name} • {new Date(transaction.date).toLocaleDateString()}
                        </p>
                        <Badge variant={transaction.status === 'completed' ? 'default' : 'secondary'}>
                          {transaction.status}
                        </Badge>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-green-600">+AED {transaction.amount.toFixed(2)}</p>
                        <p className="text-sm text-muted-foreground">{transaction.type}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-muted-foreground text-center py-4">No transactions yet</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <StripeConnectSetup />
        </TabsContent>
      </Tabs>
    </div>
  )
}
