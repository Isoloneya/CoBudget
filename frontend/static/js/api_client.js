const TOKEN_KEY = "cobudget_token";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function isAuthenticated() {
  return Boolean(getToken());
}

async function apiFetch(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(path, { ...options, headers });
  } catch (networkError) {
    throw { code: "NETWORK_ERROR", message: "Не вдалося з'єднатися з сервером" };
  }

  if (response.status === 401) {
    clearToken();
    window.location.href = "/login.html";
    throw { code: "UNAUTHORIZED", message: "Сесія завершена, увійдіть знову" };
  }

  if (!response.ok) {
    let body = null;
    try {
      body = await response.json();
    } catch (parseError) {
      body = null;
    }
    const error = body && body.error ? body.error : { code: "ERROR", message: "Сталася помилка" };
    throw error;
  }

  if (response.status === 204) return null;
  return response.json();
}

async function apiLogin(email, password) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const response = await fetch("/auth/login", { method: "POST", body });

  if (!response.ok) {
    let parsed = null;
    try {
      parsed = await response.json();
    } catch (parseError) {
      parsed = null;
    }
    const error = parsed && parsed.error ? parsed.error : { code: "ERROR", message: "Не вдалося увійти" };
    throw error;
  }

  const data = await response.json();
  setToken(data.access_token);
  return data;
}

function showToast(message, variant = "success") {
  const el = document.createElement("div");
  el.textContent = message;
  el.style.cssText = `
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    background: ${variant === "error" ? "#FF6B6B" : "#34D399"};
    color: #0B0B0C; font-family: 'Manrope', sans-serif; font-weight: 700;
    font-size: 13.5px; padding: 12px 20px; border-radius: 100px;
    box-shadow: 0 8px 20px -6px rgba(0,0,0,0.3); z-index: 9999;
  `;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}