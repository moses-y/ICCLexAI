// Production environment configuration
export const config = {
  // API Configuration
  apiUrl: import.meta.env.VITE_API_URL || 'https://icclexai-backend.railway.app',
  apiTimeout: 30000,
  
  // Application Settings
  environment: import.meta.env.MODE || 'production',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  appName: 'ICCLexAI',
  
  // Feature Flags
  features: {
    chatWidget: true,
    fileUpload: true,
    agenticAnalysis: true,
    autoSubmission: true,
    realTimeUpdates: true
  },
  
  // File Upload Limits
  fileUpload: {
    maxSize: 50 * 1024 * 1024, // 50MB
    allowedTypes: [
      'application/pdf',
      'image/jpeg',
      'image/png',
      'image/gif',
      'text/plain',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ],
    maxFiles: 10
  },
  
  // UI Configuration
  ui: {
    theme: 'kenyan',
    primaryColor: '#1B5E20', // Kenyan green
    secondaryColor: '#FFC107', // Kenyan gold
    darkMode: false
  },
  
  // Analytics
  analytics: {
    enabled: import.meta.env.PROD,
    trackingId: import.meta.env.VITE_GA_TRACKING_ID,
    debug: import.meta.env.DEV
  },
  
  // Error Reporting
  sentry: {
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.MODE,
    enabled: import.meta.env.PROD
  },
  
  // Performance
  performance: {
    enableServiceWorker: true,
    enableLazyLoading: true,
    chunkSize: 'small', // For better caching
    preloadImages: false
  }
}

// Type definitions
export interface AppConfig {
  apiUrl: string
  apiTimeout: number
  environment: string
  version: string
  appName: string
  features: Record<string, boolean>
  fileUpload: {
    maxSize: number
    allowedTypes: string[]
    maxFiles: number
  }
  ui: {
    theme: string
    primaryColor: string
    secondaryColor: string
    darkMode: boolean
  }
  analytics: {
    enabled: boolean
    trackingId?: string
    debug: boolean
  }
  sentry: {
    dsn?: string
    environment: string
    enabled: boolean
  }
  performance: {
    enableServiceWorker: boolean
    enableLazyLoading: boolean
    chunkSize: string
    preloadImages: boolean
  }
}

export default config
