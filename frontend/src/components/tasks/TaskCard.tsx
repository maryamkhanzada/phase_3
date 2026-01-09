'use client'

import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { cn } from '@/lib/utils'
import type { Task } from '@/types/task'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

interface TaskCardProps {
  task: Task
  onToggle: (id: string, completed: boolean) => void
  onDelete: (id: string) => void
}

export function TaskCard({ task, onToggle, onDelete }: TaskCardProps) {
  const router = useRouter()
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleToggle = () => {
    onToggle(task.id, !task.completed)
  }

  const handleDelete = async () => {
    setIsDeleting(true)
    try {
      await onDelete(task.id)
      setIsDeleteModalOpen(false)
    } catch {
      // Error handled by parent
    } finally {
      setIsDeleting(false)
    }
  }

  const handleEdit = () => {
    router.push(`/app/tasks/${task.id}/edit`)
  }

  return (
    <>
      <div className="rounded-lg border border-border bg-background p-4 transition-shadow hover:shadow-md">
        <div className="flex items-start gap-3">
          <button
            onClick={handleToggle}
            className="mt-1 h-5 w-5 flex-shrink-0 rounded border-2 border-primary transition-colors hover:bg-primary/10 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
          >
            {task.completed && (
              <svg
                className="h-full w-full text-primary"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </button>

          <div className="flex-1 min-w-0">
            <h3
              className={cn(
                'text-lg font-medium',
                task.completed && 'text-secondary line-through'
              )}
            >
              {task.title}
            </h3>
            {task.description && (
              <p
                className={cn(
                  'mt-1 text-sm',
                  task.completed ? 'text-secondary/70' : 'text-secondary',
                  'line-clamp-2'
                )}
              >
                {task.description}
              </p>
            )}
          </div>

          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleEdit}
              aria-label="Edit task"
            >
              Edit
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsDeleteModalOpen(true)}
              className="text-destructive hover:bg-destructive/10"
              aria-label="Delete task"
            >
              Delete
            </Button>
          </div>
        </div>
      </div>

      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleDelete}
        title="Delete Task"
        description="Are you sure you want to delete this task? This action cannot be undone."
        confirmText={isDeleting ? 'Deleting...' : 'Delete'}
        confirmVariant="danger"
      />
    </>
  )
}
