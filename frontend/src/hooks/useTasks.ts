'use client'

import { apiClient } from '@/lib/api-client'
import type { Task, TaskFormData, TaskListResponse, TaskResponse } from '@/types/task'
import { useCallback, useState } from 'react'

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTasks = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await apiClient<TaskListResponse>('/api/tasks')
      setTasks(data.tasks)
      return data.tasks
    } catch (err) {
      setError((err as { message: string }).message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const fetchTaskById = useCallback(async (id: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await apiClient<TaskResponse>(`/api/tasks/${id}`)
      return data.task
    } catch (err) {
      setError((err as { message: string }).message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const createTask = useCallback(
    async (formData: TaskFormData) => {
      setIsLoading(true)
      setError(null)

      try {
        const data = await apiClient<TaskResponse>('/api/tasks', {
          method: 'POST',
          body: JSON.stringify(formData),
        })

        setTasks((prev) => [...prev, data.task])
        return data.task
      } catch (err) {
        setError((err as { message: string }).message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  const updateTask = useCallback(
    async (id: string, updates: Partial<TaskFormData & { completed: boolean }>) => {
      setIsLoading(true)
      setError(null)

      try {
        const data = await apiClient<TaskResponse>(`/api/tasks/${id}`, {
          method: 'PUT',
          body: JSON.stringify(updates),
        })

        setTasks((prev) => prev.map((task) => (task.id === id ? data.task : task)))
        return data.task
      } catch (err) {
        setError((err as { message: string }).message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  const deleteTask = useCallback(async (id: string) => {
    setIsLoading(true)
    setError(null)

    try {
      await apiClient(`/api/tasks/${id}`, { method: 'DELETE' })
      setTasks((prev) => prev.filter((task) => task.id !== id))
    } catch (err) {
      setError((err as { message: string }).message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const toggleCompletion = useCallback(
    async (id: string, completed: boolean) => {
      const originalTasks = [...tasks]

      setTasks((prev) =>
        prev.map((task) => (task.id === id ? { ...task, completed } : task))
      )

      try {
        await updateTask(id, { completed })
      } catch {
        setTasks(originalTasks)
        throw new Error('Failed to update task')
      }
    },
    [tasks, updateTask]
  )

  return {
    tasks,
    isLoading,
    error,
    fetchTasks,
    fetchTaskById,
    createTask,
    updateTask,
    deleteTask,
    toggleCompletion,
  }
}
