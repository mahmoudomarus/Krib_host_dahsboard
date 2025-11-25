import { useState, useEffect, useRef, useCallback } from "react"
import { Bell, Check } from "lucide-react"
import { Button } from "./ui/button"
import { ScrollArea } from "./ui/scroll-area"
import { Badge } from "./ui/badge"
import { useNavigate } from "react-router-dom"
import { useApp } from "../contexts/AppContext"

interface Notification {
  id: string
  type: string
  title: string
  message: string
  is_read: boolean
  priority: string
  created_at: string
  booking_id?: string
  property_id?: string
  action_url?: string
}

export function NotificationBell() {
  const { user, apiCall } = useApp()
  const navigate = useNavigate()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const loadNotifications = useCallback(async () => {
    if (!user) {
      console.log('[NotificationBell] No user, skipping load')
      setLoading(false)
      return
    }
    
    console.log('[NotificationBell] Loading notifications for user:', user.id)
    setLoading(true)
    
    try {
      const data = await apiCall(`/v1/hosts/${user.id}/notifications?limit=20`)
      
      console.log('[NotificationBell] API response:', data)
      
      if (data.success && data.data.notifications) {
        setNotifications(data.data.notifications)
        setUnreadCount(data.data.unread_count || 0)
        console.log('[NotificationBell] Loaded notifications:', data.data.notifications.length, 'Unread:', data.data.unread_count)
      } else {
        console.warn('[NotificationBell] Unexpected response structure:', data)
        setNotifications([])
        setUnreadCount(0)
      }
    } catch (error) {
      console.error('[NotificationBell] Failed to load notifications:', error)
      // Keep existing notifications on error, don't clear them
    } finally {
      // Always set loading to false, no matter what
      setLoading(false)
    }
  }, [user, apiCall])

  const markAsRead = async (notificationId: string) => {
    if (!user) return
    
    // Optimistically update UI immediately
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
    )
    setUnreadCount(prev => Math.max(0, prev - 1))
    
    try {
      await apiCall(`/v1/hosts/${user.id}/notifications/${notificationId}/read`, 'PUT')
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
      // Revert on error
      loadNotifications()
    }
  }

  const markAllAsRead = useCallback(async () => {
    if (!user) return
    
    const unreadNotifications = notifications.filter(n => !n.is_read)
    if (unreadNotifications.length === 0) return
    
    console.log('[NotificationBell] Marking all as read:', unreadNotifications.length)
    
    // Optimistically update UI immediately
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
    setUnreadCount(0)
    
    try {
      // Mark all unread notifications
      await Promise.all(
        unreadNotifications.map(n => 
          apiCall(`/v1/hosts/${user.id}/notifications/${n.id}/read`, 'PUT')
        )
      )
      console.log('[NotificationBell] All notifications marked as read')
    } catch (error) {
      console.error('[NotificationBell] Failed to mark all as read:', error)
      // Revert on error
      loadNotifications()
    }
  }, [user, notifications, apiCall])

  const markVisibleAsRead = useCallback(async () => {
    if (!user) return
    
    const unreadNotifications = notifications.filter(n => !n.is_read)
    if (unreadNotifications.length === 0) return
    
    console.log('[NotificationBell] Auto-marking visible notifications as read:', unreadNotifications.length)
    
    // Optimistically update UI immediately
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
    setUnreadCount(0)
    
    try {
      // Mark all currently visible unread notifications as read
      await Promise.all(
        unreadNotifications.map(n => 
          apiCall(`/v1/hosts/${user.id}/notifications/${n.id}/read`, 'PUT').catch(err => {
            console.error(`Failed to mark ${n.id} as read:`, err)
          })
        )
      )
    } catch (error) {
      console.error('[NotificationBell] Failed to auto-mark as read:', error)
    }
  }, [user, notifications, apiCall])

  const handleNotificationClick = (notification: Notification) => {
    // Close dropdown
    setIsOpen(false)
    
    // Navigate to relevant page
    if (notification.action_url) {
      navigate(notification.action_url)
    } else {
      switch (notification.type) {
        case 'new_booking':
          navigate('/dashboard/bookings')
          break
        case 'payment_received':
          navigate('/dashboard/financials')
          break
        case 'guest_message':
          navigate('/dashboard/messages')
          break
        case 'booking_update':
          navigate('/dashboard/bookings')
          break
        case 'urgent':
          if (notification.message.includes('settings')) {
            navigate('/dashboard/settings')
          }
          break
      }
    }
  }

  const getNotificationIcon = (type: string) => {
    const baseClasses = "w-2 h-2 rounded-full"
    switch (type) {
      case 'urgent':
        return <div className={`${baseClasses} bg-red-500`} />
      case 'new_booking':
        return <div className={`${baseClasses} bg-green-500`} />
      case 'payment_received':
        return <div className={`${baseClasses} bg-blue-500`} />
      case 'guest_message':
        return <div className={`${baseClasses} bg-purple-500`} />
      default:
        return <div className={`${baseClasses} bg-gray-400`} />
    }
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  useEffect(() => {
    console.log('[NotificationBell] Initial mount, user:', user?.id)
    if (user) {
      loadNotifications()
      // Poll for new notifications every 60 seconds
      const interval = setInterval(loadNotifications, 60000)
      return () => clearInterval(interval)
    }
  }, [user, loadNotifications])

  useEffect(() => {
    console.log('[NotificationBell] isOpen changed to:', isOpen)
    if (isOpen) {
      console.log('[NotificationBell] Dropdown opened, reloading notifications')
      loadNotifications()
      
      // Auto-mark all visible notifications as read after 2 seconds
      const autoMarkTimer = setTimeout(() => {
        markVisibleAsRead()
      }, 2000)
      
      return () => clearTimeout(autoMarkTimer)
    }
  }, [isOpen, markVisibleAsRead])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        console.log('[NotificationBell] Click outside detected, closing dropdown')
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleButtonClick = (e: React.MouseEvent) => {
    console.log('[NotificationBell] Button clicked. Current:', isOpen, 'Next:', !isOpen)
    e.preventDefault()
    e.stopPropagation()
    setIsOpen(!isOpen)
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <Button 
        variant="ghost" 
        size="icon" 
        className="relative"
        type="button"
        onClick={handleButtonClick}
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <Badge 
            className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 bg-red-500 hover:bg-red-600 pointer-events-none"
            variant="destructive"
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </Badge>
        )}
      </Button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-96 bg-white dark:bg-gray-950 border border-border rounded-lg shadow-xl z-[9999]">
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold">Notifications</h3>
              {unreadCount > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {unreadCount} new
                </Badge>
              )}
            </div>
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  markAllAsRead()
                }}
                className="h-8 text-xs"
              >
                <Check className="h-3 w-3 mr-1" />
                Mark all read
              </Button>
            )}
          </div>
          <ScrollArea className="h-[400px]">
            {loading && notifications.length === 0 ? (
              <div className="p-4 text-center text-muted-foreground">
                Loading notifications...
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                <Bell className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No notifications</p>
              </div>
            ) : (
              <div className="divide-y">
                {notifications.map(notification => (
                  <button
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification)}
                    className={`w-full p-4 text-left hover:bg-accent transition-colors ${
                      !notification.is_read ? 'bg-accent/50' : ''
                    }`}
                  >
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 mt-1">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <p className={`text-sm font-medium ${
                            !notification.is_read ? 'text-foreground' : 'text-muted-foreground'
                          }`}>
                            {notification.title}
                          </p>
                          <span className="text-xs text-muted-foreground whitespace-nowrap">
                            {formatTime(notification.created_at)}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {notification.message}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>
      )}
    </div>
  )
}

