import { useState, useEffect, useRef, useCallback, useMemo } from "react"
import { Bell, Check, Calendar, DollarSign, MessageSquare, AlertTriangle, X, Loader2 } from "lucide-react"
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

interface GroupedNotifications {
  today: Notification[]
  yesterday: Notification[]
  earlier: Notification[]
}

export function NotificationBell() {
  const { user, apiCall } = useApp()
  const navigate = useNavigate()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [isClosing, setIsClosing] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Group notifications by date
  const groupedNotifications = useMemo((): GroupedNotifications => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)

    return notifications.reduce(
      (groups, notification) => {
        const notifDate = new Date(notification.created_at)
        const notifDay = new Date(notifDate.getFullYear(), notifDate.getMonth(), notifDate.getDate())

        if (notifDay.getTime() === today.getTime()) {
          groups.today.push(notification)
        } else if (notifDay.getTime() === yesterday.getTime()) {
          groups.yesterday.push(notification)
        } else {
          groups.earlier.push(notification)
        }
        return groups
      },
      { today: [], yesterday: [], earlier: [] } as GroupedNotifications
    )
  }, [notifications])

  const loadNotifications = useCallback(async () => {
    if (!user) return
    setLoading(true)
    
    try {
      const data = await apiCall(`/v1/hosts/${user.id}/notifications?limit=20`)
      
      if (data.success && data.data.notifications) {
        setNotifications(data.data.notifications)
        setUnreadCount(data.data.unread_count || 0)
      } else {
        setNotifications([])
        setUnreadCount(0)
      }
    } catch (error) {
      console.error('[NotificationBell] Failed to load notifications:', error)
    } finally {
      setLoading(false)
    }
  }, [user, apiCall])

  const markAsRead = async (notificationId: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation()
    if (!user) return
    
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
    )
    setUnreadCount(prev => Math.max(0, prev - 1))
    
    try {
      await apiCall(`/v1/hosts/${user.id}/notifications/${notificationId}/read`, 'PUT')
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
      loadNotifications()
    }
  }

  const markAllAsRead = useCallback(async () => {
    if (!user) return
    
    const unreadNotifications = notifications.filter(n => !n.is_read)
    if (unreadNotifications.length === 0) return
    
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
    setUnreadCount(0)
    
    try {
      await Promise.all(
        unreadNotifications.map(n => 
          apiCall(`/v1/hosts/${user.id}/notifications/${n.id}/read`, 'PUT')
        )
      )
    } catch (error) {
      console.error('[NotificationBell] Failed to mark all as read:', error)
      loadNotifications()
    }
  }, [user, notifications, apiCall, loadNotifications])

  const dismissNotification = async (notificationId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    // Animate out then remove
    const element = document.getElementById(`notif-${notificationId}`)
    if (element) {
      element.style.transform = 'translateX(100%)'
      element.style.opacity = '0'
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== notificationId))
      }, 200)
    }
    await markAsRead(notificationId)
  }

  const handleNotificationClick = (notification: Notification) => {
    markAsRead(notification.id)
    closeDropdown()
    
    if (notification.action_url) {
      navigate(notification.action_url)
    } else {
      switch (notification.type) {
        case 'new_booking':
        case 'booking_update':
          navigate('/dashboard/bookings')
          break
        case 'payment_received':
          navigate('/dashboard/financials')
          break
        case 'guest_message':
          navigate('/dashboard/messages')
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
    const iconClasses = "w-4 h-4"
    switch (type) {
      case 'urgent':
        return <AlertTriangle className={`${iconClasses} text-red-500`} />
      case 'new_booking':
      case 'booking_update':
        return <Calendar className={`${iconClasses} text-emerald-500`} />
      case 'payment_received':
        return <DollarSign className={`${iconClasses} text-blue-500`} />
      case 'guest_message':
        return <MessageSquare className={`${iconClasses} text-purple-500`} />
      default:
        return <Bell className={`${iconClasses} text-gray-400`} />
    }
  }

  const getNotificationBgColor = (type: string, isRead: boolean) => {
    if (isRead) return 'bg-transparent'
    switch (type) {
      case 'urgent':
        return 'bg-red-50 dark:bg-red-950/20'
      case 'new_booking':
      case 'booking_update':
        return 'bg-emerald-50 dark:bg-emerald-950/20'
      case 'payment_received':
        return 'bg-blue-50 dark:bg-blue-950/20'
      case 'guest_message':
        return 'bg-purple-50 dark:bg-purple-950/20'
      default:
        return 'bg-gray-50 dark:bg-gray-900/50'
    }
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const closeDropdown = () => {
    setIsClosing(true)
    setTimeout(() => {
      setIsOpen(false)
      setIsClosing(false)
    }, 150)
  }

  useEffect(() => {
    if (user) {
      loadNotifications()
      const interval = setInterval(loadNotifications, 60000)
      return () => clearInterval(interval)
    }
  }, [user, loadNotifications])

  useEffect(() => {
    if (isOpen) {
      loadNotifications()
    }
  }, [isOpen, loadNotifications])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        closeDropdown()
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleButtonClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (isOpen) {
      closeDropdown()
    } else {
      setIsOpen(true)
    }
  }

  const renderNotificationGroup = (title: string, notifs: Notification[]) => {
    if (notifs.length === 0) return null
    
    return (
      <div className="mb-2">
        <div className="px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted/50">
          {title}
        </div>
        {notifs.map((notification, index) => (
          <div
            key={notification.id}
            id={`notif-${notification.id}`}
            onClick={() => handleNotificationClick(notification)}
            className={`
              group relative px-4 py-3 cursor-pointer
              transition-all duration-200 ease-out
              hover:bg-muted/80
              ${getNotificationBgColor(notification.type, notification.is_read)}
              ${index !== notifs.length - 1 ? 'border-b border-border/50' : ''}
            `}
            style={{
              animationDelay: `${index * 50}ms`,
              animation: 'slideIn 0.2s ease-out forwards'
            }}
          >
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-background shadow-sm flex items-center justify-center">
                {getNotificationIcon(notification.type)}
              </div>
              <div className="flex-1 min-w-0 pr-6">
                <div className="flex items-center gap-2 mb-0.5">
                  <p className={`text-sm font-medium truncate ${
                    !notification.is_read ? 'text-foreground' : 'text-muted-foreground'
                  }`}>
                    {notification.title}
                  </p>
                  {!notification.is_read && (
                    <span className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
                  )}
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2 mb-1">
                  {notification.message}
                </p>
                <p className="text-xs text-muted-foreground/70">
                  {formatTime(notification.created_at)}
                </p>
              </div>
              <button
                onClick={(e) => dismissNotification(notification.id, e)}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full opacity-0 group-hover:opacity-100 hover:bg-muted transition-all"
              >
                <X className="w-3.5 h-3.5 text-muted-foreground" />
              </button>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <Button 
        variant="ghost" 
        size="icon" 
        className="relative hover:bg-muted/80 transition-colors"
        type="button"
        onClick={handleButtonClick}
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 h-5 min-w-5 px-1 flex items-center justify-center text-xs font-bold bg-red-500 text-white rounded-full animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </Button>

      {isOpen && (
        <div 
          className={`
            absolute right-0 top-full mt-2 w-[380px] 
            bg-background border border-border rounded-xl shadow-2xl 
            z-[9999] overflow-hidden
            ${isClosing ? 'animate-fadeOut' : 'animate-fadeIn'}
          `}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
            <div className="flex items-center gap-2">
              <Bell className="w-4 h-4 text-muted-foreground" />
              <h3 className="font-semibold text-sm">Notifications</h3>
              {unreadCount > 0 && (
                <Badge variant="secondary" className="text-xs px-2 py-0 h-5 bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
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
                className="h-7 text-xs text-muted-foreground hover:text-foreground"
              >
                <Check className="h-3 w-3 mr-1" />
                Mark all read
              </Button>
            )}
          </div>

          {/* Content */}
          <ScrollArea className="max-h-[420px]">
            {loading && notifications.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <Loader2 className="h-6 w-6 animate-spin mb-2" />
                <p className="text-sm">Loading notifications...</p>
              </div>
            ) : notifications.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-3">
                  <Bell className="h-8 w-8 opacity-40" />
                </div>
                <p className="text-sm font-medium">All caught up!</p>
                <p className="text-xs">No new notifications</p>
              </div>
            ) : (
              <div className="py-1">
                {renderNotificationGroup('Today', groupedNotifications.today)}
                {renderNotificationGroup('Yesterday', groupedNotifications.yesterday)}
                {renderNotificationGroup('Earlier', groupedNotifications.earlier)}
              </div>
            )}
          </ScrollArea>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="border-t px-4 py-2 bg-muted/30">
              <Button
                variant="ghost"
                size="sm"
                className="w-full h-8 text-xs text-muted-foreground hover:text-foreground"
                onClick={() => {
                  closeDropdown()
                  navigate('/dashboard/settings')
                }}
              >
                Notification Settings
              </Button>
            </div>
          )}
        </div>
      )}

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-8px) scale(0.96);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
        @keyframes fadeOut {
          from {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
          to {
            opacity: 0;
            transform: translateY(-8px) scale(0.96);
          }
        }
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.15s ease-out forwards;
        }
        .animate-fadeOut {
          animation: fadeOut 0.15s ease-out forwards;
        }
      `}</style>
    </div>
  )
}
