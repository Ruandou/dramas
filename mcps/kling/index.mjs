#!/usr/bin/env node
/**
 * 可灵AI视频生成 — Cursor MCP（stdio）
 * 依赖：Node 18+、Python3
 */
import { spawn } from "node:child_process";
import { createWriteStream } from "node:fs";
import { mkdir, stat, unlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { pipeline } from "node:stream/promises";
import { Readable } from "node:stream";
import { fileURLToPath } from "node:url";
import path from "node:path";
import process from "node:process";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON = process.env.KLING_PYTHON || "python3";
const KLING_SCRIPT = path.join(__dirname, "scripts", "kling.py");

/** MCP 在 mcp/kling，向上两级为仓库根 */
function resolveProjectRoot() {
  if (process.env.KLING_PROJECT_ROOT) {
    return path.resolve(process.env.KLING_PROJECT_ROOT);
  }
  return path.join(__dirname, "..", "..");
}

/** 默认：仓库根下 video/kling */
function resolveDownloadDir() {
  if (process.env.KLING_DOWNLOAD_DIR) {
    return path.resolve(process.env.KLING_DOWNLOAD_DIR);
  }
  return path.join(resolveProjectRoot(), "video", "kling");
}

function resolveUserPath(p) {
  const s = String(p).trim();
  if (!s) {
    throw new Error("路径为空");
  }
  if (path.isAbsolute(s)) {
    return path.resolve(s);
  }
  return path.join(resolveProjectRoot(), s);
}

function safeVideoFilename(name) {
  const trimmed = String(name)
    .replace(/[/\\:*?"<>|\x00-\x1f]/g, "_")
    .trim();
  const base = trimmed || `kling_${Date.now()}`;
  return base.toLowerCase().endsWith(".mp4") ? base : `${base}.mp4`;
}

async function downloadVideoToPath(url, destPath) {
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

/** 调用 kling.py 子命令 */
function runKlingPy(args) {
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, [KLING_SCRIPT, ...args], {
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
  {
    name: "kling",
    version: "1.0.0",
  },
  {
    capabilities: { tools: {} },
  }
);

server.registerTool(
  "kling_docs",
  {
    title: "可灵AI接入文档链接",
    description: "返回可灵AI视频生成接口文档链接（不涉及密钥）。",
    inputSchema: z.object({}),
  },
  async () => {
    const text = [
      "【可灵AI官网】https://klingai.com",
      "【API文档】https://klingapi.com/zh/docs",
      "【API端点】",
      "  POST /v1/videos/text2video - 文生视频",
      "  POST /v1/videos/image2video - 图生视频",
      "  GET /v1/videos/{task_id} - 查询任务状态",
      "",
      "【支持模型】",
      "  kling-video-o1 - 统一多模态模型",
      "  kling-v3-omni - 3.0全能，原生音画同出",
      "  kling-v3 - 3.0基础版，支持多镜头",
      "  kling-v2.6-pro - 2.6专业版",
      "  kling-v2.6-std - 2.6标准版",
      "  kling-v2.5-turbo - 2.5快速版",
      "",
      "环境变量：",
      "  KLING_AK / KLING_SK - API密钥",
      "  KLING_PROJECT_ROOT - 仓库根目录",
      "  KLING_DOWNLOAD_DIR - 视频下载目录",
    ].join("\n");
    return { content: [{ type: "text", text }] };
  }
);

server.registerTool(
  "kling_auth",
  {
    title: "设置可灵AI API凭证",
    description: "保存 AK/SK 到 ~/.kling_credentials",
    inputSchema: z.object({
      ak: z.string().describe("Access Key"),
      sk: z.string().describe("Secret Key"),
    }),
  },
  async ({ ak, sk }) => {
    const out = await runKlingPy(["auth", ak, sk]);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_image_to_video",
  {
    title: "可灵AI图生视频",
    description: "将静态图片转化为动态视频，支持中英文配音和音效。支持多图主体（最多4张图）。返回 task_id 用于查询进度。",
    inputSchema: z.object({
      image_path: z.string().optional().describe("单张图片路径（相对仓库根或绝对路径）"),
      image_paths: z.string().optional().describe("多张图片路径，逗号分隔（注意：可灵API目前可能不支持多图）"),
      prompt: z.string().describe("视频描述，如角色动作、镜头运动等"),
      duration: z.union([z.literal(3), z.literal(5), z.literal(10), z.literal(15)]).optional().describe("视频时长（秒），默认5"),
      aspect_ratio: z.enum(["16:9", "9:16", "1:1"]).optional().describe("宽高比，默认9:16"),
      audio_prompt: z.string().optional().describe("音频描述，用于生成配音/音效/背景音乐"),
      model: z.enum(["kling-video-o1", "kling-v3-omni", "kling-v3", "kling-v2.6-pro", "kling-v2.6-std", "kling-v2.5-turbo"]).optional().describe("模型版本，默认kling-v3-omni"),
    }),
  },
  async ({ image_path, image_paths, prompt, duration, aspect_ratio, audio_prompt, model }) => {
    const args = ["image2video"];
    if (image_paths) {
      args.push("--image-paths", image_paths);
    } else if (image_path) {
      args.push("--image", image_path);
    }
    args.push("--prompt", prompt);
    if (duration) args.push("--duration", String(duration));
    if (aspect_ratio) args.push("--ratio", aspect_ratio);
    if (audio_prompt) args.push("--audio", audio_prompt);
    if (model) args.push("--model", model);
    const out = await runKlingPy(args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_text_to_video",
  {
    title: "可灵AI文生视频",
    description: "将文本描述转化为视频，支持中英文配音和音效。",
    inputSchema: z.object({
      prompt: z.string().describe("视频内容描述"),
      duration: z.union([z.literal(3), z.literal(5), z.literal(10), z.literal(15)]).optional().describe("视频时长（秒），默认5"),
      aspect_ratio: z.enum(["16:9", "9:16", "1:1"]).optional().describe("宽高比，默认9:16"),
      audio_prompt: z.string().optional().describe("音频描述"),
      model: z.enum(["kling-video-o1", "kling-v3-omni", "kling-v3", "kling-v2.6-pro", "kling-v2.6-std", "kling-v2.5-turbo"]).optional().describe("模型版本，默认kling-v3-omni"),
    }),
  },
  async ({ prompt, duration, aspect_ratio, audio_prompt, model }) => {
    const args = ["text2video", "--prompt", prompt];
    if (duration) args.push("--duration", String(duration));
    if (aspect_ratio) args.push("--ratio", aspect_ratio);
    if (audio_prompt) args.push("--audio", audio_prompt);
    if (model) args.push("--model", model);
    const out = await runKlingPy(args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_omni_video",
  {
    title: "可灵AI Omni多图视频",
    description: "使用Omni模型生成多图视频，支持多图主体控制。可用本地图片路径或URL。prompt中图片引用格式：<<<image_1>>>, <<<image_2>>>, ...",
    inputSchema: z.object({
      image_paths: z.string().describe("图片路径或URL，逗号分隔（最多4张）"),
      prompt: z.string().describe("视频描述，图片引用格式：<<<image_1>>>, <<<image_2>>>, ..."),
      duration: z.union([z.literal(3), z.literal(5), z.literal(10), z.literal(15)]).optional().describe("视频时长（秒），默认5"),
      aspect_ratio: z.enum(["16:9", "9:16", "1:1"]).optional().describe("宽高比，默认9:16"),
      model: z.enum(["kling-video-o1", "kling-v3-omni"]).optional().describe("模型版本，默认kling-v3-omni（支持音频）"),
    }),
  },
  async ({ image_paths, prompt, duration, aspect_ratio, model }) => {
    const args = ["omni", "--paths", image_paths, "--prompt", prompt];
    if (duration) args.push("--duration", String(duration));
    if (aspect_ratio) args.push("--ratio", aspect_ratio);
    if (model) args.push("--model", model);
    const out = await runKlingPy(args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_query_task",
  {
    title: "查询可灵AI任务状态",
    description: "使用 task_id 查询视频生成进度，完成后返回下载链接。",
    inputSchema: z.object({
      task_id: z.string().describe("提交任务时返回的 task_id"),
    }),
  },
  async ({ task_id }) => {
    const out = await runKlingPy(["query", "--task-id", task_id]);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_wait_task",
  {
    title: "等待可灵AI任务完成",
    description: "轮询等待任务完成，默认最多等待300秒。",
    inputSchema: z.object({
      task_id: z.string().describe("任务ID"),
      max_wait: z.number().optional().describe("最大等待秒数，默认300"),
    }),
  },
  async ({ task_id, max_wait }) => {
    const args = ["wait", "--task-id", task_id];
    if (max_wait) args.push("--max", String(max_wait));
    const out = await runKlingPy(args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_download_video",
  {
    title: "下载视频到本地",
    description: "将可灵返回的 video_url 直链保存为 MP4。",
    inputSchema: z.object({
      url: z.string().url().describe("视频 HTTPS 直链"),
      filename: z.string().optional().describe("保存文件名，省略则自动生成"),
    }),
  },
  async ({ url, filename }) => {
    const dir = resolveDownloadDir();
    const name = filename
      ? safeVideoFilename(filename)
      : safeVideoFilename(`kling_${new Date().toISOString().replace(/[:.]/g, "-")}`);
    const destPath = path.join(dir, name);
    await downloadVideoToPath(url, destPath);
    const st = await stat(destPath);
    const text = JSON.stringify(
      {
        savedPath: destPath,
        filename: name,
        bytes: st.size,
      },
      null,
      2
    );
    return { content: [{ type: "text", text }] };
  }
);

server.registerTool(
  "kling_list_tasks",
  {
    title: "列出归档的任务",
    description: "列出本地归档的可灵AI任务记录。",
    inputSchema: z.object({
      limit: z.number().optional().describe("显示条数，默认20"),
    }),
  },
  async ({ limit }) => {
    const args = ["list", "--limit", String(limit || 20)];
    const out = await runKlingPy(args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_download",
  {
    title: "下载可灵视频",
    description: "下载可灵生成的视频到本地。先用kling_query_task拿到URL后，再调用此工具。",
    inputSchema: z.object({
      url: z.string().describe("视频URL（从query_task返回的）"),
      output_path: z.string().describe("输出文件路径"),
    }),
  },
  async ({ url, output_path }) => {
    const args = ["download", "--url", url, "--output", output_path];
    const out = await runKlingPy(args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_imgbb_upload",
  {
    title: "上传图片到imgbb",
    description: "上传本地图片到imgbb免费图床，返回公开URL。用于可灵视频生成的图片上传。",
    inputSchema: z.object({
      file_path: z.string().describe("本地图片文件路径"),
    }),
  },
  async ({ file_path }) => {
    const args = ["imgbb", file_path];
    const out = await runKlingPy(args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_omni_image",
  {
    title: "可灵AI OmniImage图片生成",
    description: "使用OmniImage模型生成图片，支持参考图。有参考图时prompt只描述变化差异部分。",
    inputSchema: z.object({
      prompt: z.string().describe("图片描述文本（中英文均可）"),
      image_paths: z.string().optional().describe("参考图片路径，逗号分隔（最多支持多张）"),
      resolution: z.enum(["1k", "2k", "4k"]).optional().describe("分辨率，默认2k"),
      aspect_ratio: z.enum(["16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9", "auto"]).optional().describe("宽高比，默认9:16"),
      n: z.number().optional().describe("生成数量，1-9，默认1"),
      model: z.enum(["kling-image-o1", "kling-v3-omni"]).optional().describe("模型，默认kling-v3-omni"),
    }),
  },
  async ({ prompt, image_paths, resolution, aspect_ratio, n, model }) => {
    const args = ["omni_image", "--prompt", prompt];
    if (image_paths) args.push("--paths", image_paths);
    if (resolution) args.push("--resolution", resolution);
    if (aspect_ratio) args.push("--ratio", aspect_ratio);
    if (n) args.push("--n", String(n));
    if (model) args.push("--model", model);
    const out = await runKlingPy(args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_query_image_task",
  {
    title: "查询可灵AI图片任务状态",
    description: "使用 task_id 查询图片生成进度，完成后返回图片URL列表。",
    inputSchema: z.object({
      task_id: z.string().describe("提交任务时返回的 task_id"),
    }),
  },
  async ({ task_id }) => {
    const out = await runKlingPy(["query_image", "--task-id", task_id]);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_wait_image_task",
  {
    title: "等待可灵AI图片任务完成",
    description: "轮询等待图片生成任务完成，完成后自动下载到本地。",
    inputSchema: z.object({
      task_id: z.string().describe("提交任务时返回的 task_id"),
      output_path: z.string().optional().describe("输出文件路径（省略则只返回URL）"),
      max_wait: z.number().optional().describe("最大等待秒数，默认300"),
    }),
  },
  async ({ task_id, output_path, max_wait }) => {
    const args = ["wait_image", "--task-id", task_id];
    if (max_wait) args.push("--max", String(max_wait));
    const out = await runKlingPy(args);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "kling_download_image",
  {
    title: "下载可灵AI生成的图片",
    description: "下载图片到本地，并归档任务。",
    inputSchema: z.object({
      url: z.string().describe("图片URL（从query_image_task返回的）"),
      output_path: z.string().describe("输出文件路径"),
      task_id: z.string().optional().describe("任务ID（用于归档）"),
    }),
  },
  async ({ url, output_path, task_id }) => {
    const args = ["download_image", "--url", url, "--output", output_path];
    if (task_id) args.push("--task-id", task_id);
    const out = await runKlingPy(args);
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
