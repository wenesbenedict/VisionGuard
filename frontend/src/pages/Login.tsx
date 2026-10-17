import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { login } from '../api'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await login(email, password)
      const from = (location.state as { from?: { pathname?: string; search?: string; hash?: string } } | null)?.from
      const destination = from
        ? `${from.pathname || '/'}${from.search || ''}${from.hash || ''}`
        : '/'
      navigate(destination, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-10">
      <h1 className="text-2xl font-bold mb-4">Login</h1>
      <form onSubmit={submit} className="space-y-3">
        <input className="bg-slate-800 rounded p-2 w-full" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" autoComplete="username" required />
        <input className="bg-slate-800 rounded p-2 w-full" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" type="password" autoComplete="current-password" required />
        <button disabled={busy} className="bg-sky-600 hover:bg-sky-500 rounded px-4 py-2 disabled:opacity-50">{busy ? 'Signing in…' : 'Login'}</button>
        {error && <p role="alert" className="text-red-400">{error}</p>}
      </form>
    </div>
  )
}
