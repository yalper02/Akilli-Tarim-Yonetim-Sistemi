import { cookies } from 'next/headers'

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://127.0.0.1:8000'

async function getAuthToken(): Promise<string | null> {
  const cookieStore = await cookies()
  return cookieStore.get('access_token')?.value ?? null
}

/** Sunucu bileşenlerinde kimlik doğrulamalı API isteği yapar. */
export async function serverFetch<T>(path: string): Promise<T | null> {
  const token = await getAuthToken()
  if (!token) return null
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1${path}`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store',
    })
    if (!res.ok) return null
    return res.json() as Promise<T>
  } catch {
    return null
  }
}
