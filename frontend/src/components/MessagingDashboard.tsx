import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { Textarea } from "./ui/textarea"
import { Badge } from "./ui/badge"
import { ScrollArea } from "./ui/scroll-area"
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar"
import { MessageSquare, Send, Sparkles, Archive, Search } from "lucide-react"
import { useApp } from "../contexts/AppContext"

interface Conversation {
  id: string
  property_id: string
  guest_name: string
  guest_email: string
  status: string
  last_message_at: string
  unread_count_host: number
}

interface Message {
  id: string
  sender_type: string
  content: string
  is_ai_generated: boolean
  created_at: string
  is_read: boolean
}

export function MessagingDashboard() {
  const { apiCall } = useApp()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [messageInput, setMessageInput] = useState("")
  const [aiResponse, setAiResponse] = useState("")
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")

  useEffect(() => {
    loadConversations()
  }, [])

  useEffect(() => {
    if (selectedConversation) {
      loadMessages(selectedConversation.id)
    }
  }, [selectedConversation])

  async function loadConversations() {
    try {
      const data = await apiCall("/messages/conversations", "GET")
      setConversations(data || [])
    } catch (error) {
      console.error("Failed to load conversations:", error)
    }
  }

  async function loadMessages(conversationId: string) {
    try {
      const data = await apiCall(`/messages/conversations/${conversationId}/messages`, "GET")
      setMessages(data || [])
    } catch (error) {
      console.error("Failed to load messages:", error)
    }
  }

  async function sendMessage() {
    if (!messageInput.trim() || !selectedConversation) return

    setLoading(true)
    try {
      await apiCall(`/messages/conversations/${selectedConversation.id}/messages`, "POST", {
        content: messageInput,
      })
      setMessageInput("")
      setAiResponse("")
      await loadMessages(selectedConversation.id)
      await loadConversations()
    } catch (error) {
      console.error("Failed to send message:", error)
    } finally {
      setLoading(false)
    }
  }

  async function generateAIResponse() {
    if (!selectedConversation || messages.length === 0) return

    const lastGuestMessage = [...messages].reverse().find(m => m.sender_type === "guest")
    if (!lastGuestMessage) return

    setLoading(true)
    try {
      const data = await apiCall(
        `/messages/conversations/${selectedConversation.id}/ai-response`,
        "POST",
        { message: lastGuestMessage.content }
      )
      setAiResponse(data.ai_response)
    } catch (error) {
      console.error("Failed to generate AI response:", error)
    } finally {
      setLoading(false)
    }
  }

  async function archiveConversation(conversationId: string) {
    try {
      await apiCall(`/messages/conversations/${conversationId}/archive`, "POST")
      await loadConversations()
      if (selectedConversation?.id === conversationId) {
        setSelectedConversation(null)
        setMessages([])
      }
    } catch (error) {
      console.error("Failed to archive conversation:", error)
    }
  }

  const filteredConversations = conversations.filter(
    (c) =>
      c.guest_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.guest_email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Messages</h1>
        <p className="text-muted-foreground">Communicate with your guests</p>
      </div>

      <div className="grid grid-cols-3 gap-6 h-[calc(100vh-200px)]">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Conversations</CardTitle>
            <CardDescription>
              {conversations.filter((c) => c.status === "active").length} active
            </CardDescription>
            <div className="relative mt-4">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search conversations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[calc(100vh-380px)]">
              {filteredConversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => setSelectedConversation(conversation)}
                  className={`p-4 border-b cursor-pointer hover:bg-accent transition-colors ${
                    selectedConversation?.id === conversation.id ? "bg-accent" : ""
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarFallback>{conversation.guest_name.charAt(0)}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-semibold">{conversation.guest_name}</p>
                        <p className="text-sm text-muted-foreground">{conversation.guest_email}</p>
                      </div>
                    </div>
                    {conversation.unread_count_host > 0 && (
                      <Badge variant="destructive">{conversation.unread_count_host}</Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {new Date(conversation.last_message_at).toLocaleString()}
                  </p>
                </div>
              ))}
              {filteredConversations.length === 0 && (
                <div className="p-8 text-center text-muted-foreground">
                  <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No conversations found</p>
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        <Card className="col-span-2 flex flex-col">
          {selectedConversation ? (
            <>
              <CardHeader className="border-b">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{selectedConversation.guest_name}</CardTitle>
                    <CardDescription>{selectedConversation.guest_email}</CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => archiveConversation(selectedConversation.id)}
                  >
                    <Archive className="h-4 w-4 mr-2" />
                    Archive
                  </Button>
                </div>
              </CardHeader>

              <ScrollArea className="flex-1 p-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${
                        message.sender_type === "host" ? "justify-end" : "justify-start"
                      }`}
                    >
                      <div
                        className={`max-w-[70%] rounded-lg p-3 ${
                          message.sender_type === "host"
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                        }`}
                      >
                        {message.is_ai_generated && (
                          <div className="flex items-center gap-1 mb-1">
                            <Sparkles className="h-3 w-3" />
                            <span className="text-xs opacity-70">AI Generated</span>
                          </div>
                        )}
                        <p className="text-sm">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {new Date(message.created_at).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>

              {aiResponse && (
                <div className="px-4 py-2 bg-blue-50 dark:bg-blue-950 border-t border-b">
                  <div className="flex items-start gap-2">
                    <Sparkles className="h-4 w-4 text-blue-600 mt-1" />
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-blue-600 mb-1">AI Suggestion</p>
                      <p className="text-sm">{aiResponse}</p>
                      <Button
                        size="sm"
                        variant="link"
                        onClick={() => setMessageInput(aiResponse)}
                        className="mt-1 p-0 h-auto"
                      >
                        Use this response
                      </Button>
                    </div>
                  </div>
                </div>
              )}

              <div className="p-4 border-t">
                <div className="flex gap-2 mb-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={generateAIResponse}
                    disabled={loading || messages.length === 0}
                  >
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate AI Response
                  </Button>
                </div>
                <div className="flex gap-2">
                  <Textarea
                    placeholder="Type your message..."
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault()
                        sendMessage()
                      }
                    }}
                    className="resize-none"
                    rows={3}
                  />
                  <Button onClick={sendMessage} disabled={loading || !messageInput.trim()}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <CardContent className="flex items-center justify-center h-full">
              <div className="text-center text-muted-foreground">
                <MessageSquare className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg">Select a conversation to start messaging</p>
              </div>
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  )
}

