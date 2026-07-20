import { Link } from 'react-router-dom'

import { PlaceholderPage } from '../components/common/PlaceholderPage'

export function NotFoundPage() {
  return (
    <>
      <PlaceholderPage
        description="The requested route does not exist in the current application foundation."
        title="Page not found"
      />
      <Link className="mt-6 inline-block text-sm font-medium underline" to="/">
        Return home
      </Link>
    </>
  )
}
