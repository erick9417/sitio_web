"use client";

import { useAuth, login } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const ok = await login(email, password);
      if (ok) {
        router.push('/products');
      } else {
        setError('Correo o contraseña incorrectos');
      }
    } catch (err: any) {
      // Cuando el backend no está disponible o hay CORS, axios lanza "Network Error"
      setError('No se pudo conectar con el servidor. Intenta de nuevo en unos segundos.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-xl shadow-lg p-8 flex flex-col items-center w-full max-w-sm gap-4"
      >
        <img
          src="/logo1.png"
          alt="Logo Ortomedica"
          className="w-28 mb-4"
        />
        <h2 className="text-2xl font-bold text-blue-900 mb-2 text-center">Iniciar sesión</h2>
        <input
          type="email"
          placeholder="Correo electrónico"
          value={email}
          required
          onChange={e => setEmail(e.target.value)}
          className="w-full px-4 py-2 rounded-md border border-blue-200 text-base focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          required
          onChange={e => setPassword(e.target.value)}
          className="w-full px-4 py-2 rounded-md border border-blue-200 text-base focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        {error && (
          <div className="w-full text-center text-red-600 text-sm">{error}</div>
        )}
        <button
          type="submit"
          className="w-full bg-blue-900 text-white rounded-md py-2 font-semibold text-base mt-2 hover:bg-blue-800 transition"
        >
          Iniciar sesión
        </button>
      </form>
    </div>
  );
}
// ...existing code...