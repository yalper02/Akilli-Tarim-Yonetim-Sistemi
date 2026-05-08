import Link from 'next/link'
import { serverFetch } from '@/lib/api'
import type { Farm, PaginatedResponse } from '@/types/api'

export default async function FarmsPage() {
  const data = await serverFetch<PaginatedResponse<Farm>>('/farms/')
  const farms = data?.results ?? []

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-800">Çiftliklerim</h1>
      <p className="mt-1 text-sm text-slate-500">Yönetmek istediğiniz çiftliği seçin.</p>

      {farms.length === 0 ? (
        <p className="mt-8 text-slate-400">Henüz kayıtlı çiftlik yok.</p>
      ) : (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {farms.map((farm) => (
            <Link
              key={farm.id}
              href={`/farms/${farm.id}`}
              className="flex flex-col gap-1 rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
            >
              <span className="font-semibold text-slate-800">{farm.name}</span>
              {farm.location && <span className="text-sm text-slate-500">{farm.location}</span>}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
