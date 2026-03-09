type Provider = "gemini" | "deepseek" | "openai" | "claude";

const BASE_KEYS: Record<Provider, string> = {
  gemini: "gemini_api_key",
  deepseek: "deepseek_api_key",
  openai: "openai_api_key",
  claude: "claude_api_key",
};

function getUserEmail(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem("user_email");
}

function namespacedKey(base: string): string {
  const email = getUserEmail();
  return email ? `${email}:${base}` : base;
}

export function getApiKey(provider: Provider): string | null {
  if (typeof window === "undefined") return null;
  const key = localStorage.getItem(namespacedKey(BASE_KEYS[provider]));
  if (key) return key;
  // Fallback: read legacy un-namespaced key and migrate it
  const email = getUserEmail();
  if (email) {
    const legacy = localStorage.getItem(BASE_KEYS[provider]);
    if (legacy) {
      localStorage.setItem(namespacedKey(BASE_KEYS[provider]), legacy);
      localStorage.removeItem(BASE_KEYS[provider]);
      return legacy;
    }
  }
  return null;
}

export function setApiKey(provider: Provider, value: string): void {
  localStorage.setItem(namespacedKey(BASE_KEYS[provider]), value);
}

export function removeApiKey(provider: Provider): void {
  localStorage.removeItem(namespacedKey(BASE_KEYS[provider]));
}

export function hasApiKey(provider: Provider): boolean {
  return getApiKey(provider) !== null;
}

export function clearSessionData(): void {
  sessionStorage.removeItem("id_token");
  sessionStorage.removeItem("user_email");
}
