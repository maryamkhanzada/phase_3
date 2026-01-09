'use client'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import type { Task, TaskFormData } from '@/types/task'
import { useRouter } from 'next/navigation'
import { FormEvent, useState } from 'react'

interface TaskFormProps {
  initialData?: Task
  onSubmit: (data: TaskFormData) => Promise<void>
  submitLabel?: string
}

export function TaskForm({
  initialData,
  onSubmit,
  submitLabel = 'Create Task',
}: TaskFormProps) {
  const router = useRouter()
  const [formData, setFormData] = useState<TaskFormData>({
    title: initialData?.title || '',
    description: initialData?.description || '',
  })
  const [formErrors, setFormErrors] = useState<{ title?: string }>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const validateForm = (): boolean => {
    const errors: { title?: string } = {}

    if (!formData.title.trim()) {
      errors.title = 'Title is required'
    } else if (formData.title.length > 255) {
      errors.title = 'Title must be less than 255 characters'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!validateForm()) return

    setIsSubmitting(true)

    try {
      await onSubmit(formData)
      router.push('/app/tasks')
    } catch (err) {
      setError((err as { message: string }).message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    router.push('/app/tasks')
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <Input
          label="Title"
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          error={formErrors.title}
          placeholder="Enter task title"
          required
        />
      </div>

      <div>
        <label htmlFor="description" className="mb-2 block text-sm font-medium">
          Description (optional)
        </label>
        <textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Enter task description"
          rows={4}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </div>

      {error && (
        <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive" role="alert">
          {error}
        </div>
      )}

      <div className="flex gap-3">
        <Button type="submit" isLoading={isSubmitting} className="flex-1">
          {isSubmitting ? 'Saving...' : submitLabel}
        </Button>
        <Button type="button" variant="ghost" onClick={handleCancel} className="flex-1">
          Cancel
        </Button>
      </div>
    </form>
  )
}
