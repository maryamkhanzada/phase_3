'use client'

import { Loader } from '@/components/ui/Loader'
import { TaskForm } from '@/components/tasks/TaskForm'
import { useTasks } from '@/hooks/useTasks'
import type { TaskFormData } from '@/types/task'
import { useParams } from 'next/navigation'
import { useCallback, useEffect, useState } from 'react'

export default function EditTaskPage() {
  const params = useParams()
  const taskId = params.id as string
  const { fetchTaskById, updateTask } = useTasks()
  const [task, setTask] = useState<Awaited<ReturnType<typeof fetchTaskById>> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadTask = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const fetchedTask = await fetchTaskById(taskId)
        setTask(fetchedTask)
      } catch (err) {
        setError((err as { message: string }).message || 'Task not found')
      } finally {
        setIsLoading(false)
      }
    }

    loadTask()
  }, [taskId, fetchTaskById])

  const handleSubmit = useCallback(
    async (formData: TaskFormData) => {
      await updateTask(taskId, formData)
    },
    [taskId, updateTask]
  )

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl">
        <h1 className="mb-6 text-2xl font-bold">Edit Task</h1>
        <Loader />
      </div>
    )
  }

  if (error || !task) {
    return (
      <div className="mx-auto max-w-2xl">
        <h1 className="mb-6 text-2xl font-bold">Edit Task</h1>
        <div className="rounded-md bg-destructive/10 p-4 text-destructive">
          <p className="font-medium">Error loading task</p>
          <p className="mt-1 text-sm">{error || 'Task not found'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-2xl font-bold">Edit Task</h1>
      <div className="rounded-lg border border-border bg-background p-6">
        <TaskForm initialData={task} onSubmit={handleSubmit} submitLabel="Save Changes" />
      </div>
    </div>
  )
}
