import { useState } from 'react'
import { login } from '../api'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const [email, setEmail] = useState('admin@visionguard.local')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError('Invalid credentials')
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-10">
      <h1 className="text-2xl font-bold mb-4">Login</h1>
      <form onSubmit={submit} className="space-y-3">
        <input className="bg-slate-800 rounded p-2 w-full" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" />
        <input className="bg-slate-800 rounded p-2 w-full" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" />
        <button className="bg-sky-600 hover:bg-sky-500 rounded px-4 py-2">Login</button>
        {error && <p className="text-red-400">{error}</p>}
      </form>
    </div>
  )
}
