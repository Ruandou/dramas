#!/usr/bin/env node
/**
 * MiniMax 海螺AI - Cursor MCP（stdio）
 * 支持文生图、语音合成
 */
import { spawn } from "node:child_process";
import { mkdir, stat } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { createWriteStream } from "node:fs";
import { pipeline } from "node:stream/promises";
import { Readable } from "node:stream";
import { fileURLToPath } from "node:url";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON = process.env.MINIMAX_PYTHON || "python3";
const MINIMAX_SCRIPT = path.join(__dirname, "scripts", "minimax.py");

function resolveProjectRoot() {
  if (process.env.MINIMAX_PROJECT_ROOT) {
    return path.resolve(process.env.MINIMAX_PROJECT_ROOT);
  }
  return path.join(__dirname, "..", "..");
}

function resolveDownloadDir() {
  if (process.env.MINIMAX_DOWNLOAD_DIR) {
    return path.resolve(process.env.MINIMAX_DOWNLOAD_DIR);
  }
  return path.join(resolveProjectRoot(), "video", "minimax");
}

function safeFilename(name) {
  const trimmed = String(name)
    .replace(/[/\\:*?"<>|\x00-\x1f]/g, "_")
    .trim();
  const base = trimmed || `minimax_${Date.now()}`;
  return base.toLowerCase().endsWith(".jpeg") || base.toLowerCase().endsWith(".mp3") || base.toLowerCase().endsWith(".wav")
    ? base
    : `${base}.jpeg`;
}

async function downloadToPath(url, destPath) {
  const res = await fetch(url, { redirect: "follow" });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${res.statusText}`);
  }
  if (!res.body) {
    throw new Error("响应无 body");
  }
  await mkdir(path.dirname(destPath), { recursive: true });
  await pipeline(Readable.fromWeb(res.body), createWriteStream(destPath));
}

function runPython(args) {
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, [MINIMAX_SCRIPT, ...args], {
      env: { ...process.env },
      stdio: ["pipe", "pipe", "pipe"],
    });
    let out = "";
    let err = "";
    child.stdout.on("data", (c) => (out += c.toString()));
    child.stderr.on("data", (c) => (err += c.toString()));
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0 && err) {
        reject(new Error(err || `exit ${code}`));
        return;
      }
      resolve(out.trim());
    });
  });
}

const server = new McpServer(
  { name: "minimax", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.registerTool(
  "minimax_docs",
  {
    title: "MiniMax 海螺AI 接入文档",
    description: "返回 MiniMax 海螺AI 接口文档链接和功能说明。",
    inputSchema: z.object({}),
  },
  async () => {
    const text = [
      "【MiniMax 海螺AI 官网】https://www.minimaxi.com",
      "【API文档】https://platform.minimaxi.com/docs",
      "",
      "【支持功能】",
      "  text_to_image - 文生图（image-01 模型）",
      "  text_to_audio - 语音合成（speech-02-hd 等模型）",
      "  list_voices - 列出可用音色",
      "",
      "【环境变量】",
      "  MINIMAX_API_KEY - API密钥",
      "  MINIMAX_API_HOST - API地址（默认 https://api.minimaxi.com）",
      "  MINIMAX_DOWNLOAD_DIR - 下载目录",
    ].join("\n");
    return { content: [{ type: "text", text }] };
  }
);

server.registerTool(
  "minimax_text_to_image",
  {
    title: "MiniMax 文生图",
    description: "根据文本描述生成图片，默认9:16竖屏比例。",
    inputSchema: z.object({
      prompt: z.string().describe("图片描述文本（建议使用英文）"),
      model: z.string().optional().describe("模型，默认 image-01"),
      aspect_ratio: z.string().optional().describe("宽高比，默认 9:16"),
      n: z.number().optional().describe("生成数量，默认 1"),
      prompt_optimizer: z.boolean().optional().describe("是否优化prompt，默认 false"),
      output_directory: z.string().optional().describe("输出目录，省略则只返回URL"),
    }),
  },
  async ({ prompt, model, aspect_ratio, n, prompt_optimizer, output_directory }) => {
    const args = ["image", "--prompt", prompt];
    if (model) args.push("--model", model);
    if (aspect_ratio) args.push("--ratio", aspect_ratio);
    else args.push("--ratio", "9:16"); // 默认9:16
    if (n) args.push("--n", String(n));
    if (prompt_optimizer === false || !prompt_optimizer) {
      args.push("--no-optimizer");
    }
    if (output_directory) args.push("--output", output_directory);

    const out = await runPython(args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "minimax_text_to_audio",
  {
    title: "MiniMax 语音合成",
    description: "将文本转换为语音，支持多种音色和模型。",
    inputSchema: z.object({
      text: z.string().describe("要合成的文本"),
      model: z.string().optional().describe("模型，默认 speech-02-hd"),
      voice_id: z.string().optional().describe("音色ID，默认 female-shaonv"),
      output_directory: z.string().optional().describe("输出目录，省略则只返回URL"),
    }),
  },
  async ({ text, model, voice_id, output_directory }) => {
    const args = ["audio", "--text", text];
    if (model) args.push("--model", model);
    if (voice_id) args.push("--voice", voice_id);
    if (output_directory) args.push("--output", output_directory);

    const out = await runPython(args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "minimax_list_voices",
  {
    title: "列出可用音色",
    description: "查询 MiniMax 海螺AI 所有可用的语音音色。",
    inputSchema: z.object({}),
  },
  async () => {
    const out = await runPython(["voices"]);
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
