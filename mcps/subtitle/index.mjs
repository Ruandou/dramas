#!/usr/bin/env node
/**
 * 字幕生成MCP - 使用faster-whisper将视频转SRT字幕
 */
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";
import process from "node:process";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON = process.env.SUBTITLE_PYTHON || "python3";
const SUBTITLE_SCRIPT = path.join(__dirname, "scripts", "subtitle.py");

function runSubtitlePy(args) {
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, [SUBTITLE_SCRIPT, ...args], {
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
  { name: "subtitle", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.registerTool(
  "video_to_srt",
  {
    title: "视频转SRT字幕",
    description: "使用faster-whisper将视频文件的音频转成SRT字幕文件。需要先安装faster-whisper和ffmpeg。",
    inputSchema: z.object({
      video_path: z.string().describe("视频文件路径"),
      output_srt: z.string().optional().describe("输出SRT路径，默认与视频同目录"),
      language: z.string().optional().describe("语言，默认zh（中文）"),
    }),
  },
  async ({ video_path, output_srt, language }) => {
    const args = ["video2srt", video_path];
    if (output_srt) args.push("--output", output_srt);
    if (language) args.push("--lang", language);
    const out = await runSubtitlePy(args);
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
