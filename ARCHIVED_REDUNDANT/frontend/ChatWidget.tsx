import React, { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send, Scale, Zap } from 'lucide-react'
import { Button } from './ui/button'
import '../styles/kenyan-theme.css'

interface ChatMessage {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
}

interface ChatWidgetProps {
  isOpen: boolean
  onClose: () => void
  caseContext?: any
}

const ChatWidget: React.FC<ChatWidgetProps> = ({ isOpen, onClose, caseContext }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      content: "Jambo! 🇰🇪 I'm your ICCLexAI assistant. I'm here to help you build a strong case for the International Criminal Court. How can I assist you today?",
      sender: 'ai',
      timestamp: new Date()
    }
  ])
  const [newMessage, setNewMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: newMessage.trim(),
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setNewMessage('')
    setIsTyping(true)

    try {
      // Call AI chat guidance endpoint
      const response = await fetch('http://localhost:8001/chat-guidance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userMessage.content,
          case_context: caseContext
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          content: data.ai_response,
          sender: 'ai',
          timestamp: new Date()
        }

        setTimeout(() => {
          setMessages(prev => [...prev, aiMessage])
          setIsTyping(false)
        }, 1000) // Simulate typing delay
      } else {
        throw new Error('Chat service unavailable')
      }
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "I'm having trouble connecting right now. Please try again in a moment. In the meantime, make sure you've uploaded your evidence files and provided relevant keywords.",
        sender: 'ai',
        timestamp: new Date()
      }
      
      setTimeout(() => {
        setMessages(prev => [...prev, errorMessage])
        setIsTyping(false)
      }, 1000)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  if (!isOpen) return null

  return (
    <div className="kenyan-chat-widget">
      {/* Chat Header */}
      <div className="kenyan-chat-header">
        <Scale className="h-5 w-5 text-kenya-white justice-scale" />
        <div className="flex-1">
          <h3 className="font-semibold">ICC Legal AI Assistant</h3>
          <p className="text-xs opacity-90">Powered by Kenyan AI Innovation 🇰🇪</p>
        </div>
        <Button
          onClick={onClose}
          className="p-1 hover:bg-white/20 rounded"
          variant="ghost"
          size="sm"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Chat Body */}
      <div className="kenyan-chat-body">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.sender === 'user'
                    ? 'bg-kenya-red text-kenya-white'
                    : 'bg-kenya-gold-light text-kenya-black border border-kenya-green'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p className="text-xs opacity-75 mt-1">
                  {formatTimestamp(message.timestamp)}
                </p>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-kenya-gold-light text-kenya-black border border-kenya-green rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-kenya-green animate-pulse" />
                  <span className="text-sm">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Chat Input */}
      <div className="kenyan-chat-input">
        <div className="flex gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about evidence analysis, ICC requirements, or legal guidance..."
            className="flex-1 p-2 border border-kenya-black-light rounded-lg focus:border-kenya-red outline-none text-sm"
            disabled={isTyping}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || isTyping}
            className="kenyan-button primary p-2"
            size="sm"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        
        {/* Quick Actions */}
        <div className="flex gap-2 mt-2 flex-wrap">
          <button
            onClick={() => setNewMessage("What evidence do I need for a strong ICC case?")}
            className="text-xs bg-kenya-green text-kenya-white px-2 py-1 rounded hover:bg-kenya-green-light transition-colors"
          >
            Evidence Requirements
          </button>
          <button
            onClick={() => setNewMessage("How can I improve my case strength?")}
            className="text-xs bg-kenya-red text-kenya-white px-2 py-1 rounded hover:bg-kenya-red-light transition-colors"
          >
            Improve Case
          </button>
          <button
            onClick={() => setNewMessage("What's my current case confidence score?")}
            className="text-xs bg-kenya-gold text-kenya-black px-2 py-1 rounded hover:bg-kenya-gold-light transition-colors"
          >
            Confidence Score
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatWidget
