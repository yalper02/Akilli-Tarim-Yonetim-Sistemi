'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Cpu,
  BookMarked,
  Leaf,
  BarChart2,
  ChevronRight,
  Tractor,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import type { Farm } from '@/types/api'

interface SidebarProps {
  farms: Farm[]
}

const farmNavItems = [
  { href: '', label: 'Özet', icon: LayoutDashboard },
  { href: '/devices', label: 'Cihazlar', icon: Cpu },
  { href: '/rules', label: 'Kurallar', icon: BookMarked },
  { href: '/fertilization', label: 'Gübreleme', icon: Leaf },
  { href: '/reports', label: 'Raporlar', icon: BarChart2 },
]

export function Sidebar({ farms }: SidebarProps) {
  const pathname = usePathname()

  const farmMatch = pathname.match(/^\/farms\/(\d+)/)
  const activeFarmId = farmMatch ? parseInt(farmMatch[1]) : null
  const activeFarm = activeFarmId ? farms.find((f) => f.id === activeFarmId) : null

  return (
    <aside className="flex w-60 flex-col border-r border-slate-200 bg-white">
      <div className="flex h-14 items-center border-b border-slate-200 px-4">
        <span className="text-base font-semibold text-slate-800">🌱 Akıllı Tarım</span>
      </div>

      <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-3 py-4">
        <p className="mb-1 px-2 text-xs font-semibold tracking-wider text-slate-400 uppercase">
          Çiftliklerim
        </p>

        {farms.length === 0 && <p className="px-2 text-sm text-slate-400">Henüz çiftlik yok.</p>}

        {farms.map((farm) => (
          <Link
            key={farm.id}
            href={`/farms/${farm.id}`}
            className={cn(
              'flex items-center gap-2 rounded-md px-2 py-2 text-sm font-medium transition-colors',
              activeFarmId === farm.id
                ? 'bg-green-50 text-green-700'
                : 'text-slate-700 hover:bg-slate-100',
            )}
          >
            <Tractor className="h-4 w-4 flex-shrink-0" />
            <span className="flex-1 truncate">{farm.name}</span>
            {activeFarmId === farm.id && <ChevronRight className="h-3 w-3" />}
          </Link>
        ))}

        {activeFarm && (
          <>
            <div className="my-3 border-t border-slate-100" />
            <p className="mb-1 px-2 text-xs font-semibold tracking-wider text-slate-400 uppercase">
              {activeFarm.name}
            </p>
            {farmNavItems.map(({ href, label, icon: Icon }) => {
              const fullHref = `/farms/${activeFarmId}${href}`
              const isActive = href === '' ? pathname === fullHref : pathname.startsWith(fullHref)
              return (
                <Link
                  key={href}
                  href={fullHref}
                  className={cn(
                    'flex items-center gap-2 rounded-md px-2 py-2 text-sm transition-colors',
                    isActive
                      ? 'bg-slate-100 font-medium text-slate-900'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
                  )}
                >
                  <Icon className="h-4 w-4 flex-shrink-0" />
                  {label}
                </Link>
              )
            })}
          </>
        )}
      </nav>
    </aside>
  )
}
