# Top MCP Servers

Mevcut yapılandırılmış MCP'ler: Playwright, Puppeteer, Chrome DevTools, Docker, n8n, Filesystem, Git, Brave Search, Obsidian, PostgreSQL, Sequential Thinking

## Popüler MCP Kurulum Komutları

```bash
# GitHub
claude mcp add --transport http github https://api.githubcopilot.com/mcp/

# Supabase
claude mcp add --transport stdio supabase --env SUPABASE_ACCESS_TOKEN=YOUR_TOKEN -- npx -y @supabase/mcp-server-supabase

# Stripe
claude mcp add --transport http stripe https://mcp.stripe.com

# Sentry
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# Figma
claude mcp add --transport http figma https://mcp.figma.com/mcp

# Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Cloudflare
claude mcp add --transport http cloudflare https://mcp.cloudflare.com/mcp

# Vercel
claude mcp add --transport http vercel https://mcp.vercel.com/

# Linear
claude mcp add --transport http linear https://mcp.linear.app/mcp

# Playwright (browser automation)
claude mcp add --transport stdio playwright -- npx @playwright/mcp@latest
```

Tam liste (1,076 server): github.com/punkpeye/awesome-mcp-servers
Kaynak: awesomeclaude.ai/top-mcp-servers
