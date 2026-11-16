(function () {
  const app = document.getElementById("app");
  const btnLogin = document.getElementById("btnLogin");
  const btnLogout = document.getElementById("btnLogout");

  function refreshAuthUi() {
    const on = OrbitCognito.isLoggedIn();
    btnLogin.style.display = on ? "none" : "inline-flex";
    btnLogout.style.display = on ? "inline-flex" : "none";
  }
  btnLogin.onclick = () => OrbitCognito.startLogin();
  btnLogout.onclick = () => OrbitCognito.startLogout();

  async function loadSessionStatus() {
    try {
      const r = await fetch("session/session_status.json", { cache: "no-store" });
      if (!r.ok) throw new Error("status " + r.status);
      return await r.json();
    } catch (e) {
      return { error: String(e), services: {}, agents_23: ORBIT_CONFIG.agents.map(a => a[0] + " " + a[1]) };
    }
  }

  function route() {
    const hash = (location.hash || "#home").replace("#", "");
    const routes = { home, swarm, session, auth, tools, ingest };
    (routes[hash] || home)();
    document.querySelectorAll("[data-nav]").forEach(a => {
      a.classList.toggle("active", a.getAttribute("href") === "#" + hash);
    });
  }

  async function home() {
    const st = await loadSessionStatus();
    const svc = st.services || {};
    const rows = Object.entries(svc).map(([k,v]) =>
      `<div class="row"><span>${k}</span><span class="${v&&v.ok?'ok':'bad'}">${v&&v.ok?'ACTIVE':'DOWN'}</span></div>`
    ).join("") || '<div class="muted">No status file — open after deploy</div>';
    app.innerHTML = `
      <div class="toolbar">
        <button class="btn primary" id="hLogin">Hosted UI Login</button>
        <a class="btn" href="#swarm">Open Swarm-23</a>
        <a class="btn" href="#ingest">Session Merge Prompt</a>
      </div>
      <div class="grid">
        <div class="card"><h2>Identity</h2>
          <div class="row"><span>Org</span><span>${ORBIT_CONFIG.org}</span></div>
          <div class="row"><span>Primary session</span><span class="muted" style="font-size:.7rem">${ORBIT_CONFIG.primarySession}</span></div>
          <div class="row"><span>Pool</span><span class="muted" style="font-size:.7rem">${ORBIT_CONFIG.userPoolId}</span></div>
          <div class="row"><span>Identity pool</span><span class="muted" style="font-size:.7rem">${ORBIT_CONFIG.identityPoolId}</span></div>
          <div class="row"><span>Auth</span><span class="${OrbitCognito.isLoggedIn()?'ok':'warn'}">${OrbitCognito.isLoggedIn()?'SIGNED IN':'GUEST'}</span></div>
        </div>
        <div class="card"><h2>Services</h2>${rows}</div>
        <div class="card"><h2>Quick links</h2>
          <div class="row"><a href="${ORBIT_CONFIG.hostedUiBase}" target="_blank">Hosted UI base</a></div>
          <div class="row"><a href="${ORBIT_CONFIG.githubRepo}" target="_blank">GitHub repo</a></div>
          <div class="row"><a href="${ORBIT_CONFIG.hfSpace}" target="_blank">HF Space</a></div>
          <div class="row"><a href="dashboard/">Static dashboard</a></div>
        </div>
      </div>`;
    document.getElementById("hLogin").onclick = () => OrbitCognito.startLogin();
  }

  function swarm() {
    const cards = ORBIT_CONFIG.agents.map(([id,name]) =>
      `<div class="agent">
        <div class="id">${id}</div>
        <div class="name">${name}</div>
        <div class="st ok">READY · individuality_lock</div>
        <button class="btn" data-run="${id}">Run task</button>
        <pre class="log" id="log-${id}" style="display:none"></pre>
      </div>`).join("");
    app.innerHTML = `
      <h2>Multi-Agent Swarm (23)</h2>
      <p class="muted">Client-side task simulator + log — server logs live under agents/</p>
      <div class="toolbar">
        <button class="btn primary" id="runAll">Run all agents</button>
        <button class="btn" id="exportLogs">Export logs JSON</button>
      </div>
      <div class="grid" id="agentGrid">${cards}</div>`;
    const logs = {};
    function runOne(id) {
      const name = ORBIT_CONFIG.agents.find(a => a[0]===id)[1];
      const rec = {
        agent: id, name,
        session_id: crypto.randomUUID(),
        parent: ORBIT_CONFIG.primarySession,
        ts: Date.now(),
        task: "client_tooling_ping",
        status: "OK"
      };
      logs[id] = logs[id] || [];
      logs[id].push(rec);
      const el = document.getElementById("log-" + id);
      el.style.display = "block";
      el.textContent = JSON.stringify(logs[id], null, 2);
    }
    document.querySelectorAll("[data-run]").forEach(b => b.onclick = () => runOne(b.dataset.run));
    document.getElementById("runAll").onclick = () => ORBIT_CONFIG.agents.forEach(a => runOne(a[0]));
    document.getElementById("exportLogs").onclick = () => {
      const blob = new Blob([JSON.stringify(logs,null,2)], {type:"application/json"});
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "swarm-client-logs.json";
      a.click();
    };
  }

  async function session() {
    const st = await loadSessionStatus();
    const user = OrbitCognito.currentUser();
    app.innerHTML = `
      <h2>Live Session</h2>
      <div class="grid">
        <div class="card"><h2>User</h2>
          <pre>${JSON.stringify(user || { note: "not signed in" }, null, 2)}</pre>
        </div>
        <div class="card"><h2>session_status.json</h2>
          <pre>${JSON.stringify(st, null, 2)}</pre>
        </div>
      </div>`;
  }

  function auth() {
    app.innerHTML = `
      <h2>Hosted UI Auth</h2>
      <div class="grid">
        <div class="card">
          <h2>Actions</h2>
          <div class="toolbar">
            <button class="btn primary" id="aLogin">Login (Hosted UI)</button>
            <button class="btn danger" id="aLogout">Logout</button>
            <a class="btn" href="auth/callback/">Callback route</a>
          </div>
          <div class="row"><span>Redirect URI</span><span class="muted">${OrbitCognito.redirectUri()}</span></div>
          <div class="row"><span>Client</span><span class="muted">${ORBIT_CONFIG.clientId}</span></div>
          <div class="row"><span>Identity pool</span><span class="muted">${ORBIT_CONFIG.identityPoolId}</span></div>
        </div>
        <div class="card"><h2>Tokens (local only)</h2>
          <pre>${JSON.stringify((() => { const t=OrbitCognito.loadTokens(); if(!t) return null; return { token_type:t.token_type, expires_in:t.expires_in, has_access:!!t.access_token, has_id:!!t.id_token, savedAt:t.savedAt }; })(), null, 2)}</pre>
        </div>
      </div>`;
    document.getElementById("aLogin").onclick = () => OrbitCognito.startLogin();
    document.getElementById("aLogout").onclick = () => OrbitCognito.startLogout();
  }

  function tools() {
    app.innerHTML = `
      <h2>Multi-agent tooling</h2>
      <div class="grid">
        <div class="card"><h2>Connected surfaces</h2>
          <div class="row"><span>GitHub</span><span class="ok">connector</span></div>
          <div class="row"><span>Vercel</span><span class="warn">403 create (push still works)</span></div>
          <div class="row"><span>HF CLI</span><span class="ok">albedd</span></div>
          <div class="row"><span>AWS profile mrcc</span><span class="ok">STS + Cognito</span></div>
          <div class="row"><span>Agent Toolkit</span><span class="ok">25 skills</span></div>
        </div>
        <div class="card"><h2>MCP / skills</h2>
          <p class="muted">Use SESSION_MERGE_V3_INGEST when switching session IDs.</p>
          <a class="btn" href="prompts/MULTI_SESSION_ID_INGESTION_PROMPT.md">Open ingestion prompt</a>
        </div>
        <div class="card"><h2>Bridge</h2>
          <a class="btn" href="bridge/cognito_auth.js">cognito_auth.js</a>
          <a class="btn" href="bridge/README.md">bridge README</a>
        </div>
      </div>`;
  }

  async function ingest() {
    let text = "";
    try {
      const r = await fetch("prompts/MULTI_SESSION_ID_INGESTION_PROMPT.md");
      text = await r.text();
    } catch (e) { text = "# missing prompt file locally\n" + e; }
    app.innerHTML = `
      <h2>Multi Session_ID Ingestion Prompt</h2>
      <p class="muted">Copy and paste into this thread when switching sessions/models/MCP.</p>
      <div class="toolbar">
        <button class="btn primary" id="copyPrompt">Copy full prompt</button>
      </div>
      <pre id="promptBox"></pre>`;
    document.getElementById("promptBox").textContent = text;
    document.getElementById("copyPrompt").onclick = async () => {
      await navigator.clipboard.writeText(text);
      alert("Copied ingestion prompt");
    };
  }

  window.addEventListener("hashchange", route);
  refreshAuthUi();
  route();
})();
