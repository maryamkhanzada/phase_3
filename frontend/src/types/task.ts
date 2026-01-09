export interface Task {
  id: string
  title: string
  description: string | null
  completed: boolean
  user_id: string
  created_at: string
  updated_at: string
}

export interface TaskListResponse {
  tasks: Task[]
}

export interface TaskResponse {
  task: Task
}

export interface TaskFormData {
  title: string
  description?: string
}
