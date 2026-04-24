const API = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiGet(path, token) {
  const res = await fetch(`${API}${path}`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || `GET ${path} failed`);
  return res.json();
}

export async function apiSend(path, method, body, token) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `${method} ${path} failed`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export async function apiUpload(path, formData, token) {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: authHeaders(token),
    body: formData,
  });
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || `Upload ${path} failed`);
  return res.json();
}

export const API_URL = API;
