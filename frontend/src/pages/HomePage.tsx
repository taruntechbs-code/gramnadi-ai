import { Link } from 'react-router-dom'

import { PlaceholderPage } from '../components/common/PlaceholderPage'

export function HomePage() {
  return (
    <>
      <PlaceholderPage
        description="The application foundation is ready for future rural enterprise resilience workflows."
        title="Welcome to GramNadi AI"
      />
      <Link className="mt-6 inline-block text-sm font-medium underline" to="/login">
        Continue to the placeholder login route
      </Link>
    </>
  )
}
