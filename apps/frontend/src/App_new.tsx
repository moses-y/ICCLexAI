import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import AgenticDashboard from './components/AgenticDashboard'
import './styles/kenyan-theme.css'

const queryClient = new QueryClient()

function App() {
  const handleSubmissionComplete = (submissionData: any) => {
    console.log('🎯 ICC Submission Generated:', submissionData)
    // Handle successful submission - could show success modal, redirect, etc.
    alert(`🇰🇪 Success! ICC Submission ${submissionData.submission_package?.submission_id} generated!`)
  }

  return (
    <QueryClientProvider client={queryClient}>
      <AgenticDashboard onSubmissionComplete={handleSubmissionComplete} />
    </QueryClientProvider>
  )
}

export default App
