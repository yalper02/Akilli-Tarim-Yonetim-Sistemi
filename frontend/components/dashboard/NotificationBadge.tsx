'use client'

import { Bell } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { NotificationsDrawer } from '@/components/dashboard/NotificationsDrawer'
import { clientFetch } from '@/lib/client-api'

interface NotificationBadgeProps {
  initialCount: number
}

export function NotificationBadge({ initialCount }: NotificationBadgeProps) {
  const [count, setCount] = useState(initialCount)
  const [open, setOpen] = useState(false)
  const queryClient = useQueryClient()

  // Bildirim cache'i değiştiğinde okunmamış sayacını güncelle
  useEffect(() => {
    return queryClient.getQueryCache().subscribe((event) => {
      if (
        event.type === 'updated' &&
        Array.isArray(event.query.queryKey) &&
        event.query.queryKey[0] === 'notifications'
      ) {
        void clientFetch<{ unread_count: number }>('/notifications/unread-count/').then((data) =>
          setCount(data.unread_count),
        )
      }
    })
  }, [queryClient])

  // Drawer kapandığında sayacı yenile
  function handleClose() {
    setOpen(false)
    void clientFetch<{ unread_count: number }>('/notifications/unread-count/').then((data) =>
      setCount(data.unread_count),
    )
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="relative rounded-md p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-700"
        aria-label="Bildirimler"
      >
        <Bell className="h-5 w-5" />
        {count > 0 && (
          <span className="absolute top-0 right-0 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
            {count > 9 ? '9+' : count}
          </span>
        )}
      </button>

      {open && <NotificationsDrawer onClose={handleClose} />}
    </>
  )
}
