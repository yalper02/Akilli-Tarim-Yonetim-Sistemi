import { cookies } from 'next/headers'

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://127.0.0.1:8000'

export async function POST() {
  const cookieStore = await cookies()
  const refresh = cookieStore.get('refresh_token')?.value

  if (refresh) {
    try {
      await fetch(`${BACKEND_URL}/api/v1/auth/logout/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      })
    } catch {
      // Best effort — clear cookies regardless of Django response
    }
  }

  cookieStore.delete('access_token')
  cookieStore.delete('refresh_token')

  return Response.json({ ok: true })
}
