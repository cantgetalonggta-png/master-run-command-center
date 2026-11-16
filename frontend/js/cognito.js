/** Cognito Hosted UI + token storage (public client SPA) */
(function (global) {
  const C = () => global.ORBIT_CONFIG;
  const STORAGE_KEY = "orbit_cognito_tokens";

  function redirectUri() {
    // prefer /auth/callback relative to origin
    return global.location.origin + "/auth/callback/";
  }
  function logoutUri() {
    return global.location.origin + "/";
  }
  function loginUrl(extra) {
    const c = C();
    const u = new URL(c.hostedUiBase + "/login");
    u.searchParams.set("client_id", c.clientId);
    u.searchParams.set("response_type", "code");
    u.searchParams.set("scope", "openid email profile");
    u.searchParams.set("redirect_uri", redirectUri());
    if (extra && extra.state) u.searchParams.set("state", extra.state);
    return u.toString();
  }
  function logoutUrl() {
    const c = C();
    const u = new URL(c.hostedUiBase + "/logout");
    u.searchParams.set("client_id", c.clientId);
    u.searchParams.set("logout_uri", logoutUri());
    return u.toString();
  }
  function saveTokens(t) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...t, savedAt: Date.now() }));
  }
  function loadTokens() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "null"); } catch { return null; }
  }
  function clearTokens() { localStorage.removeItem(STORAGE_KEY); }
  function isLoggedIn() {
    const t = loadTokens();
    return !!(t && (t.id_token || t.access_token));
  }
  async function exchangeCode(code) {
    const c = C();
    const body = new URLSearchParams({
      grant_type: "authorization_code",
      client_id: c.clientId,
      code,
      redirect_uri: redirectUri(),
    });
    const res = await fetch(c.hostedUiBase + "/oauth2/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!res.ok) throw new Error("token_exchange_failed " + res.status + " " + (await res.text()));
    const json = await res.json();
    saveTokens(json);
    return json;
  }
  function parseJwt(token) {
    try {
      const p = token.split(".")[1];
      return JSON.parse(atob(p.replace(/-/g, "+").replace(/_/g, "/")));
    } catch { return null; }
  }
  function currentUser() {
    const t = loadTokens();
    if (!t || !t.id_token) return null;
    return parseJwt(t.id_token);
  }
  global.OrbitCognito = {
    loginUrl, logoutUrl, redirectUri, logoutUri,
    exchangeCode, saveTokens, loadTokens, clearTokens,
    isLoggedIn, currentUser, parseJwt,
    startLogin() { global.location.href = loginUrl({ state: "orbit-" + Date.now() }); },
    startLogout() { clearTokens(); global.location.href = logoutUrl(); },
  };
})(window);
