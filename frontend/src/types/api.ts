export interface ErrorResponse {
  error: string
}

export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

export interface FormErrors {
  [key: string]: string | undefined
}

export interface APIError {
  message: string
  status?: number
}
