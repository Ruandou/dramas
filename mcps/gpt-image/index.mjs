#!/usr/bin/env node
/**
 * gpt-image MCP（gpt-image）：OpenAI 兼容中转 gpt-image-2 文生图/图生图
 * 独立于 volc-ark；鉴权为 GPT_IMAGE_API_KEY（Bearer，兼容回退 OPENAI_API_KEY）
 */
import { spawn } from "node:child_process";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON =
  process.env.GPT_IMAGE_PYTHON || process.env.ARK_PYTHON || "python3";
const SCRIPTS = path.join(__dirname, "scripts");
const SHARED = path.join(__dirname, "..", "shared");
const IMAGE_CLI = path.join(SCRIPTS, "gpt_image.py");

function resolveProjectRoot() {
  const root =
    process.env.DRAMA_PROJECT_ROOT ||
    process.env.GPT_IMAGE_PROJECT_ROOT ||
    process.env.ARK_PROJECT_ROOT ||
    "";
  if (root) {
    return path.resolve(root);
  }
  return path.join(__dirname, "..", "..");
}

function resolveUserPath(p) {
  const s = String(p).trim();
  if (!s) return resolveProjectRoot();
  return path.isAbsolute(s) ? path.resolve(s) : path.join(resolveProjectRoot(), s);
}

function runCli(scriptPath, args, options = {}) {
  const { cwd = SCRIPTS, envExtra = {} } = options;
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, [scriptPath, ...args], {
      env: {
        ...process.env,
        PYTHONPATH: `${SCRIPTS}:${SHARED}`,
        ...envExtra,
      },
      cwd,
      stdio: ["pipe", "pipe", "pipe"],
    });
    let out = "";
    let err = "";
    child.stdout.on("data", (c) => (out += c.toString()));
    child.stderr.on("data", (c) => (err += c.toString()));
    child.on("error", reject);
    child.on("close", (code) => {
      const combined = [out.trim(), err.trim()].filter(Boolean).join("\n");
      if (code !== 0) {
        reject(new Error(combined || `exit ${code}`));
        return;
      }
      resolve(combined || "{}");
    });
  });
}

const server = new McpServer(
  { name: "gpt-image", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// --- gpt-image 图片 ---

server.registerTool(
  "gpt_image_docs",
  {
    title: "gpt-image-2 文档",
    description: "图片生成文档、默认配置与环境变量说明。",
    inputSchema: z.object({}),
  },
  async () => {
    const out = await runCli(IMAGE_CLI, ["docs"]);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "gpt_image_generate",
  {
    title: "gpt-image-2 文生图/图生图",
    description:
      "POST {base}/v1/images/generations。需 GPT_IMAGE_API_KEY。会扣费，仅用户明确要求时调用。",
    inputSchema: z.object({
      prompt: z.string(),
      output_path: z.string().optional(),
      ratio: z.string().optional().describe("9:16 / 16:9 / 1:1 / 4:3 / 3:4"),
      size: z.string().optional().describe("如 1024x1536 / 2160x3840 / 2k / 4k"),
      tier: z.string().optional().describe("standard / 2k / 4k"),
      quality: z.string().optional().describe("low / medium / high / auto"),
      model: z.string().optional(),
      image_urls: z
        .array(z.string())
        .optional()
        .describe("参考图 URL/本地路径，≤16 张"),
      index: z.number().optional().describe("组图时取第几张，默认 0"),
      dry_run: z.boolean().optional(),
      force: z.boolean().optional().describe("忽略去重强制重出（需 ARK_ALLOW_FORCE=1）"),
      project_root: z.string().optional().describe("本地参考图相对路径的根目录"),
    }),
  },
  async (p) => {
    const args = ["generate", "--prompt", p.prompt];
    if (p.output_path) args.push("--output", resolveUserPath(p.output_path));
    if (p.ratio) args.push("--ratio", p.ratio);
    if (p.size) args.push("--size", p.size);
    if (p.tier) args.push("--tier", p.tier);
    if (p.quality) args.push("--quality", p.quality);
    if (p.model) args.push("--model", p.model);
    for (const u of p.image_urls || []) args.push("--image-url", u);
    if (p.index != null) args.push("--index", String(p.index));
    if (p.dry_run) args.push("--dry-run");
    if (p.force) args.push("--force");
    if (p.project_root) args.push("--project-root", resolveUserPath(p.project_root));
    const out = await runCli(IMAGE_CLI, args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "gpt_image_batch",
  {
    title: "gpt_image_batch.yaml 批量出图",
    description: "读定妆/场景 batch YAML。会扣费。",
    inputSchema: z.object({
      yaml_path: z.string(),
      project_root: z.string().optional(),
      ids: z.string().optional(),
      model: z.string().optional(),
      size: z.string().optional(),
      ratio: z.string().optional(),
      tier: z.string().optional(),
      quality: z.string().optional(),
      force: z.boolean().optional(),
      dry_run: z.boolean().optional(),
      pending: z.boolean().optional().describe("只生成未生成的（增量）"),
      status: z.boolean().optional().describe("只打印每项状态不生成"),
      delay_sec: z.number().optional(),
    }),
  },
  async (p) => {
    const args = ["batch", "--yaml", resolveUserPath(p.yaml_path)];
    if (p.project_root) args.push("--project-root", resolveUserPath(p.project_root));
    if (p.ids) args.push("--ids", p.ids);
    if (p.model) args.push("--model", p.model);
    if (p.size) args.push("--size", p.size);
    if (p.ratio) args.push("--ratio", p.ratio);
    if (p.tier) args.push("--tier", p.tier);
    if (p.quality) args.push("--quality", p.quality);
    if (p.force) args.push("--force");
    if (p.dry_run) args.push("--dry-run");
    if (p.pending) args.push("--pending");
    if (p.status) args.push("--status");
    if (p.delay_sec != null) args.push("--delay", String(p.delay_sec));
    const out = await runCli(IMAGE_CLI, args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "gpt_image_reconcile",
  {
    title: "gpt-image 本地归档对账",
    description:
      "图片本地归档与 output 文件对账（gpt-image 无远程历史 API）。不扣费。",
    inputSchema: z.object({
      yaml_path: z.string().optional().describe("gpt_image_batch.yaml，用于算指纹比对"),
      project_root: z.string().optional(),
    }),
  },
  async (p) => {
    const args = ["reconcile"];
    if (p.yaml_path) args.push("--yaml", resolveUserPath(p.yaml_path));
    if (p.project_root) args.push("--project-root", resolveUserPath(p.project_root));
    const out = await runCli(IMAGE_CLI, args);
    return { content: [{ type: "text", text: out }] };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
