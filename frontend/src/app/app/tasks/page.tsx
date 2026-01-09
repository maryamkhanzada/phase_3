'use client'

import { Button } from '@/components/ui/Button'
import { Loader } from '@/components/ui/Loader'
import { TaskList } from '@/components/tasks/TaskList'
import { useTasks } from '@/hooks/useTasks'
import Link from 'next/link'
import { useEffect } from 'react'

export default function TasksPage() {
  const { tasks, isLoading, error, fetchTasks, toggleCompletion, deleteTask } = useTasks()

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  if (isLoading && tasks.length === 0) {
    return (
      <div>
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold">My Tasks</h1>
        </div>
        <Loader />
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h1 className="mb-6 text-2xl font-bold">My Tasks</h1>
        <div className="rounded-md bg-destructive/10 p-4 text-destructive">
          <p className="font-medium">Error loading tasks</p>
          <p className="mt-1 text-sm">{error}</p>
          <Button className="mt-4" onClick={() => fetchTasks()} variant="secondary">
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">My Tasks</h1>
        <Link href="/app/tasks/new">
          <Button>New Task</Button>
        </Link>
      </div>

      <TaskList
        tasks={tasks}
        onToggle={toggleCompletion}
        onDelete={deleteTask}
      />
    </div>
  )
}
