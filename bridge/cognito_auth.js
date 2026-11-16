/** Orbit Chat Hub — Cognito Hosted UI + token helpers (public client) */
export const COGNITO = {
  region: "us-east-1",
  userPoolId: "us-east-1_yr5vuS7Kz",
  clientId: "1t94d90dg0lc6uiemlukj98p5u",
  domain: "orbit-echo-ec69-1yr5vus7kz",
  get base() {
    return `https://${this.domain}.auth.${this.region}.amazoncognito.com`;
  },
  loginUrl(redirectUri) {
    const u = new URL(this.base + "/login");
    u.searchParams.set("client_id", this.clientId);
    u.searchParams.set("response_type", "code");
    u.searchParams.set("scope", "openid email profile");
    u.searchParams.set("redirect_uri", redirectUri);
    return u.toString();
  },
  logoutUrl(logoutUri) {
    const u = new URL(this.base + "/logout");
    u.searchParams.set("client_id", this.clientId);
    u.searchParams.set("logout_uri", logoutUri);
    return u.toString();
  },
};
