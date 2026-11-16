/** Expandable multi-agent tooling registry for ORBIT swarm */
export const TOOL_REGISTRY = {
  "file.read": { desc: "Read workspace file", risk: "low" },
  "file.search": { desc: "Search code", risk: "low" },
  "aws.sts": { desc: "Verify AWS identity", risk: "low" },
  "cognito.auth": { desc: "Hosted UI / token flows", risk: "med" },
  "hf.buckets": { desc: "HF bucket list/sync", risk: "med" },
  "github.push": { desc: "Commit durable state", risk: "med" },
  "swarm.delegate": { desc: "Delegate to agent session_id", risk: "low" },
  "session.merge": { desc: "SESSION_MERGE_V3_INGEST", risk: "low" },
  "stress.inject": { desc: "Failure injection tick", risk: "low" },
};
export function toolsForAgent(agentId) {
  const base = ["file.read", "file.search", "swarm.delegate", "session.merge"];
  if (agentId.startsWith("DEP")) return base.concat(["aws.sts", "github.push", "stress.inject"]);
  if (agentId.startsWith("FE")) return base.concat(["cognito.auth"]);
  if (agentId.startsWith("RS")) return base.concat(["hf.buckets"]);
  if (agentId.startsWith("LC")) return base.concat(["file.read"]);
  return base;
}
