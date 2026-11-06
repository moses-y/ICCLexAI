import React, { useState, useEffect, useCallback } from 'react'
import { Upload, CheckCircle, Clock, AlertCircle, Edit, Save, X, FileText, Eye } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Progress } from './ui/progress'
import { useToast } from './ui/toast'
// If you have a toast hook in your UI library, use the correct path, e.g.:
//import { useToast } from '@/components/ui/use-toast'
// Or, if you do not have a use-toast hook, comment this out and use a fallback or remove toast usage.

interface ICCContextState {
  session_id: string
  case_metadata: any
  evidence_pool: any[]
  validation_state: any
  case_summary: any
  validation_progress: number
}

interface ICCValidationDashboardProps {
  apiBaseUrl?: string
}

const ICCValidationDashboard: React.FC<ICCValidationDashboardProps> = ({ 
  apiBaseUrl = 'http://localhost:8002' 
}) => {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [contextState, setContextState] = useState<ICCContextState | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [editingMode, setEditingMode] = useState<string | null>(null)
  const [editedContent, setEditedContent] = useState<string>('')
  const [currentView, setCurrentView] = useState<'dashboard' | 'evidence' | 'validation' | 'document'>('dashboard')
  const { toast } = useToast()

  // Initialize new session
  const initializeSession = useCallback(async () => {
    try {
      setIsLoading(true)
      
      const incidentDetails = {
        date: new Date().toISOString().split('T')[0],
        time: new Date().toTimeString().split(' ')[0],
        location: 'Nairobi, Kenya',
        description: 'Human rights violation requiring ICC investigation',
        victim_info: '',
        perpetrator_info: '',
        witness_info: '',
        urgency_level: 'High',
        submitter_info: {
          name: 'Anonymous Submitter',
          role: 'Witness'
        }
      }

      const response = await fetch(`${apiBaseUrl}/api/session/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(incidentDetails)
      })

      if (response.ok) {
        const result = await response.json()
        setSessionId(result.session_id)
        await loadSessionState(result.session_id)
        toast({
          title: "Session Created",
          description: `New ICC case session created: ${result.file_number}`,
        })
      } else {
        throw new Error('Failed to create session')
      }
    } catch (error) {
      console.error('Session initialization error:', error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to initialize ICC session",
      })
    } finally {
      setIsLoading(false)
    }
  }, [apiBaseUrl, toast])

  // Load session state
  const loadSessionState = useCallback(async (sessionId: string) => {
    try {
      const [stateResponse, validationResponse] = await Promise.all([
        fetch(`${apiBaseUrl}/api/session/${sessionId}/state`),
        fetch(`${apiBaseUrl}/api/session/${sessionId}/validation`)
      ])

      if (stateResponse.ok && validationResponse.ok) {
        const stateData = await stateResponse.json()
        const validationData = await validationResponse.json()
        
        setContextState({
          ...stateData,
          ...validationData
        })
      }
    } catch (error) {
      console.error('Failed to load session state:', error)
    }
  }, [apiBaseUrl])

  // Upload evidence files
  const uploadEvidence = useCallback(async (files: FileList) => {
    if (!sessionId) return

    try {
      setIsLoading(true)
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
        await loadSessionState(sessionId)
        toast({
          title: "Evidence Uploaded",
          description: `Uploaded ${files.length} files. Analysis in progress.`,
        })
      } else {
        throw new Error('Upload failed')
      }
    } catch (error) {
      console.error('Evidence upload error:', error)
      toast({
        variant: "destructive",
        title: "Upload Error",
        description: "Failed to upload evidence files",
      })
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, apiBaseUrl, loadSessionState, toast])

  // Update validation state
  const updateValidation = useCallback(async (field: string, value: any) => {
    if (!sessionId) return

    try {
      const response = await fetch(`${apiBaseUrl}/api/session/${sessionId}/validation/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          field,
          value,
          reviewer_id: 'human_validator'
        })
      })

      if (response.ok) {
        await loadSessionState(sessionId)
        toast({
          title: "Validation Updated",
          description: `${field.replace('_', ' ')} has been ${value ? 'completed' : 'reset'}`,
        })
      }
    } catch (error) {
      console.error('Validation update error:', error)
    }
  }, [sessionId, apiBaseUrl, loadSessionState, toast])

  // Update case summary
  const updateSummary = useCallback(async (field: string, content: string) => {
    if (!sessionId) return

    try {
      const response = await fetch(`${apiBaseUrl}/api/session/${sessionId}/summary/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          [field]: content,
          editor_id: 'human_editor'
        })
      })

      if (response.ok) {
        await loadSessionState(sessionId)
        setEditingMode(null)
        toast({
          title: "Summary Updated",
          description: "Case summary has been updated successfully",
        })
      }
    } catch (error) {
      console.error('Summary update error:', error)
    }
  }, [sessionId, apiBaseUrl, loadSessionState, toast])

  // Generate AI summary
  const generateAISummary = useCallback(async () => {
    if (!sessionId) return

    try {
      setIsLoading(true)
      const response = await fetch(`${apiBaseUrl}/api/session/${sessionId}/summary/generate`)
      
      if (response.ok) {
        await loadSessionState(sessionId)
        toast({
          title: "AI Summary Generated",
          description: "Case summary has been generated by AI",
        })
      }
    } catch (error) {
      console.error('AI summary generation error:', error)
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, apiBaseUrl, loadSessionState, toast])

  // Generate ICC document
  const generateICCDocument = useCallback(async () => {
    if (!sessionId) return

    try {
      setIsLoading(true)
      const response = await fetch(`${apiBaseUrl}/api/session/${sessionId}/document/generate`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const result = await response.json()
        toast({
          title: "ICC Document Generated",
          description: "Final ICC submission document is ready",
        })
        console.log('ICC Document:', result.document)
      } else {
        const error = await response.json()
        toast({
          variant: "destructive",
          title: "Generation Failed",
          description: error.detail || "Failed to generate ICC document",
        })
      }
    } catch (error) {
      console.error('ICC document generation error:', error)
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, apiBaseUrl, toast])

  // Validate evidence item
  const validateEvidence = useCallback(async (evidenceId: string, status: string) => {
    if (!sessionId) return

    try {
      const response = await fetch(`${apiBaseUrl}/api/session/${sessionId}/evidence/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          evidence_id: evidenceId,
          status,
          validator_id: 'human_validator'
        })
      })

      if (response.ok) {
        await loadSessionState(sessionId)
        toast({
          title: "Evidence Validated",
          description: `Evidence marked as ${status}`,
        })
      }
    } catch (error) {
      console.error('Evidence validation error:', error)
    }
  }, [sessionId, apiBaseUrl, loadSessionState, toast])

  // Handle file drop
  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const files = e.dataTransfer.files
    if (files.length > 0) {
      uploadEvidence(files)
    }
  }, [uploadEvidence])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      uploadEvidence(files)
    }
  }, [uploadEvidence])

  // Start editing
  const startEditing = (field: string, currentContent: string) => {
    setEditingMode(field)
    setEditedContent(currentContent || '')
  }

  // Save edit
  const saveEdit = () => {
    if (editingMode) {
      updateSummary(editingMode, editedContent)
    }
  }

  // Cancel edit
  const cancelEdit = () => {
    setEditingMode(null)
    setEditedContent('')
  }

  if (!sessionId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-red-50 p-8">
        <div className="max-w-4xl mx-auto">          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              🇰🇪 ICCLexAI - Evidence Validation
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Human-in-the-Loop Validation for International Criminal Court Submissions
            </p>
            <Button 
              onClick={initializeSession} 
              disabled={isLoading}
              size="lg"
              className="bg-green-600 hover:bg-green-700"
            >
              {isLoading ? 'Creating Session...' : 'Initialize New ICC Case'}
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}        <div className="bg-gradient-to-r from-green-600 to-red-600 text-white p-6 rounded-lg mb-6">
          <h1 className="text-3xl font-bold mb-2">🇰🇪 ICCLexAI - Case Validation</h1>
          <p className="text-green-100">
            Session: {sessionId?.slice(0, 8)}... | 
            File Number: {contextState?.case_metadata?.file_number || 'Generating...'}
          </p>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-2">
              <span>Validation Progress</span>
              <span>{Math.round((contextState?.validation_progress || 0) * 100)}%</span>
            </div>
            <Progress 
              value={(contextState?.validation_progress || 0) * 100} 
              className="h-2"
            />
          </div>
        </div>

        {/* Navigation */}
        <div className="flex space-x-4 mb-6">
          {['dashboard', 'evidence', 'validation', 'document'].map((view) => (
            <Button
              key={view}
              variant={currentView === view ? 'default' : 'outline'}
              onClick={() => setCurrentView(view as any)}
              className="capitalize"
            >
              {view}
            </Button>
          ))}
        </div>

        {/* Dashboard View */}
        {currentView === 'dashboard' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Evidence Upload */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Upload className="mr-2" />
                  Evidence Upload
                </CardTitle>
                <CardDescription>
                  Upload evidence files for analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-500 transition-colors"
                  onDrop={handleFileDrop}
                  onDragOver={(e) => e.preventDefault()}
                >
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-gray-600 mb-4">
                    Drag & drop files here, or click to select
                  </p>
                  <input
                    type="file"
                    multiple
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                  >
                    Select Files
                  </label>
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  Evidence Files: {contextState?.evidence_pool?.length || 0}
                </div>
              </CardContent>
            </Card>

            {/* Case Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="mr-2" />
                  Case Summary
                </CardTitle>
                <CardDescription>
                  AI-generated case analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Button 
                    onClick={generateAISummary}
                    disabled={isLoading}
                    className="w-full"
                  >
                    {isLoading ? 'Generating...' : 'Generate AI Summary'}
                  </Button>
                  
                  {contextState?.case_summary?.ai_generated_summary && (
                    <div className="p-4 bg-gray-50 rounded text-sm">
                      {contextState.case_summary.ai_generated_summary.slice(0, 200)}...
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Validation Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CheckCircle className="mr-2" />
                  Validation Status
                </CardTitle>
                <CardDescription>
                  Human review progress
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(contextState?.validation_state || {}).map(([key, value]) => {
                    if (key === 'validation_progress') return null
                    
                    return (
                      <div key={key} className="flex items-center justify-between">
                        <span className="text-sm capitalize">
                          {key.replace('_', ' ')}
                        </span>
                        <div className="flex items-center">
                          {value ? (
                            <CheckCircle className="h-5 w-5 text-green-500" />
                          ) : (
                            <Clock className="h-5 w-5 text-yellow-500" />
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => updateValidation(key, !value)}
                            className="ml-2"
                          >
                            {value ? 'Reset' : 'Mark Complete'}
                          </Button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Evidence View */}
        {currentView === 'evidence' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Evidence Pool Management</CardTitle>
                <CardDescription>
                  Review and validate uploaded evidence items
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {contextState?.evidence_pool?.map((evidence: any, index: number) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-semibold">{evidence.filename || `Evidence ${index + 1}`}</h4>
                          <p className="text-sm text-gray-600">
                            Type: {evidence.file_type || 'Unknown'} | 
                            Size: {evidence.size ? `${(evidence.size / 1024).toFixed(1)}KB` : 'Unknown'}
                          </p>
                          <p className="text-sm text-gray-600">
                            Relevance: {evidence.legal_relevance ? `${(evidence.legal_relevance * 100).toFixed(0)}%` : 'Analyzing...'}
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => validateEvidence(evidence.file_id, 'validated')}
                            className="text-green-600"
                          >
                            Validate
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => validateEvidence(evidence.file_id, 'rejected')}
                            className="text-red-600"
                          >
                            Reject
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {(!contextState?.evidence_pool || contextState.evidence_pool.length === 0) && (
                    <div className="text-center py-8 text-gray-500">
                      No evidence files uploaded yet. Upload files to begin analysis.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Validation View */}
        {currentView === 'validation' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Case Summary Review & Editing</CardTitle>
                <CardDescription>
                  Review and edit AI-generated case summaries
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* AI Generated Summary */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="font-semibold">AI Generated Summary</h4>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => startEditing('human_edited_summary', contextState?.case_summary?.ai_generated_summary || '')}
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        Edit
                      </Button>
                    </div>
                    {editingMode === 'human_edited_summary' ? (
                      <div className="space-y-2">
                        <textarea
                          value={editedContent}
                          onChange={(e) => setEditedContent(e.target.value)}
                          className="w-full h-32 p-3 border rounded-lg"
                          placeholder="Edit the case summary..."
                        />
                        <div className="flex space-x-2">
                          <Button size="sm" onClick={saveEdit}>
                            <Save className="h-4 w-4 mr-1" />
                            Save
                          </Button>
                          <Button size="sm" variant="outline" onClick={cancelEdit}>
                            <X className="h-4 w-4 mr-1" />
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="p-4 bg-gray-50 rounded-lg">
                        {contextState?.case_summary?.human_edited_summary || 
                         contextState?.case_summary?.ai_generated_summary || 
                         'No summary generated yet. Click "Generate AI Summary" in the dashboard.'}
                      </div>
                    )}
                  </div>

                  {/* Key Findings */}
                  <div>
                    <h4 className="font-semibold mb-2">Key Findings</h4>
                    <div className="space-y-2">
                      {contextState?.case_summary?.key_findings?.map((finding: string, index: number) => (
                        <div key={index} className="p-2 bg-blue-50 rounded border-l-4 border-blue-500">
                          {finding}
                        </div>
                      )) || (
                        <div className="text-gray-500">No key findings identified yet.</div>
                      )}
                    </div>
                  </div>

                  {/* Legal Assessment */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="font-semibold">Legal Assessment</h4>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => startEditing('legal_assessment', contextState?.case_summary?.legal_assessment || '')}
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        Edit
                      </Button>
                    </div>
                    {editingMode === 'legal_assessment' ? (
                      <div className="space-y-2">
                        <textarea
                          value={editedContent}
                          onChange={(e) => setEditedContent(e.target.value)}
                          className="w-full h-24 p-3 border rounded-lg"
                          placeholder="Edit legal assessment..."
                        />
                        <div className="flex space-x-2">
                          <Button size="sm" onClick={saveEdit}>
                            <Save className="h-4 w-4 mr-1" />
                            Save
                          </Button>
                          <Button size="sm" variant="outline" onClick={cancelEdit}>
                            <X className="h-4 w-4 mr-1" />
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="p-4 bg-gray-50 rounded-lg">
                        {contextState?.case_summary?.legal_assessment || 'No legal assessment available.'}
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Document View */}
        {currentView === 'document' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>ICC Document Generation</CardTitle>
                <CardDescription>
                  Generate final ICC submission document
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex">
                      <AlertCircle className="h-5 w-5 text-yellow-600 mr-2 mt-0.5" />
                      <div>
                        <h4 className="font-semibold text-yellow-800">Validation Required</h4>
                        <p className="text-yellow-700 text-sm">
                          Case must be at least 80% validated before generating ICC document.
                          Current progress: {Math.round((contextState?.validation_progress || 0) * 100)}%
                        </p>
                      </div>
                    </div>
                  </div>

                  <Button
                    onClick={generateICCDocument}
                    disabled={isLoading || (contextState?.validation_progress || 0) < 0.8}
                    className="w-full"
                    size="lg"
                  >
                    {isLoading ? 'Generating Document...' : 'Generate ICC Submission Document'}
                  </Button>

                  <div className="text-sm text-gray-600">
                    <p>The ICC document will include:</p>
                    <ul className="list-disc ml-5 mt-2">
                      <li>Complete case summary and metadata</li>
                      <li>Validated evidence inventory</li>
                      <li>Cross-reference analysis</li>
                      <li>Legal assessment and recommendations</li>
                      <li>Human validation certification</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

export default ICCValidationDashboard
