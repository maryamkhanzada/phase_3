'use client'

import type { Task } from '@/types/task'
import Link from 'next/link'
import { Button } from '../ui/Button'
import { TaskCard } from './TaskCard'

interface TaskListProps {
  tasks: Task[]
  onToggle: (id: string, completed: boolean) => void
  onDelete: (id: string) => void
}

export function TaskList({ tasks, onToggle, onDelete }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-border bg-background p-12 text-center">
        <h3 className="text-lg font-medium">No tasks yet</h3>
        <p className="mt-2 text-sm text-secondary">
          Create your first task to get started
        </p>
        <Link href="/app/tasks/new">
          <Button className="mt-4">Create Task</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}
