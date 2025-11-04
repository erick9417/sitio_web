// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider, Navigate, Outlet } from "react-router-dom";
import CatalogPage from "./pages/Catalog";
import LoginPage from "./pages/Login";
import "./index.css";

function Protected() {
  const token = localStorage.getItem("token");
  if (!token) return <Navigate to="/login" replace />;
  return <Outlet />;
}

const router = createBrowserRouter([
  { element: <Protected />, children: [
      { path: "/", element: <CatalogPage /> },
    ]
  },
  { path: "/login", element: <LoginPage /> },
  { path: "*", element: <Navigate to="/" replace /> },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router}/>
  </React.StrictMode>
);
