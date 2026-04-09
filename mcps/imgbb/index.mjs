#!/usr/bin/env node
/**
 * imgbb图片上传 — Cursor MCP（stdio）
 */
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";
import process from "node:process";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON = process.env.IMGBB_PYTHON || "python3";
const IMGBB_SCRIPT = path.join(__dirname, "scripts", "imgbb.py");

function runImgbbPy(args) {
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, [IMGBB_SCRIPT, ...args], {
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
  { name: "imgbb", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.registerTool(
  "imgbb_upload",
  {
    title: "上传图片到imgbb",
    description: "上传本地图片到imgbb免费图床，返回公开URL。",
    inputSchema: z.object({
      file_path: z.string().describe("本地图片文件路径"),
    }),
  },
  async ({ file_path }) => {
    const out = await runImgbbPy(["upload", file_path]);
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
