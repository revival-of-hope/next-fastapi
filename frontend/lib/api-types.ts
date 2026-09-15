export type MessageRole = "user" | "assistant"

export type UserPublic = {
  id: number
  name: string
  created_at: string
  is_active: boolean
}

export type Token = {
  access_token: string
  token_type: string
}

export type ConversationPublic = {
  conversation_id: number
  title: string | null
  created_at: string
  updated_at: string
}

export type MessagePublic = {
  message_id: number
  conversation_id: number | null
  role: MessageRole
  content: string
  created_at: string
}

export type ChatRequest = {
  conversation_id?: number | null
  content: string
}
