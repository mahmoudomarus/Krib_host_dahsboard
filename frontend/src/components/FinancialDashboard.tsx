import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { Progress } from "./ui/progress"
import { Alert, AlertDescription } from "./ui/alert"
import { 
  DollarSign, 
  TrendingUp, 
  Calendar, 
  CreditCard, 
  Download,
  Plus,
  AlertCircle,
  CheckCircle,
  Clock,
  Banknote
} from "lucide-react"
import { useApp } from "../contexts/AppContext"

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
    getBankAccounts, 
    addBankAccount, 
    requestPayout, 
    getTransactions, 
    updatePayoutSettings 
  } = useApp()
  const [summary, setSummary] = useState<FinancialSummary | null>(null)
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([])
  const [payouts, setPayouts] = useState<Payout[]>([])
  const [loading, setLoading] = useState(true)
  const [payoutAmount, setPayoutAmount] = useState("")
  const [selectedBankAccount, setSelectedBankAccount] = useState("")

  useEffect(() => {
    loadFinancialData()
  }, [])

  async function loadFinancialData() {
    try {
      setLoading(true)
      
      const [summaryData, bankAccountsData, transactionsData] = await Promise.all([
        getFinancialSummary(),
        getBankAccounts(),
        getTransactions(20)
      ])
      
      setSummary(summaryData)
      setBankAccounts(bankAccountsData)
      setPayouts(transactionsData || [])
      
      // Set default bank account
      const primaryAccount = bankAccountsData.find((account: BankAccount) => account.is_primary)
      if (primaryAccount) {
        setSelectedBankAccount(primaryAccount.id)
      }
      
    } catch (error) {
      console.error('Failed to load financial data:', error)
    } finally {
      setLoading(false)
    }
  }

  async function requestPayout() {
    if (!payoutAmount || !selectedBankAccount) return
    
    try {
      const payout = await makeAPIRequest('/financials/payouts/request', {
        method: 'POST',
        body: JSON.stringify({
          amount: parseFloat(payoutAmount),
          bank_account_id: selectedBankAccount
        })
      })
      
      setPayouts(prev => [payout, ...prev])
      setPayoutAmount("")
      
      // Reload summary to update available balance
      const updatedSummary = await makeAPIRequest('/financials/summary')
      setSummary(updatedSummary)
      
    } catch (error) {
      console.error('Failed to request payout:', error)
      alert('Failed to request payout. Please try again.')
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
      <div className="p-6 space-y-6">
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
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Financial Dashboard</h1>
        <p className="text-muted-foreground">
          Manage your earnings, payouts, and financial settings
        </p>
      </div>

      {/* Financial Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Available Balance</CardTitle>
            <DollarSign className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${summary?.pending_earnings.toFixed(2) || '0.00'}</div>
            <p className="text-xs text-muted-foreground">Ready for payout</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Earnings</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${summary?.total_earnings.toFixed(2) || '0.00'}</div>
            <p className="text-xs text-muted-foreground">All time earnings</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Payouts</CardTitle>
            <Banknote className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${summary?.total_payouts.toFixed(2) || '0.00'}</div>
            <p className="text-xs text-muted-foreground">Money transferred</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Platform Fees</CardTitle>
            <CreditCard className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${summary?.platform_fees.toFixed(2) || '0.00'}</div>
            <p className="text-xs text-muted-foreground">Fees paid</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="payouts" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="payouts">Payouts</TabsTrigger>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Payouts Tab */}
        <TabsContent value="payouts" className="space-y-4">
          {/* Request Payout Section */}
          <Card>
            <CardHeader>
              <CardTitle>Request Payout</CardTitle>
              <CardDescription>
                Transfer your available earnings to your bank account
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {summary && summary.pending_earnings > 0 ? (
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <label className="text-sm font-medium">Amount</label>
                    <input
                      type="number"
                      value={payoutAmount}
                      onChange={(e) => setPayoutAmount(e.target.value)}
                      placeholder={`Max: $${summary.pending_earnings.toFixed(2)}`}
                      max={summary.pending_earnings}
                      className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Bank Account</label>
                    <select
                      value={selectedBankAccount}
                      onChange={(e) => setSelectedBankAccount(e.target.value)}
                      className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {bankAccounts.map((account) => (
                        <option key={account.id} value={account.id}>
                          {account.bank_name} ****{account.account_number_last4}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex items-end">
                    <Button 
                      onClick={requestPayout}
                      disabled={!payoutAmount || parseFloat(payoutAmount) <= 0}
                      className="w-full"
                    >
                      Request Payout
                    </Button>
                  </div>
                </div>
              ) : (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    No earnings available for payout. Complete bookings to start earning!
                  </AlertDescription>
                </Alert>
              )}

              {summary?.next_payout_date && (
                <div className="text-sm text-muted-foreground">
                  <Calendar className="inline h-4 w-4 mr-1" />
                  Next automatic payout: {new Date(summary.next_payout_date).toLocaleDateString()}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Payout History */}
          <Card>
            <CardHeader>
              <CardTitle>Payout History</CardTitle>
              <CardDescription>Your recent payout requests and transfers</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {payouts.length > 0 ? (
                  payouts.map((payout) => (
                    <div key={payout.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(payout.status)}
                          <span className="font-medium">${payout.amount.toFixed(2)}</span>
                          <Badge className={getStatusColor(payout.status)}>
                            {payout.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {new Date(payout.requested_at).toLocaleDateString()}
                          {payout.estimated_arrival && ` • Arrives ${new Date(payout.estimated_arrival).toLocaleDateString()}`}
                        </p>
                        {payout.failure_reason && (
                          <p className="text-sm text-red-600">{payout.failure_reason}</p>
                        )}
                      </div>
                      <div className="text-right text-sm text-muted-foreground">
                        {payout.bank_info && `${payout.bank_info.bank_name} ****${payout.bank_info.account_number_last4}`}
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
                        <p className="font-medium text-green-600">+${transaction.amount.toFixed(2)}</p>
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
          <Card>
            <CardHeader>
              <CardTitle>Bank Accounts</CardTitle>
              <CardDescription>Manage your payout destinations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {bankAccounts.map((account) => (
                  <div key={account.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">{account.bank_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {account.account_type} ****{account.account_number_last4}
                      </p>
                      <div className="flex gap-2 mt-1">
                        {account.is_primary && <Badge>Primary</Badge>}
                        <Badge variant={account.is_verified ? 'default' : 'secondary'}>
                          {account.verification_status}
                        </Badge>
                      </div>
                    </div>
                  </div>
                ))}
                <Button variant="outline" className="w-full">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Bank Account
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Payout Settings</CardTitle>
              <CardDescription>Configure automatic payouts and preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Payout Frequency</label>
                <select className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md">
                  <option value="weekly">Weekly</option>
                  <option value="biweekly">Bi-weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">Minimum Payout Amount</label>
                <input
                  type="number"
                  defaultValue="25"
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div className="flex items-center space-x-2">
                <input type="checkbox" id="auto-payout" defaultChecked />
                <label htmlFor="auto-payout" className="text-sm">Enable automatic payouts</label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
