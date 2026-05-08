import { cookies } from 'next/headers'

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://127.0.0.1:8000'

async function proxy(request: Request, params: Promise<{ path: string[] }>, method: string) {
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    return Response.json({ detail: 'Oturum açılmamış.' }, { status: 401 })
  }

  const { path } = await params
  const url = new URL(request.url)
  const backendUrl = `${BACKEND_URL}/api/v1/${path.join('/')}/${url.search}`

  try {
    const body = method !== 'GET' && method !== 'HEAD' ? await request.text() : undefined

    const res = await fetch(backendUrl, {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      ...(body ? { body } : {}),
    })

    const data = await res.json().catch(() => null)
    return Response.json(data, { status: res.status })
  } catch {
    return Response.json({ detail: 'Bağlantı hatası.' }, { status: 502 })
  }
}

export async function GET(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  return proxy(request, params, 'GET')
}

export async function POST(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  return proxy(request, params, 'POST')
}

export async function PATCH(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  return proxy(request, params, 'PATCH')
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ path: string[] }> },
) {
  return proxy(request, params, 'DELETE')
}
