"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useEffect } from "react";


export default function LoginPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      router.push("/");
    }
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    try {
      const res = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            "username_or_email": username,
          "password": password,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || "Invalid credentials");
        return;
      }

      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);

      router.push("/"); // redirect to main posts page
    } catch (err) {
      setError("Something went wrong");
    }
  }

  return (
    <div style={{
      maxWidth: 400,
      margin: "60px auto",
      padding: 20,
      border: "1px solid #ddd",
      borderRadius: 8
    }}>
      <h1>Login</h1>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <input
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          style={{ padding: 10, borderRadius: 6, border: "1px solid #ccc" }}
        />

        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          style={{ padding: 10, borderRadius: 6, border: "1px solid #ccc" }}
        />

        <button type="submit" style={{
          padding: 12,
          borderRadius: 6,
          background: "black",
          color: "white",
          cursor: "pointer"
        }}>
          Log in
        </button>
      </form>

      {error && <p style={{ color: "red", marginTop: 10 }}>{error}</p>}
    </div>
  );
}