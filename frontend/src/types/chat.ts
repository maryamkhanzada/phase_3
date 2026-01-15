/**
 * TypeScript types for chat/chatbot functionality
 */

export interface ToolCall {
  tool: string;
  parameters: Record<string, any>;
  result: any;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: ToolCall[];
  timestamp: string;
}

export interface ChatRequest {
  conversation_id?: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  tool_calls?: ToolCall[];
  timestamp: string;
}
