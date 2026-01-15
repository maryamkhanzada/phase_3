'use client'

import { useState } from 'react'
import { ChatIcon } from './ChatIcon'
import { ChatPopup } from './ChatPopup'

interface ChatContainerProps {
  userId: string
}

export function ChatContainer({ userId }: ChatContainerProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {!isOpen && <ChatIcon onClick={() => setIsOpen(true)} />}
      {isOpen && <ChatPopup userId={userId} onClose={() => setIsOpen(false)} />}
    </>
  )
}
