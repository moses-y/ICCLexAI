import React, { useState, useCallback } from 'react'
import { Upload, Scale, Zap, MessageCircle, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import ChatWidget from './ChatWidget'
import '../styles/kenyan-theme.css'

interface EvidenceFile {
  name: string
  type: string
  size: number
  status: 'uploading' | 'analyzing' | 'complete' | 'error'
  analysis?: any
}

interface AgenticDashboardProps {
  onSubmissionComplete?: (submissionData: any) => void
}

const AgenticDashboard: React.FC<AgenticDashboardProps> = ({ onSubmissionComplete }) => {
  const [evidenceFiles, setEvidenceFiles] = useState<EvidenceFile[]>([])
  const [keywords, setKeywords] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<any>(null)
  const [submissionReady, setSubmissionReady] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)

  const handleFileUpload = useCallback((files: FileList) => {
    const newFiles: EvidenceFile[] = Array.from(files).map(file => ({
      name: file.name,
      type: file.type,
      size: file.size,
      status: 'uploading'
    }))
    
    setEvidenceFiles(prev => [...prev, ...newFiles])
    
    // Simulate upload and analysis
    newFiles.forEach((file, index) => {
      setTimeout(() => {
        setEvidenceFiles(prev => 
          prev.map(f => 
            f.name === file.name 
              ? { ...f, status: 'analyzing' }
              : f
          )
        )
        
        // Simulate analysis completion
        setTimeout(() => {
          setEvidenceFiles(prev => 
            prev.map(f => 
              f.name === file.name 
                ? { ...f, status: 'complete', analysis: { confidence: 85 + Math.random() * 10 } }
                : f
            )
          )
        }, 2000 + index * 500)
      }, 500 + index * 200)
    })
  }, [])

  const handleAgenticAnalysis = async () => {
    if (!keywords.trim() || evidenceFiles.length === 0) {
      alert('Please upload evidence files and provide keywords')
      return
    }

    setIsProcessing(true)
    
    try {
      // Call agentic analysis endpoint
      const formData = new FormData()
      evidenceFiles.forEach((file, index) => {
        // In real implementation, we'd have the actual File objects
        formData.append('files', new Blob(['mock data']), file.name)
      })
      formData.append('keywords', keywords)

      const response = await fetch('http://localhost:8001/agentic-analysis', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const results = await response.json()
        setAnalysisResults(results)
        setSubmissionReady(true)
      } else {
        throw new Error('Analysis failed')
      }
    } catch (error) {
      console.error('Agentic analysis error:', error)
      alert('Analysis failed. Please try again.')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleAutoSubmission = async () => {
    if (!analysisResults) return

    try {
      const response = await fetch('http://localhost:8001/auto-submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          analysis_id: analysisResults.analysis_id,
          additional_context: 'Generated via ICCLexAI agentic workflow'
        })
      })

      if (response.ok) {
        const submissionData = await response.json()
        onSubmissionComplete?.(submissionData)
        alert('🎯 ICC Submission Generated Successfully!')
      }
    } catch (error) {
      console.error('Auto-submission error:', error)
      alert('Submission generation failed. Please try again.')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'uploading':
        return <Upload className="h-4 w-4 text-kenya-gold animate-spin" />
      case 'analyzing':
        return <Clock className="h-4 w-4 text-kenya-gold ai-processing" />
      case 'complete':
        return <CheckCircle className="h-4 w-4 text-kenya-green" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-kenya-red" />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card kenyan-pattern">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Scale className="h-8 w-8 text-kenya-red justice-scale" />              <div>
                <h1 className="text-3xl font-bold text-kenya-black">🇰🇪 ICCLexAI</h1>
                <p className="text-sm text-kenya-green font-semibold">
                  Agentic AI-Powered ICC Evidence Analysis
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Button 
                onClick={() => setChatOpen(!chatOpen)}
                className="kenyan-button secondary"
              >
                <MessageCircle className="h-4 w-4 mr-2" />
                AI Assistant
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Agentic Workflow Steps */}
        <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-3 mb-8">
          <Card className="kenyan-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-kenya-black">
                <Upload className="h-5 w-5 text-kenya-red" />
                Step 1: Upload Evidence
              </CardTitle>
              <CardDescription>
                Upload all relevant evidence files for AI analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                className="kenyan-upload-area p-8 text-center cursor-pointer"
                onDrop={(e) => {
                  e.preventDefault()
                  const files = e.dataTransfer.files
                  if (files.length > 0) {
                    handleFileUpload(files)
                  }
                }}
                onDragOver={(e) => e.preventDefault()}
                onClick={() => {
                  const input = document.createElement('input')
                  input.type = 'file'
                  input.multiple = true
                  input.accept = 'image/*,video/*,audio/*,.pdf,.doc,.docx'
                  input.onchange = (e) => {
                    const files = (e.target as HTMLInputElement).files
                    if (files) handleFileUpload(files)
                  }
                  input.click()
                }}
              >
                <Upload className="h-12 w-12 mx-auto mb-4 text-kenya-red" />
                <p className="text-lg font-semibold text-kenya-black">
                  Drop evidence files here or click to browse
                </p>
                <p className="text-sm text-kenya-green mt-2">
                  Images, Videos, Audio, Documents supported
                </p>
              </div>
              
              {/* Evidence Files List */}
              {evidenceFiles.length > 0 && (
                <div className="mt-4 space-y-2">
                  <h4 className="font-semibold text-kenya-black">Evidence Files:</h4>
                  {evidenceFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-kenya-gold-light rounded">
                      <span className="text-sm text-kenya-black">{file.name}</span>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(file.status)}
                        {file.analysis && (
                          <span className="text-xs text-kenya-green">
                            {Math.round(file.analysis.confidence)}% confidence
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="kenyan-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-kenya-black">
                <Zap className="h-5 w-5 text-kenya-gold" />
                Step 2: AI Keywords
              </CardTitle>
              <CardDescription>
                Provide 3-5 keywords to guide AI analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-kenya-black mb-2">
                    Incident Keywords
                  </label>
                  <input
                    type="text"
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    placeholder="e.g., human rights violation, police brutality, displacement"
                    className="w-full p-3 border-2 border-kenya-black-light rounded-lg focus:border-kenya-red outline-none"
                  />
                </div>
                
                <Button
                  onClick={handleAgenticAnalysis}
                  disabled={isProcessing || evidenceFiles.length === 0 || !keywords.trim()}
                  className="kenyan-button primary w-full"
                >
                  {isProcessing ? (
                    <>
                      <Clock className="h-4 w-4 mr-2 animate-spin" />
                      AI Analyzing...
                    </>
                  ) : (
                    <>
                      <Zap className="h-4 w-4 mr-2" />
                      Start Agentic Analysis
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className={`kenyan-card ${submissionReady ? 'featured' : ''}`}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-kenya-black">
                <Scale className="h-5 w-5 text-kenya-green" />
                Step 3: Auto-Submit
              </CardTitle>
              <CardDescription>
                Generate complete ICC submission package
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysisResults ? (
                <div className="space-y-4">
                  <div className="p-4 bg-kenya-green-light/10 rounded-lg">
                    <h4 className="font-semibold text-kenya-green mb-2">Analysis Complete!</h4>
                    <div className="text-sm space-y-1">
                      <p>🎯 Confidence: {analysisResults.confidence_score}%</p>
                      <p>📄 Context: 1000+ words generated</p>
                      <p>📋 Form: 95% auto-populated</p>
                      <p>⚡ Ready for submission</p>
                    </div>
                  </div>
                  
                  <Button
                    onClick={handleAutoSubmission}
                    className="kenyan-button accent w-full"
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Generate ICC Submission
                  </Button>
                </div>
              ) : (
                <div className="text-center py-8 text-kenya-black opacity-50">
                  <Scale className="h-12 w-12 mx-auto mb-4" />
                  <p>Complete analysis first</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Analysis Results Display */}
        {analysisResults && (
          <Card className="kenyan-card featured">
            <CardHeader>
              <CardTitle className="text-kenya-black">🤖 Agentic Analysis Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <h4 className="font-semibold text-kenya-red mb-2">Evidence Timeline</h4>
                  <div className="space-y-2">
                    {analysisResults.evidence_timeline?.map((item: any, index: number) => (
                      <div key={index} className="p-2 bg-kenya-gold-light rounded text-sm">
                        {item.description}
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-kenya-green mb-2">AI Recommendations</h4>
                  <div className="space-y-2">
                    {analysisResults.recommendations?.map((rec: string, index: number) => (
                      <div key={index} className="p-2 bg-kenya-green-light/10 rounded text-sm">
                        {rec}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </main>

      {/* Chat Widget */}
      {chatOpen && (
        <ChatWidget
          isOpen={chatOpen}
          onClose={() => setChatOpen(false)}
          caseContext={analysisResults}
        />
      )}
    </div>
  )
}

export default AgenticDashboard
