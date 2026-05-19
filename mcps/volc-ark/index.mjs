#!/usr/bin/env node
/**
 * 火山方舟 MCP（volc-ark）：Seedream 图片 + Seedance 视频
 * 独立于 volc-jimeng；鉴权均为 ARK_API_KEY（Bearer）
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
  process.env.VOLC_ARK_PYTHON || process.env.ARK_PYTHON || "python3";
const SCRIPTS = path.join(__dirname, "scripts");
const IMAGE_CLI = path.join(SCRIPTS, "ark_seedream_image.py");
const VIDEO_CLI = path.join(SCRIPTS, "ark_seedance_video.py");
const ARCHIVE_CLI = path.join(SCRIPTS, "ark_archive.py");

function resolveProjectRoot() {
  const root =
    process.env.ARK_PROJECT_ROOT ||
    process.env.ARK_SEEDREAM_PROJECT_ROOT ||
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

function runCli(scriptPath, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, [scriptPath, ...args], {
      env: { ...process.env, PYTHONPATH: SCRIPTS },
      cwd: SCRIPTS,
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
  { name: "volc-ark", version: "1.2.0" },
  { capabilities: { tools: {} } }
);

// --- Seedream 图片 ---

server.registerTool(
  "ark_seedream_docs",
  {
    title: "Seedream 5.0 lite 文档",
    description: "图片生成文档与默认配置。",
    inputSchema: z.object({}),
  },
  async () => {
    const out = await runCli(IMAGE_CLI, ["docs"]);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "ark_seedream_generate",
  {
    title: "Seedream 5.0 lite 文生图",
    description:
      "POST /api/v3/responses。需 ARK_API_KEY。会扣费，仅用户明确要求时调用。",
    inputSchema: z.object({
      prompt: z.string(),
      output_path: z.string().optional(),
      ratio: z.string().optional(),
      size: z.string().optional(),
      model: z.string().optional(),
      image_urls: z.array(z.string()).optional(),
      web_search: z.boolean().optional(),
      watermark: z.boolean().optional(),
      dry_run: z.boolean().optional(),
      project_root: z.string().optional().describe("本地参考图相对路径的根目录"),
    }),
  },
  async (p) => {
    const args = ["generate", "--prompt", p.prompt];
    if (p.output_path) args.push("--output", resolveUserPath(p.output_path));
    if (p.ratio) args.push("--ratio", p.ratio);
    if (p.size) args.push("--size", p.size);
    if (p.model) args.push("--model", p.model);
    for (const u of p.image_urls || []) args.push("--image-url", u);
    if (p.web_search) args.push("--web-search");
    if (p.watermark) args.push("--watermark");
    if (p.dry_run) args.push("--dry-run");
    if (p.project_root) args.push("--project-root", resolveUserPath(p.project_root));
    const out = await runCli(IMAGE_CLI, args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "ark_seedream_batch",
  {
    title: "seedream_batch.yaml 批量出图",
    description: "读定妆/场景 batch YAML。会扣费。",
    inputSchema: z.object({
      yaml_path: z.string(),
      project_root: z.string().optional(),
      ids: z.string().optional(),
      force: z.boolean().optional(),
      dry_run: z.boolean().optional(),
      delay_sec: z.number().optional(),
    }),
  },
  async (p) => {
    const args = ["batch", "--yaml", resolveUserPath(p.yaml_path)];
    if (p.project_root) args.push("--project-root", resolveUserPath(p.project_root));
    if (p.ids) args.push("--ids", p.ids);
    if (p.force) args.push("--force");
    if (p.dry_run) args.push("--dry-run");
    if (p.delay_sec != null) args.push("--delay", String(p.delay_sec));
    const out = await runCli(IMAGE_CLI, args);
    return { content: [{ type: "text", text: out }] };
  }
);

// --- Seedance 视频 ---

server.registerTool(
  "ark_seedance_docs",
  {
    title: "Seedance 2.0 文档",
    description: "视频生成教程、API 与环境变量说明。",
    inputSchema: z.object({}),
  },
  async () => {
    const out = await runCli(VIDEO_CLI, ["docs"]);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "ark_seedance_create",
  {
    title: "创建 Seedance 视频任务",
    description:
      "POST /api/v3/contents/generations/tasks。content[] 多模态。会扣费。",
    inputSchema: z.object({
      text: z.string().optional().describe("提示词（与 body_json_path 二选一）"),
      body_json_path: z
        .string()
        .optional()
        .describe("完整请求体 JSON 文件路径"),
      image_urls: z
        .array(z.string())
        .optional()
        .describe("参考图 URL，可写 url:role"),
      model: z.string().optional(),
      ratio: z.string().optional(),
      resolution: z.string().optional(),
      duration: z.number().optional(),
      generate_audio: z.boolean().optional(),
      watermark: z.boolean().optional(),
      return_last_frame: z.boolean().optional(),
      dry_run: z.boolean().optional(),
      project_root: z.string().optional(),
    }),
  },
  async (p) => {
    const args = ["create"];
    if (p.body_json_path) args.push("--body-json", resolveUserPath(p.body_json_path));
    if (p.text) args.push("--text", p.text);
    for (const u of p.image_urls || []) args.push("--image-url", u);
    if (p.model) args.push("--model", p.model);
    if (p.ratio) args.push("--ratio", p.ratio);
    if (p.resolution) args.push("--resolution", p.resolution);
    if (p.duration != null) args.push("--duration", String(p.duration));
    if (p.generate_audio) args.push("--generate-audio");
    if (p.watermark) args.push("--watermark");
    if (p.return_last_frame) args.push("--return-last-frame");
    if (p.dry_run) args.push("--dry-run");
    if (p.project_root) args.push("--project-root", resolveUserPath(p.project_root));
    const out = await runCli(VIDEO_CLI, args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "ark_seedance_get",
  {
    title: "查询 Seedance 任务",
    description: "GET …/contents/generations/tasks/{task_id}，并更新本地归档",
    inputSchema: z.object({ task_id: z.string() }),
  },
  async ({ task_id }) => {
    const out = await runCli(VIDEO_CLI, ["get", "--task-id", task_id]);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "ark_list_tasks",
  {
    title: "本地任务归档（volc-ark）",
    description:
      "读取 video/ark_tasks/tasks_image.json 与 tasks_video.json，与 volc-jimeng 的 jimeng_tasks 同级。",
    inputSchema: z.object({
      type: z.enum(["image", "video", "all"]).optional(),
      limit: z.number().optional(),
    }),
  },
  async (p) => {
    const args = ["list"];
    if (p.type && p.type !== "all") args.push("--type", p.type);
    if (p.limit != null) args.push("--limit", String(p.limit));
    const out = await runCli(ARCHIVE_CLI, args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "ark_seedance_list",
  {
    title: "列出 Seedance 任务",
    description: "GET …/contents/generations/tasks（近约 7 天）",
    inputSchema: z.object({
      status: z.string().optional(),
      model: z.string().optional(),
      page_size: z.number().optional(),
      max_pages: z.number().optional(),
    }),
  },
  async (p) => {
    const args = ["list", "--json"];
    if (p.status) args.push("--status", p.status);
    if (p.model) args.push("--model", p.model);
    if (p.page_size != null) args.push("--page-size", String(p.page_size));
    if (p.max_pages != null) args.push("--max-pages", String(p.max_pages));
    const out = await runCli(VIDEO_CLI, args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "ark_seedance_wait",
  {
    title: "轮询 Seedance 任务至完成",
    description: "直到 succeeded / failed / expired",
    inputSchema: z.object({
      task_id: z.string(),
      max_wait_sec: z.number().optional(),
      poll_interval_sec: z.number().optional(),
    }),
  },
  async (p) => {
    const args = ["wait", "--task-id", p.task_id];
    if (p.max_wait_sec != null) args.push("--max-wait", String(p.max_wait_sec));
    if (p.poll_interval_sec != null) args.push("--interval", String(p.poll_interval_sec));
    const out = await runCli(VIDEO_CLI, args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "ark_seedance_download",
  {
    title: "下载 Seedance 成片",
    description: "按 task_id 或直链下载 MP4（URL 约 24h 有效）",
    inputSchema: z.object({
      task_id: z.string().optional(),
      url: z.string().optional(),
      output_path: z.string().describe("保存路径 .mp4"),
    }),
  },
  async (p) => {
    const args = ["download", "--output", resolveUserPath(p.output_path)];
    if (p.task_id) args.push("--task-id", p.task_id);
    if (p.url) args.push("--url", p.url);
    const out = await runCli(VIDEO_CLI, args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "ark_seedance_shots",
  {
    title: "从 shots.yaml 提交分镜视频",
    description:
      "读取 EP##_shots.yaml，本地 assets 自动 base64 提交。会扣费。",
    inputSchema: z.object({
      episode: z.string().describe("如 EP01"),
      project_root: z.string().describe("短剧根目录，如 darams/天工开物"),
      cdn_base: z.string().optional().describe("（已废弃，忽略）"),
      shot_id: z.string().optional(),
      check_only: z.boolean().optional(),
      dry_run: z.boolean().optional(),
      output_log_dir: z
        .string()
        .optional()
        .describe("写入 task_log.jsonl，如 assets/generated/EP01"),
    }),
  },
  async (p) => {
    const args = [
      "shots",
      p.episode.toUpperCase(),
      "--project-root",
      resolveUserPath(p.project_root),
    ];
    if (p.cdn_base) args.push("--cdn-base", p.cdn_base);
    if (p.shot_id) args.push("--shot", p.shot_id);
    if (p.check_only) args.push("--check-only");
    if (p.dry_run) args.push("--dry-run");
    if (p.output_log_dir) args.push("--output-dir", resolveUserPath(p.output_log_dir));
    const out = await runCli(VIDEO_CLI, args);
    return { content: [{ type: "text", text: out }] };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
