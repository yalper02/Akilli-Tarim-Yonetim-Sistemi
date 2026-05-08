import { cookies } from 'next/headers'

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://127.0.0.1:8000'

export async function POST(request: Request) {
  const body = await request.json()

  const djangoRes = await fetch(`${BACKEND_URL}/api/v1/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  // Rate limit veya sunucu hatası durumunda HTML dönebilir
  const contentType = djangoRes.headers.get('content-type') ?? ''
  if (!contentType.includes('application/json')) {
    const status = djangoRes.status === 403 ? 429 : djangoRes.status
    return Response.json(
      { detail: 'Çok fazla deneme yapıldı. Lütfen bekleyin.' },
      { status },
    )
  }

  const data = await djangoRes.json()

  if (!djangoRes.ok) {
    return Response.json(data, { status: djangoRes.status })
  }

  const cookieStore = await cookies()
  const isProd = process.env.NODE_ENV === 'production'

  cookieStore.set('access_token', data.access, {
    httpOnly: true,
    secure: isProd,
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 15,
  })

  cookieStore.set('refresh_token', data.refresh, {
    httpOnly: true,
    secure: isProd,
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 24 * 7,
  })

  return Response.json({ ok: true })
}
