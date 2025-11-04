import React from "react";
import "./topbar.css";

type Props = {
  q: string;
  onSearch: (v: string) => void;
  onRunIngest: () => void;
  autoStatus: { status: "idle" | "running" | "error"; lastRun?: string };
  userName?: string;
  onLogout?: () => void;
  pageTitle?: string;
};

export default function TopBar({
  q,
  onSearch,
  onRunIngest,
  autoStatus,
  userName,
  onLogout,
  pageTitle = "Catálogo",
}: Props) {
  return (
    <header className="tb">
      <div className="tb__left">
        {/* Coloca tu logo en /public/logo.png */}
        <img className="tb__logo" src="/logo.png" alt="Ortomédica" />
        <span className="tb__title">{pageTitle}</span>
      </div>

      <div className="tb__center">
        <div className="tb__search">
          <input
            value={q}
            onChange={(e) => onSearch(e.target.value)}
            placeholder="Buscar productos..."
            aria-label="Buscar productos"
          />
          <button aria-label="Buscar">
            <span className="material-icons">search</span>
          </button>
        </div>
        <small className="tb__status">
          Auto-refresco cada 60s · Estado:{" "}
          <b
            className={
              autoStatus.status === "running"
                ? "ok"
                : autoStatus.status === "error"
                ? "err"
                : ""
            }
          >
            {autoStatus.status}
          </b>
          {autoStatus.lastRun ? (
            <>
              {" "}
              · Última actualización: <b>{autoStatus.lastRun}</b>
            </>
          ) : null}
        </small>
      </div>

      <div className="tb__right">
        <button className="tb__refresh" onClick={onRunIngest}>
          Actualizar
        </button>

        {userName ? (
          <div className="tb__user">
            <span>{userName}</span>
            <button onClick={onLogout}>Salir</button>
          </div>
        ) : null}
      </div>
    </header>
  );
}
