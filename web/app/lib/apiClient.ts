export async function apiFetch(
    path: string,
    options: RequestInit = {}
  ) {
    const baseUrl = "http://localhost:8000"; // your FastAPI URL
    const token = typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null;
  
    const headers = new Headers(options.headers || {});
    headers.set("Content-Type", "application/json");
  
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  
    const res = await fetch(`${baseUrl}${path}`, {
      ...options,
      headers,
    });
  
    // Optional: handle 401 globally here
    // if (res.status === 401) { ... }
  
    return res;
  }