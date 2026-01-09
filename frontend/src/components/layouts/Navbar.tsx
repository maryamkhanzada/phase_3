'use client'

import { Button } from '@/components/ui/Button'
import { useAuth } from '@/hooks/useAuth'

export function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="border-b border-border bg-background">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <div>
          <h1 className="text-xl font-bold">Todo App</h1>
        </div>
        <div className="flex items-center gap-4">
          {user && (
            <span className="text-sm text-secondary">{user.email}</span>
          )}
          <Button variant="ghost" onClick={logout} size="sm">
            Log Out
          </Button>
        </div>
      </div>
    </nav>
  )
}
