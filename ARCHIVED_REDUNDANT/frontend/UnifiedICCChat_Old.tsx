import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Plus, Send, Check, Edit, Eye, Download, Scale, Upload, MessageCircle, Bot, User, CheckCircle, AlertCircle } from 'lucide-react'
import { Card, CardContent } from './ui/card'
import { Button } from './ui/button'
import { Progress } from './ui/progress'
import { useToast } from './ui/toast'
import '../styles/kenyan-theme.css'

interface ChatMessage {
  id: string
  type: 'user' | 'ai' | 'system' | 'evidence'
  content: string
  timestamp: Date
  evidenceData?: any
  validationState?: any
  editableFields?: string[]
}

interface EvidenceItem {
  id: string
  filename: string
  type: string
  size: number
  analysis?: any
  validated: boolean
  userEdits?: any
}

interface UnifiedICCChatProps {
  apiBaseUrl?: string
}

const UnifiedICCChat: React.FC<UnifiedICCChatProps> = ({ 
  apiBaseUrl = 'http://localhost:8002' 
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [evidenceItems, setEvidenceItems] = useState<EvidenceItem[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [isAITyping, setIsAITyping] = useState(false)
  const [validationProgress, setValidationProgress] = useState(0)
  const [isDragOver, setIsDragOver] = useState(false)
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')
    const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const initializationRef = useRef<boolean>(false)
  const { toast } = useToast()

  // Initialize session and welcome message
  useEffect(() => {
    if (!initializationRef.current) {
      initializationRef.current = true
      initializeChat()
    }
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const initializeChat = async () => {
    try {
      // Create session
      const response = await fetch(`${apiBaseUrl}/api/session/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date: new Date().toISOString().split('T')[0],
          time: new Date().toTimeString().split(' ')[0],
          location: 'Kenya',
          description: 'Evidence submission via ICCLexAI chat interface',
          urgency_level: 'High',          submitter_info: { name: 'Chat User', role: 'Submitter' }
        })
      })

      if (response.ok) {
        const result = await response.json()
        setSessionId(result.session_id)        // Add welcome message
        addAIMessage(
          `Jambo! 🇰🇪 Welcome to ICCLexAI\n\nI help you submit evidence to the International Criminal Court.\n\nReady to start? Upload your evidence files and I'll guide you through each step.`,
          'welcome'
        )
      }
    } catch (error) {
      console.error('Failed to initialize session:', error)
      addAIMessage('Sorry, I had trouble starting up. Please refresh and try again.', 'error')
    }
  }

  const addAIMessage = (content: string, subtype?: string) => {
    const message: ChatMessage = {
      id: Date.now().toString(),
      type: 'ai',
      content,
      timestamp: new Date(),
      validationState: subtype
    }
    setMessages(prev => [...prev, message])
  }

  const addUserMessage = (content: string) => {
    const message: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, message])
  }
  
  const addEvidenceMessage = (evidenceData: EvidenceItem, analysis: any) => {
    const validationStatus = evidenceData.validated ? '✅ VALIDATED' : '⏳ PENDING VALIDATION'
    const validationClass = evidenceData.validated ? 'validation-approved' : 'validation-pending'
    
    const message: ChatMessage = {
      id: Date.now().toString(),
      type: 'evidence',
      content: `📁 ${evidenceData.filename} (${(evidenceData.size / 1024 / 1024).toFixed(1)}MB) ${validationStatus}\n\n` +
               `🤖 AI Analysis:\n` +
               `${analysis.summary || 'Analyzing content...'}\n\n` +
               `🎯 Key Findings:\n` +
               `${analysis.key_findings?.join('\n') || '• Processing...'}\n\n` +
               `⚖️ Legal Relevance: ${analysis.legal_relevance || 'High'}\n` +
               `📊 Confidence: ${Math.round(analysis.confidence || 85)}%\n\n` +
               `${evidenceData.validated ? '✅ Human Verified - Ready for submission' : '⏳ Awaiting Validation - Please review above'}`,
      timestamp: new Date(),
      evidenceData,
      validationState: validationClass,
      editableFields: ['summary', 'key_findings', 'legal_relevance']
    }
    setMessages(prev => [...prev, message])
  }

  const handleFileUpload = async (files: FileList) => {
    if (!sessionId || files.length === 0) return

    // Add user message about upload
    addUserMessage(`📁 Uploading ${files.length} file(s): ${Array.from(files).map(f => f.name).join(', ')}`)
    
    setIsAITyping(true)
    
    try {
      const formData = new FormData()
      Array.from(files).forEach(file => {
        formData.append('files', file)
      })

      const response = await fetch(`${apiBaseUrl}/api/session/${sessionId}/evidence/upload`, {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        
        // Simulate AI analysis for each file
        for (let i = 0; i < files.length; i++) {
          const file = files[i]
          const evidenceItem: EvidenceItem = {
            id: result.evidence_ids?.[i] || `evidence-${Date.now()}-${i}`,
            filename: file.name,
            type: file.type,
            size: file.size,
            validated: false
          }

          // Mock AI analysis (in real app, this comes from backend)
          const analysis = {
            summary: `This ${file.type.includes('image') ? 'image' : file.type.includes('video') ? 'video' : 'document'} contains evidence relevant to the incident.`,
            key_findings: [
              '• Timestamp metadata available',
              '• Location data embedded',
              '• Content shows relevant incident details'            ],
            legal_relevance: 'High',
            confidence: 85 + Math.random() * 10
          }

          setEvidenceItems(prev => [...prev, evidenceItem])
          
          // Add evidence analysis message with delay for natural feel
          setTimeout(() => {
            addEvidenceMessage(evidenceItem, analysis)
            
            // Simple validation prompt
            setTimeout(() => {
              addAIMessage(`📁 Analysis complete for ${file.name}\n\nPlease review the analysis above. Say "yes" to validate or "edit" to modify.`)
            }, 500)
          }, 1000 + i * 800)
        }

        toast({
          title: "Evidence Uploaded",
          description: `Uploaded ${files.length} files successfully`,
        })
      }
    } catch (error) {
      console.error('Upload failed:', error)
      addAIMessage('Sorry, I had trouble uploading those files. Please try again.')
    } finally {
      setIsAITyping(false)
    }
  }
  const handleSendMessage = async () => {
    if (!newMessage.trim()) return

    const userInput = newMessage.trim()
    setNewMessage('')
    addUserMessage(userInput)
    setIsAITyping(true)    // Sequential workflow-based AI responses
    setTimeout(() => {
      let aiResponse = ''

      // Check current workflow state
      const hasEvidence = evidenceItems.length > 0
      const needsValidation = evidenceItems.some(item => !item.validated)
      const allValidated = hasEvidence && evidenceItems.every(item => item.validated)

      // Sequential response logic
      if (userInput.toLowerCase().includes('yes') || userInput.toLowerCase().includes('looks good') || userInput.toLowerCase().includes('correct')) {
        if (needsValidation) {
          aiResponse = `✅ Evidence validated!\n\nValidation progress: ${validationProgress + 15}%\n\n`
          setValidationProgress(prev => {
            const newProgress = Math.min(prev + 15, 100)
            if (newProgress >= 80) {
              setTimeout(() => {
                addAIMessage('🎯 All evidence validated! Ready to generate your ICC submission package.\n\nShall I create the documents now?')
              }, 1000)
            }
            return newProgress
          })
          
          // Update evidence as validated
          setEvidenceItems(prev => prev.map(item => 
            prev.length > 0 ? { ...item, validated: true } : item
          ))
        } else {
          aiResponse = 'Thank you for confirming. What would you like to do next?'
        }
        
      } else if (userInput.toLowerCase().includes('generate') || userInput.toLowerCase().includes('create') || userInput.toLowerCase().includes('submit')) {
        if (allValidated) {
          aiResponse = `🎯 Generating ICC submission package...\n\nCreating documents:\n📄 Legal analysis\n📋 Evidence inventory\n✅ Validation certificates\n\nThis will take a moment...`
          
          setTimeout(() => {
            addAIMessage(
              `✅ Package complete!\n\nCase Reference: ICC-KENYA-2025-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}\nEvidence Items: ${evidenceItems.length}\nValidation: ${validationProgress}%\n\nReady to download and submit to ICC.`
            )
          }, 3000)
        } else {
          aiResponse = `⏳ Please finish validating all evidence first.\n\nRemaining items need validation before generating documents.`
        }

      } else if (userInput.toLowerCase().includes('edit') || userInput.toLowerCase().includes('change')) {
        aiResponse = `✏️ Click the edit button on any evidence card to make changes.\n\nOr tell me specifically what needs to be corrected.`

      } else if (userInput.toLowerCase().includes('help') || userInput.toLowerCase().includes('what')) {
        if (!hasEvidence) {
          aiResponse = `📁 Upload evidence files to get started.\n\nI'll analyze each file and guide you through validation.`
        } else if (needsValidation) {
          aiResponse = `✅ Review the evidence analysis above.\n\nSay "yes" to validate or "edit" to make changes.\n\nProgress: ${validationProgress}%`
        } else {
          aiResponse = `🎯 All evidence validated!\n\nReady to generate ICC submission package.`
        }

      } else {
        // Context-aware default response
        if (!hasEvidence) {
          aiResponse = `Please upload your evidence files first.\n\nDrag files here or click the + button.`
        } else if (needsValidation) {
          aiResponse = `Please validate the evidence analysis above.\n\nSay "yes" if correct or "edit" to modify.`
        } else {
          aiResponse = `All evidence validated! Say "generate" to create your ICC submission package.`
        }
      }

      addAIMessage(aiResponse)
      setIsAITyping(false)
    }, 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileUpload(files)
    }
  }, [sessionId])

  const startEditing = (messageId: string, currentContent: string) => {
    setEditingMessageId(messageId)
    setEditContent(currentContent)
  }

  const saveEdit = (messageId: string) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId 
        ? { ...msg, content: editContent }
        : msg
    ))
    setEditingMessageId(null)
    setEditContent('')
    
    addAIMessage('✅ Thanks for the correction! I\'ve updated the analysis.')
  }
  return (
    <div 
      className={`min-h-screen kenyan-landscape-bg ${isDragOver ? 'brightness-110' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >      {/* Header */}
      <header className="kenyan-header-enhanced text-white p-4 sticky top-0 z-10">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Scale className="h-8 w-8 text-kenya-gold justice-scale" />
            <div>
              <h1 className="text-2xl font-bold">🇰🇪 ICCLexAI</h1>
              <p className="text-kenya-gold text-sm">AI-Powered Evidence Analysis Chat</p>
            </div>
          </div>
          
          {/* Progress Indicator */}
          <div className="text-right">
            <div className="text-sm text-kenya-gold mb-1">
              Validation Progress: {validationProgress}%
            </div>
            <Progress value={validationProgress} className="w-32 h-2" />
            {validationProgress >= 80 && (
              <div className="mt-2">
                <Button
                  size="sm"
                  className="kenyan-button accent text-xs"
                  onClick={() => {
                    setNewMessage('generate submission')
                    setTimeout(() => handleSendMessage(), 100)
                  }}
                >
                  <Download className="h-3 w-3 mr-1" />
                  Generate Submission
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="container mx-auto max-w-4xl p-4 pb-24">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-3xl ${message.type === 'user' ? 'ml-16' : 'mr-16'}`}>                <Card className={`
                  ${message.type === 'user' 
                    ? 'chat-message-user' 
                    : message.type === 'evidence'
                    ? `evidence-card-enhanced ${message.validationState || ''}`
                    : 'chat-message-ai kenyan-glass-card'
                  }
                `}>
                  <CardContent className="p-4">
                    {/* Message Header */}
                    <div className="flex items-center gap-2 mb-2">
                      {message.type === 'user' ? (
                        <User className="h-5 w-5" />
                      ) : (
                        <Bot className="h-5 w-5 text-kenya-gold" />
                      )}
                      <span className="font-semibold text-sm">
                        {message.type === 'user' ? 'You' : message.type === 'evidence' ? 'Evidence Analysis' : 'ICCLexAI'}
                      </span>
                      <span className="text-xs opacity-70">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                    </div>

                    {/* Message Content */}
                    {editingMessageId === message.id ? (
                      <div className="space-y-2">
                        <textarea
                          value={editContent}
                          onChange={(e) => setEditContent(e.target.value)}
                          className="w-full p-2 border rounded text-kenya-black"
                          rows={4}
                        />
                        <div className="flex gap-2">
                          <Button size="sm" onClick={() => saveEdit(message.id)}>
                            <Check className="h-4 w-4 mr-1" />
                            Save
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline" 
                            onClick={() => setEditingMessageId(null)}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>                    ) : (
                      <div className="whitespace-pre-wrap">
                        {message.content}
                        
                        {/* Download buttons for submission complete messages */}
                        {message.validationState === 'submission-complete' && (
                          <div className="mt-4 space-y-2">
                            <div className="grid grid-cols-2 gap-2">
                              <Button
                                size="sm"
                                className="kenyan-button primary"
                                onClick={() => {
                                  // Mock download functionality
                                  const element = document.createElement('a')
                                  element.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent('ICC Submission Package - Generated by ICCLexAI')
                                  element.download = 'ICC-Submission-Package.zip'
                                  element.click()
                                  addAIMessage('📥 Submission package downloaded! Please submit to ICC Prosecutor\'s Office.')
                                }}
                              >
                                <Download className="h-4 w-4 mr-1" />
                                Download Package
                              </Button>
                              
                              <Button
                                size="sm"
                                variant="outline"
                                className="kenyan-button secondary"
                                onClick={() => {
                                  addAIMessage(`📋 **Document Review**\n\nYour ICC submission includes:\n• Article 15 Communication\n• Evidence Analysis Report\n• Chain of Custody Documents\n• Validation Certificates\n\nEverything looks complete and ready for submission!`)
                                }}
                              >
                                <Eye className="h-4 w-4 mr-1" />
                                Review Docs
                              </Button>
                            </div>
                          </div>
                        )}
                      </div>
                    )}{/* Evidence Actions */}
                    {message.type === 'evidence' && message.editableFields && (
                      <div className="flex gap-2 mt-3 pt-3 border-t border-kenya-gold">
                        <Button
                          size="sm"
                          className="kenyan-button secondary"
                          onClick={() => startEditing(message.id, message.content)}
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Edit Analysis
                        </Button>
                        
                        {!message.evidenceData?.validated ? (
                          <Button
                            size="sm"
                            className="kenyan-button primary"
                            onClick={() => {
                              // Update evidence as validated
                              setEvidenceItems(prev => prev.map(item => 
                                item.id === message.evidenceData?.id 
                                  ? { ...item, validated: true } 
                                  : item
                              ))
                              
                              // Update message content to show validated status
                              setMessages(prev => prev.map(msg => 
                                msg.id === message.id 
                                  ? { 
                                      ...msg, 
                                      content: msg.content.replace('⏳ PENDING VALIDATION', '✅ VALIDATED').replace('⏳ **Awaiting Validation**', '✅ **Human Verified**'),
                                      validationState: 'validation-approved'
                                    }
                                  : msg
                              ))
                              
                              setValidationProgress(prev => Math.min(prev + 15, 100))
                              
                              setTimeout(() => {
                                addAIMessage('✅ Evidence validated successfully! Great work - this strengthens your case.')
                              }, 500)
                            }}
                          >
                            <Check className="h-4 w-4 mr-1" />
                            Validate Evidence
                          </Button>
                        ) : (
                          <div className="flex items-center gap-2 px-3 py-2 bg-kenya-green-light rounded-lg">
                            <CheckCircle className="h-4 w-4 text-kenya-green" />
                            <span className="text-sm font-semibold text-kenya-green">Validated ✓</span>
                          </div>
                        )}
                        
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-kenya-red border-kenya-red hover:bg-kenya-red hover:text-white"
                          onClick={() => {
                            addAIMessage(`⚠️ I understand you have concerns about this evidence. Please tell me what's wrong and I'll help address it.\n\nYou can also edit the analysis directly or provide additional context.`)
                          }}
                        >
                          <AlertCircle className="h-4 w-4 mr-1" />
                          Flag Issue
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          ))}

          {/* AI Typing Indicator */}
          {isAITyping && (
            <div className="flex justify-start">
              <div className="max-w-3xl mr-16">
                <Card className="kenyan-glass-card">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Bot className="h-5 w-5 text-kenya-gold ai-processing" />
                      <span className="text-sm font-semibold">ICCLexAI is typing</span>
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-kenya-gold rounded-full animate-pulse"></div>
                        <div className="w-2 h-2 bg-kenya-gold rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                        <div className="w-2 h-2 bg-kenya-gold rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>      </div>
      
      {/* Input Area */}
      <div className="kenyan-chat-input">
        <div className="container mx-auto max-w-4xl">
          <div className="flex gap-3 items-end">
            {/* File Upload Button */}
            <Button
              onClick={() => fileInputRef.current?.click()}
              className="kenyan-button secondary flex-shrink-0"
              size="lg"
            >
              <Plus className="h-5 w-5" />
            </Button>
            
            {/* Message Input */}
            <div className="flex-1">
              <textarea
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Tell me about the incident, validate evidence, or ask questions..."
                rows={2}
              />
            </div>
            
            {/* Send Button */}
            <Button
              onClick={handleSendMessage}
              disabled={!newMessage.trim() || isAITyping}
              className="kenyan-button primary flex-shrink-0"
              size="lg"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
          
          {/* File Upload Hint */}
          <div className="text-center text-sm text-kenya-green mt-2">
            💡 Drop files anywhere on the page or click + to upload evidence
          </div>
        </div>
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
        onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
        className="hidden"
      />      {/* Drag Overlay */}
      {isDragOver && (
        <div className="kenyan-upload-overlay fixed inset-0 flex items-center justify-center z-50">
          <div className="kenyan-upload-area p-16 text-center max-w-md">
            <Upload className="h-20 w-20 text-kenya-red mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-kenya-black mb-2">Drop Evidence Files Here</h2>
            <p className="text-kenya-green text-lg">ICCLexAI will analyze them immediately</p>
            <div className="mt-4 text-sm text-kenya-gold">
              📁 Images • 🎥 Videos • 🎵 Audio • 📄 Documents
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UnifiedICCChat
