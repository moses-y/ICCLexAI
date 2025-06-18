import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import AgenticDashboard from './components/AgenticDashboard'
import ErrorBoundary from './components/ErrorBoundary'
import './styles/kenyan-theme.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
    },
  },
})

function App() {
  const handleSubmissionComplete = (submissionData: any) => {
    console.log('🎯 ICC Submission Generated:', submissionData)
    // Handle successful submission - could show success modal, redirect, etc.
    alert(`🇰🇪 Success! ICC Submission ${submissionData.submission_package?.submission_id} generated!`)
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AgenticDashboard onSubmissionComplete={handleSubmissionComplete} />
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
