'use client'

import { TaskForm } from '@/components/tasks/TaskForm'
import { useTasks } from '@/hooks/useTasks'
import type { TaskFormData } from '@/types/task'

export default function NewTaskPage() {
  const { createTask } = useTasks()

  const handleSubmit = async (formData: TaskFormData) => {
    await createTask(formData)
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-2xl font-bold">Create New Task</h1>
      <div className="rounded-lg border border-border bg-background p-6">
        <TaskForm onSubmit={handleSubmit} submitLabel="Create Task" />
      </div>
    </div>
  )
}
