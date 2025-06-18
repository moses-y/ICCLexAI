import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Image, Music, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import axios from 'axios'

interface AnalysisResult {
  file_name: string
  file_type: string
  ai_analysis: string
  legal_assessment: string
  confidence_score: number
  processing_time: number
  timestamp: string
}

interface UploadedFile extends File {
  id: string
  status: 'uploading' | 'processing' | 'completed' | 'error'
  result?: AnalysisResult
  error?: string
}

const FileUploadArea = () => {
  const [files, setFiles] = useState<UploadedFile[]>([])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      ...file,
      id: Math.random().toString(36).substring(7),
      status: 'uploading' as const
    }))
    
    setFiles(prev => [...prev, ...newFiles])

    for (const file of newFiles) {
      try {
        const formData = new FormData()
        formData.append('file', file)

        // Update file status to processing
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'processing' } : f
        ))

        const response = await axios.post('/api/analyze', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        // Update file with result
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { 
            ...f, 
            status: 'completed', 
            result: response.data 
          } : f
        ))
      } catch (error) {
        console.error('Analysis failed:', error)
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { 
            ...f, 
            status: 'error', 
            error: 'Analysis failed' 
          } : f        ))
      }
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
      'audio/*': ['.mp3', '.wav', '.m4a', '.aac'],
      'application/pdf': ['.pdf'],
      'text/*': ['.txt', '.md'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: true,
    maxSize: 100 * 1024 * 1024 // 100MB
  })

  const getFileIcon = (file: UploadedFile) => {
    if (file.type.startsWith('image/')) return <Image className="h-5 w-5" />
    if (file.type.startsWith('audio/')) return <Music className="h-5 w-5" />
    return <FileText className="h-5 w-5" />
  }

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <Clock className="h-4 w-4 animate-spin" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            ICC Evidence Upload
          </CardTitle>
          <CardDescription>
            Upload images, audio files, or documents for AI-powered legal analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-primary bg-primary/5'
                : 'border-muted-foreground/25 hover:border-primary/50'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            {isDragActive ? (
              <p className="text-lg font-medium">Drop files here...</p>
            ) : (
              <>
                <p className="text-lg font-medium mb-2">
                  Drag & drop files here, or click to select
                </p>
                <p className="text-sm text-muted-foreground">
                  Supports images, audio, PDF, Word documents (up to 100MB each)
                </p>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
            <CardDescription>
              Real-time AI analysis of uploaded evidence
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="border rounded-lg p-4 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getFileIcon(file)}
                      <div>
                        <p className="font-medium">{file.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(file.status)}
                      <span className="text-sm capitalize">{file.status}</span>
                    </div>
                  </div>

                  {file.result && (
                    <div className="space-y-3 pt-3 border-t">
                      <div>
                        <h4 className="font-medium mb-2">AI Analysis</h4>
                        <p className="text-sm bg-muted p-3 rounded">
                          {file.result.ai_analysis}
                        </p>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Legal Assessment</h4>
                        <p className="text-sm bg-muted p-3 rounded">
                          {file.result.legal_assessment}
                        </p>
                      </div>
                      <div className="flex items-center justify-between text-sm text-muted-foreground">
                        <span>
                          Confidence: {(file.result.confidence_score * 100).toFixed(1)}%
                        </span>
                        <span>
                          Processed in {file.result.processing_time.toFixed(2)}s
                        </span>
                      </div>
                    </div>
                  )}

                  {file.error && (
                    <div className="pt-3 border-t">
                      <p className="text-sm text-red-500">{file.error}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default FileUploadArea
