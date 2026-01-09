import { ReactNode } from 'react'

export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">Todo App</h1>
          <p className="mt-2 text-sm text-secondary">
            Organize your tasks efficiently
          </p>
        </div>
        {children}
      </div>
    </div>
  )
}
