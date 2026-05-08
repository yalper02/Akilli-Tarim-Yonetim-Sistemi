'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const LoginSchema = z.object({
  username: z.string().min(1, { message: 'Kullanıcı adı gereklidir.' }),
  password: z.string().min(1, { message: 'Şifre gereklidir.' }),
})

type LoginInput = z.infer<typeof LoginSchema>

export default function LoginPage() {
  const router = useRouter()
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginInput>({
    resolver: zodResolver(LoginSchema),
  })

  async function onSubmit(data: LoginInput) {
    setServerError(null)

    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })

    if (res.ok) {
      router.push('/farms')
    } else {
      const body = await res.json().catch(() => ({}))
      setServerError(body.detail ?? 'Giriş başarısız. Bilgilerinizi kontrol edin.')
    }
  }

  return (
    <div className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <div className="mb-8 text-center">
        <div className="mb-2 text-3xl">🌱</div>
        <h1 className="text-xl font-semibold text-slate-800">Akıllı Tarım Sistemi</h1>
        <p className="mt-1 text-sm text-slate-500">Hesabınıza giriş yapın</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        <div>
          <label htmlFor="username" className="mb-1.5 block text-sm font-medium text-slate-700">
            Kullanıcı adı
          </label>
          <Input
            id="username"
            type="text"
            autoComplete="username"
            autoFocus
            disabled={isSubmitting}
            aria-invalid={!!errors.username}
            {...register('username')}
          />
          {errors.username && (
            <p className="mt-1 text-xs text-red-600">{errors.username.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-slate-700">
            Şifre
          </label>
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            disabled={isSubmitting}
            aria-invalid={!!errors.password}
            {...register('password')}
          />
          {errors.password && (
            <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
          )}
        </div>

        {serverError && (
          <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{serverError}</div>
        )}

        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? 'Giriş yapılıyor…' : 'Giriş Yap'}
        </Button>
      </form>
    </div>
  )
}
