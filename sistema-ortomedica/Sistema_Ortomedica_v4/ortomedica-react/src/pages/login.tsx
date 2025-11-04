// src/pages/Login.tsx
import React from "react";
import { login } from "../api";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const nav = useNavigate();
  const [email, setEmail] = React.useState("epadilla@ortomedica.com");
  const [password, setPassword] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      setLoading(true);
      const { access_token } = await login(email, password);
      localStorage.setItem("token", access_token);
      nav("/", { replace: true }); // al catálogo
    } catch (err: any) {
      alert("Usuario o contraseña incorrectos");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight:"100vh", display:"grid", placeItems:"center",
      background:"#f6f7fb"
    }}>
      <form onSubmit={onSubmit}
        style={{
          width:360, background:"#fff", padding:24, borderRadius:12,
          boxShadow:"0 8px 24px rgba(0,0,0,.08)", border:"1px solid #e5e7eb"
        }}>
        <h2 style={{margin:"0 0 16px 0"}}>Login</h2>

        <label style={{display:"block", fontSize:12, color:"#6b7280"}}>Email</label>
        <input
          value={email}
          onChange={e=>setEmail(e.target.value)}
          type="email"
          required
          style={{width:"100%", height:36, margin:"6px 0 14px 0", padding:"0 10px",
                  border:"1px solid #d1d5db", borderRadius:8}}
        />

        <label style={{display:"block", fontSize:12, color:"#6b7280"}}>Contraseña</label>
        <input
          value={password}
          onChange={e=>setPassword(e.target.value)}
          type="password"
          required
          style={{width:"100%", height:36, margin:"6px 0 14px 0", padding:"0 10px",
                  border:"1px solid #d1d5db", borderRadius:8}}
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            width:"100%", height:38, borderRadius:8, border:"1px solid #2563eb",
            background:"#2563eb", color:"#fff", cursor:"pointer"
          }}>
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
