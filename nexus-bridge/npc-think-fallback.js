import { OpenCodeACPBridge } from "./opencode-acp-client.js";

/**
 * NPC Consciousness System → OpenCode ACP fallback bridge.
 * Connects to NEXUS Core v2 MCP Server + WebSocket Gateway.
 * npc_think tool'u LLM'e gitmeden önce OpenCode'a danışır.
 * 3-tier routing: rule-engine → OpenCode ACP → LLM fallback
 */
export class NPCThinkFallback {
  constructor(opts = {}) {
    this.bridge = new OpenCodeACPBridge({ config: opts.config });
    this.wsUrl = opts.wsUrl || "ws://localhost:8000/ws";
    this.ws = null;
    this._pending = {};
    this._id = 0;
    this.domainMap = opts.domainMap || {
      "trade": "pine-architect",
      "combat": "ai-systems-architect",
      "dialog": "web-artifact-forge",
      "render": "visual-pipeline-ops",
      "plan": "plan-reviewer"
    };
  }

  async connectWebSocket() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    const { WebSocket } = await import("ws");
    this.ws = new WebSocket(this.wsUrl);
    this.ws.on("message", (raw) => {
      try {
        const msg = JSON.parse(raw.toString());
        if (msg.type === "npc_think_result" && msg.id) {
          const handler = this._pending[msg.id];
          if (handler) { clearTimeout(handler.timer); delete this._pending[msg.id]; handler.resolve(msg); }
        }
      } catch { /* ignore */ }
    });
    return new Promise((resolve) => this.ws.on("open", resolve));
  }

  async think(npcState) {
    const domain = this.domainMap[npcState.intent] || "universal-architect";
    const complexity = npcState.complexity || 0;

    // Tier 1: Simple decisions → direct world server (no LLM)
    if (complexity < 2 && npcState.intent === "idle") {
      return { action: "patrol", reason: "low complexity, direct world rule", tier: 1 };
    }

    // Tier 2: Medium complexity → OpenCode ACP bridge
    if (complexity < 5) {
      try {
        const prompt = `NPC ${npcState.id} durumu: ${JSON.stringify(npcState)}
Intent: ${npcState.intent}
Son karar: ${npcState.lastDecision || "yok"}
Ne yapmalı? (tek cümle)`;
        const result = await this.bridge.runTask(domain, prompt, {
          timeout: 15000,
          sessionId: npcState.sessionId
        });
        return { ...result.payload, tier: 2, source: "opencode-acp" };
      } catch (e) {
        // Fall through to Tier 3
      }
    }

    // Tier 3: Complex → WebSocket to NEXUS MCP Server (which routes to LLM)
    try {
      await this.connectWebSocket();
      const id = ++this._id;
      const msg = JSON.stringify({ id, type: "npc_think", params: { npc_id: npcState.id, intent: npcState.intent, state: npcState } });
      const result = await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error("WS timeout")), 30000);
        this._pending[id] = { resolve, reject, timer };
        this.ws.send(msg);
      });
      return { ...result, tier: 3, source: "nexus-llm" };
    } catch (e) {
      return { action: "idle", reason: `all tiers failed: ${e.message}`, tier: 0, error: true };
    }
  }

  async close() {
    if (this.ws) this.ws.close();
    await this.bridge.close();
  }
}
