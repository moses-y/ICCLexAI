import CaseApp from './components/case/CaseApp'
import ErrorBoundary from './components/ErrorBoundary'

// The previous App mounted a chat that faked analysis and submission (see ARCHIVED_REDUNDANT/frontend).
// Every number and statement shown now comes from the case API.
export default function App() {
  return (
    <ErrorBoundary>
      <CaseApp />
    </ErrorBoundary>
  )
}
