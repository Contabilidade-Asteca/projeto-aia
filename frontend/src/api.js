const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function setGroqKey(apiKey) {
  const res = await fetch(`${API_BASE}/api/set-key`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ apiKey }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Erro ao salvar a chave.");
  }
  return res.json();
}

export async function clearGroqKey() {
  const res = await fetch(`${API_BASE}/api/clear-key`, {
    method: "POST",
    credentials: "include",
  });
  return res.json();
}

export async function sendChat(message) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Erro no chat.");
  }
  return res.json();
}
