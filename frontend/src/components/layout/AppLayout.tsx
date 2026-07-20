import { NavLink, Outlet } from 'react-router-dom'

const navigation = [
  { label: 'Home', to: '/' },
  { label: 'Login', to: '/login' },
  { label: 'Dashboard', to: '/dashboard' },
]

export function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <NavLink className="text-lg font-semibold" to="/">
            GramNadi AI
          </NavLink>
          <nav aria-label="Primary navigation" className="flex gap-4 text-sm">
            {navigation.map((item) => (
              <NavLink
                className={({ isActive }) =>
                  isActive ? 'font-semibold text-slate-900' : 'text-slate-500'
                }
                key={item.to}
                to={item.to}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-12">
        <Outlet />
      </main>
    </div>
  )
}
