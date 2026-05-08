'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'

export function LogoutButton() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  async function handleLogout() {
    setLoading(true)
    await fetch('/api/auth/logout', { method: 'POST' })
    router.push('/login')
  }

  return (
    <Button variant="ghost" size="sm" disabled={loading} onClick={handleLogout}>
      {loading ? 'Çıkış…' : 'Çıkış Yap'}
    </Button>
  )
}
