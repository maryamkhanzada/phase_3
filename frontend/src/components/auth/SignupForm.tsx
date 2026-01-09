'use client'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/hooks/useAuth'
import type { SignupFormData } from '@/types/user'
import Link from 'next/link'
import { FormEvent, useState } from 'react'

export function SignupForm() {
  const { signup, isLoading, error } = useAuth()
  const [formData, setFormData] = useState<SignupFormData>({
    email: '',
    password: '',
  })
  const [formErrors, setFormErrors] = useState<{ email?: string; password?: string }>({})

  const validateForm = (): boolean => {
    const errors: { email?: string; password?: string } = {}

    if (!formData.email) {
      errors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Invalid email format'
    }

    if (!formData.password) {
      errors.password = 'Password is required'
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    try {
      await signup(formData)
    } catch {
      // Error handled by useAuth hook
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-4">
      <div>
        <Input
          label="Email"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          error={formErrors.email}
          placeholder="you@example.com"
          required
        />
      </div>

      <div>
        <Input
          label="Password"
          type="password"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          error={formErrors.password}
          placeholder="••••••••"
          required
        />
      </div>

      {error && (
        <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive" role="alert">
          {error}
        </div>
      )}

      <Button type="submit" className="w-full" isLoading={isLoading}>
        {isLoading ? 'Creating account...' : 'Sign Up'}
      </Button>

      <p className="text-center text-sm text-secondary">
        Already have an account?{' '}
        <Link href="/login" className="font-medium text-primary hover:underline">
          Log in
        </Link>
      </p>
    </form>
  )
}
