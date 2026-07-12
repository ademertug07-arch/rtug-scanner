import { spawn } from "child_process";
import { createInterface } from "readline";

export class OpenCodeACPBridge {
  constructor(opts = {}) {
    this.proc = spawn("opencode", ["acp", ...(opts.config ? ["--config", opts.config] : [])], {
      stdio: ["pipe", "pipe", "pipe"]
    });
    this.rl = createInterface({ input: this.proc.stdout });
    this._pending = {};
    this._id = 0;

    this.rl.on("line", (line) => {
      try {
        const msg = JSON.parse(line);
        const handler = this._pending[msg.id];
        if (handler) {
          clearTimeout(handler.timer);
          delete this._pending[msg.id];
          handler.resolve(msg);
        }
      } catch { /* ignore malformed */ }
    });

    this.proc.on("exit", (code) => {
      Object.values(this._pending).forEach((p) => p.reject(new Error(`ACP kapandi (kod: ${code})`)));
      this._pending = {};
    });
  }

  async runTask(agent, prompt, opts = {}) {
    const id = ++this._id;
    const timeout = opts.timeout || 60000;
    const msg = JSON.stringify({ id, type: "task", agent, prompt, session_id: opts.sessionId }) + "\n";

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        delete this._pending[id];
        reject(new Error(`ACP timeout: ${agent} ${timeout}ms`));
      }, timeout);
      this._pending[id] = { resolve, reject, timer };
      this.proc.stdin.write(msg);
    });
  }

  async close() {
    this.proc.stdin.end();
    return new Promise((resolve) => this.proc.on("exit", resolve));
  }
}
