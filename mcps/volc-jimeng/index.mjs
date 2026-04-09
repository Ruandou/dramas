#!/usr/bin/env node
/**
 * 火山引擎即梦 / 视觉 API — Cursor MCP（stdio）
 * 依赖：Node 18+、Python3 + volcengine 旧版 SDK（见 README）
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
const PYTHON = process.env.VOLC_PYTHON || "python3";
const SUBMIT_SCRIPT = path.join(__dirname, "scripts", "volc_visual_submit.py");

/** MCP 在 mcp/volc-jimeng，向上两级为仓库根 */
function resolveProjectRoot() {
  if (process.env.VOLC_PROJECT_ROOT) {
    return path.resolve(process.env.VOLC_PROJECT_ROOT);
  }
  return path.join(__dirname, "..", "..");
}

/** 默认：仓库根下 video/generated（MCP 位于 mcp/volc-jimeng） */
function resolveDownloadDir() {
  if (process.env.VOLC_DOWNLOAD_DIR) {
    return path.resolve(process.env.VOLC_DOWNLOAD_DIR);
  }
  return path.join(resolveProjectRoot(), "video", "generated");
}

/** 拼接输出目录，默认 video/output */
function resolveMergeOutputDir() {
  if (process.env.VOLC_MERGE_OUTPUT_DIR) {
    return path.resolve(process.env.VOLC_MERGE_OUTPUT_DIR);
  }
  return path.join(resolveProjectRoot(), "video", "output");
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

/** concat demuxer 单行：file '...'，路径中单引号需转义 */
function concatFileLine(absPath) {
  const escaped = absPath.replace(/'/g, "'\\''");
  return `file '${escaped}'`;
}

function runFfmpeg(args) {
  const bin = process.env.FFMPEG_PATH || "ffmpeg";
  return new Promise((resolve, reject) => {
    const child = spawn(bin, args, {
      stdio: ["ignore", "pipe", "pipe"],
    });
    let err = "";
    child.stderr.on("data", (c) => {
      err += c.toString();
    });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(err.trim() || `ffmpeg 退出码 ${code}`));
        return;
      }
      resolve();
    });
  });
}

/** 调用 video/automation/local_pipeline.py（stdout+stderr 合并返回） */
function runLocalPipelinePy(configAbsPath) {
  const root = resolveProjectRoot();
  const script = path.join(root, "video", "automation", "local_pipeline.py");
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, [script, "--config", configAbsPath], {
      cwd: root,
      env: { ...process.env },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let out = "";
    let err = "";
    child.stdout.on("data", (c) => {
      out += c.toString();
    });
    child.stderr.on("data", (c) => {
      err += c.toString();
    });
    child.on("error", reject);
    child.on("close", (code) => {
      const combined = [out.trim(), err.trim()].filter(Boolean).join("\n--- stderr ---\n");
      if (code !== 0) {
        reject(new Error(combined || `local_pipeline 退出码 ${code}`));
        return;
      }
      resolve(combined || "(完成)");
    });
  });
}

function runTtsBatchPy(linesAbs, outDirAbs, voice) {
  const root = resolveProjectRoot();
  const script = path.join(root, "video", "automation", "tts_batch_edge.py");
  return new Promise((resolve, reject) => {
    const child = spawn(
      PYTHON,
      [
        script,
        "--lines",
        linesAbs,
        "--out-dir",
        outDirAbs,
        "--voice",
        voice || "zh-CN-XiaoxiaoNeural",
      ],
      {
        cwd: root,
        env: { ...process.env },
        stdio: ["ignore", "pipe", "pipe"],
      }
    );
    let out = "";
    let err = "";
    child.stdout.on("data", (c) => {
      out += c.toString();
    });
    child.stderr.on("data", (c) => {
      err += c.toString();
    });
    child.on("error", reject);
    child.on("close", (code) => {
      const combined = [out.trim(), err.trim()].filter(Boolean).join("\n--- stderr ---\n");
      if (code !== 0) {
        reject(new Error(combined || `tts_batch_edge 退出码 ${code}`));
        return;
      }
      resolve(combined || "(完成)");
    });
  });
}

function runMixTtsSrtPy(
  videoAbs,
  srtAbs,
  ttsDirAbs,
  outputAbs,
  originalVolume,
  dryRun
) {
  const root = resolveProjectRoot();
  const script = path.join(root, "video", "automation", "mix_tts_from_srt.py");
  const argv = [
    script,
    "--video",
    videoAbs,
    "--srt",
    srtAbs,
    "--tts-dir",
    ttsDirAbs,
    "--output",
    outputAbs,
  ];
  if (originalVolume != null && originalVolume !== "") {
    argv.push("--original-volume", String(originalVolume));
  }
  if (dryRun) {
    argv.push("--dry-run");
  }
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, argv, {
      cwd: root,
      env: { ...process.env },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let out = "";
    let err = "";
    child.stdout.on("data", (c) => {
      out += c.toString();
    });
    child.stderr.on("data", (c) => {
      err += c.toString();
    });
    child.on("error", reject);
    child.on("close", (code) => {
      const combined = [out.trim(), err.trim()].filter(Boolean).join("\n--- stderr ---\n");
      if (code !== 0) {
        reject(new Error(combined || `mix_tts_from_srt 退出码 ${code}`));
        return;
      }
      resolve(combined || "(完成)");
    });
  });
}

/** 仅去掉路径非法字符，保留中文；无扩展名则补 .mp4 */
function safeVideoFilename(name) {
  const trimmed = String(name)
    .replace(/[/\\:*?"<>|\x00-\x1f]/g, "_")
    .trim();
  const base = trimmed || `jimeng_${Date.now()}`;
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

function runPython(stdinJson) {
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, [SUBMIT_SCRIPT], {
      env: {
        ...process.env,
        // 避免 urllib OpenSSL 警告混入 stderr，干扰 MCP 对返回内容的解析
        PYTHONWARNINGS: process.env.PYTHONWARNINGS || "ignore",
      },
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
    child.stdin.write(stdinJson);
    child.stdin.end();
  });
}

function runArchivePy(args) {
  const root = resolveProjectRoot();
  const script = path.join(__dirname, "scripts", "volc_archive.py");
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, [script, ...args], {
      cwd: root,
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
    name: "volc-jimeng",
    version: "1.0.0",
  },
  {
    capabilities: { tools: {} },
  }
);

server.registerTool(
  "volcengine_docs",
  {
    title: "火山接入与即梦文档链接",
    description:
      "返回 AI 中台接入说明、即梦视频接口文档链接（不涉及密钥）。",
    inputSchema: z.object({}),
  },
  async () => {
    const text = [
      "【接入说明】https://www.volcengine.com/docs/6444/69732?lang=zh",
      "【快速接入】https://www.volcengine.com/docs/6444/69729?lang=zh",
      "【即梦视频 3.0 Pro 接口】https://www.volcengine.com/docs/85621/1777001?lang=zh",
      "【HTTP 请求示例】https://www.volcengine.com/docs/6444/1390583?lang=zh",
      "",
      "控制台创建访问密钥：API 访问密钥（AK/SK）。",
      "即梦需在控制台开通对应能力并保证账户有余额。",
      "本 MCP 工具 volc_visual_submit / volc_visual_query 的 action 与 body 请严格按接口文档填写。",
      "volc_merge_local_videos：本机 ffmpeg 拼接 MP4；可选环境变量 VOLC_PROJECT_ROOT、VOLC_MERGE_OUTPUT_DIR、FFMPEG_PATH。",
      "local_render_pipeline：local_pipeline.py（拼接+BGM+软字幕轨），需 ffmpeg 与 Python3。",
      "local_tts_edge_batch：tts_batch_edge.py（edge-tts），需 pip install edge-tts。",
      "local_mix_tts_srt：mix_tts_from_srt.py（按 SRT 起点叠 TTS 到成片音轨），需 ffmpeg。",
      "",
      "【文生视频 vs 素材】文生视频只需 req_key、prompt、aspect_ratio 等，无需图片。",
      "图生视频/首帧需按文档在 body 里传图片 URL 或文档要求的字段；本 MCP 不会替你上传本地文件，需可访问的图链或控制台支持的传参方式。",
    ].join("\n");
    return { content: [{ type: "text", text }] };
  }
);

server.registerTool(
  "volc_visual_query",
  {
    title: "查询火山 visual 异步任务结果",
    description:
      "调用 CVSync2AsyncGetResult（与即梦文档一致）。提交任务后返回的 task_id 在此查询状态与视频地址；req_key 须与提交时 body.req_key 一致。",
    inputSchema: z.object({
      task_id: z.string().describe("提交任务接口返回的 task_id"),
      req_key: z
        .string()
        .optional()
        .describe("与提交时相同，文生视频 3.0 Pro 常用 jimeng_ti2v_v30_pro"),
      version: z
        .string()
        .optional()
        .describe("接口 Version，默认 2022-08-31"),
    }),
  },
  async ({ task_id, req_key, version }) => {
    const payload = JSON.stringify({
      action: "CVSync2AsyncGetResult",
      version: version || "2022-08-31",
      body: {
        req_key: req_key || "jimeng_ti2v_v30_pro",
        task_id,
      },
    });
    const out = await runPython(payload);
    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "volc_download_video",
  {
    title: "下载视频到本地（可命名）",
    description:
      "将即梦等返回的 video_url 直链保存为 MP4。默认目录为项目 video/generated，可用环境变量 VOLC_DOWNLOAD_DIR 覆盖。",
    inputSchema: z.object({
      url: z
        .string()
        .url()
        .describe("查询结果里的 video_url 等 HTTPS 直链"),
      filename: z
        .string()
        .optional()
        .describe(
          "保存文件名，可含中文，如「第01镜_场1-1A」；不含 .mp4 会自动补上。省略则自动生成 jimeng_时间戳.mp4"
        ),
    }),
  },
  async ({ url, filename }) => {
    const dir = resolveDownloadDir();
    const name = filename
      ? safeVideoFilename(filename)
      : safeVideoFilename(
          `jimeng_${new Date().toISOString().replace(/[:.]/g, "-")}`
        );
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
  "local_render_pipeline",
  {
    title: "本地自动化成片（ffmpeg 拼接/BGM/字幕）",
    description:
      "调用仓库 video/automation/local_pipeline.py：按配置拼接多段 MP4，可选铺 BGM、封装 SRT 为软字幕轨（mov_text）。需 ffmpeg 与 Python3。VOLC_PROJECT_ROOT 指向仓库根。",
    inputSchema: z
      .object({
        config_path: z
          .string()
          .optional()
          .describe(
            "相对仓库根的 JSON，如 video/automation/config_ep01.json；若填写则优先使用，忽略 clips"
          ),
        clips: z
          .array(z.string())
          .optional()
          .describe(
            "至少 2 条 MP4 相对路径（顺序即成片顺序）；未给 config_path 时必填"
          ),
        output: z
          .string()
          .optional()
          .describe(
            "输出 MP4 相对路径；仅在使用 clips 时生效，默认 video/output/mcp_local_render.mp4"
          ),
        bgm: z
          .string()
          .optional()
          .nullable()
          .describe("BGM 相对路径，如 video/assets/bgm.mp3；仅 clips 模式"),
        bgm_volume: z.number().optional().describe("0～1，默认 0.22；仅 clips 模式"),
        srt: z
          .string()
          .optional()
          .nullable()
          .describe("字幕 SRT 相对路径（软封装）；仅 clips 模式"),
      })
      .refine(
        (d) =>
          Boolean(d.config_path) ||
          (Array.isArray(d.clips) && d.clips.length >= 2),
        { message: "须提供 config_path，或提供至少 2 条 clips" }
      ),
  },
  async (input) => {
    const root = resolveProjectRoot();
    const scriptPath = path.join(root, "video", "automation", "local_pipeline.py");
    await stat(scriptPath);

    let configAbs;
    let tempPath = null;
    if (input.config_path) {
      configAbs = resolveUserPath(input.config_path);
      await stat(configAbs);
    } else {
      const cfg = {
        clips: input.clips,
        output: input.output || "video/output/mcp_local_render.mp4",
        bgm: input.bgm ?? null,
        bgm_volume: input.bgm_volume ?? 0.22,
        srt: input.srt ?? null,
      };
      tempPath = path.join(
        tmpdir(),
        `volc-pipeline-${process.pid}-${Date.now()}.json`
      );
      await writeFile(tempPath, JSON.stringify(cfg, null, 2), "utf8");
      configAbs = tempPath;
    }

    try {
      const text = await runLocalPipelinePy(configAbs);
      return { content: [{ type: "text", text }] };
    } finally {
      if (tempPath) {
        await unlink(tempPath).catch(() => {});
      }
    }
  }
);

server.registerTool(
  "local_tts_edge_batch",
  {
    title: "本地批量配音（edge-tts）",
    description:
      "调用 video/automation/tts_batch_edge.py：按行读对白文本，生成 001.mp3、002.mp3… 需 pip install edge-tts。时间轴可与 local_mix_tts_srt 配合（同目录 SRT + 数字命名的 mp3）。",
    inputSchema: z.object({
      lines_path: z
        .string()
        .describe("对白 UTF-8 文本相对仓库根，一行一句；空行跳过不生成文件"),
      out_dir: z
        .string()
        .describe("输出目录相对仓库根，如 video/automation/tts_out"),
      voice: z
        .string()
        .optional()
        .describe("默认 zh-CN-XiaoxiaoNeural；可用 edge-tts --list-voices 查看"),
    }),
  },
  async ({ lines_path, out_dir, voice }) => {
    const root = resolveProjectRoot();
    const scriptPath = path.join(root, "video", "automation", "tts_batch_edge.py");
    await stat(scriptPath);
    const linesAbs = resolveUserPath(lines_path);
    const outDirAbs = resolveUserPath(out_dir);
    await stat(linesAbs);
    await mkdir(outDirAbs, { recursive: true });
    const text = await runTtsBatchPy(linesAbs, outDirAbs, voice);
    return { content: [{ type: "text", text }] };
  }
);

server.registerTool(
  "local_mix_tts_srt",
  {
    title: "本地按 SRT 叠 TTS 到成片",
    description:
      "调用 video/automation/mix_tts_from_srt.py：将 tts_out 内 001/002…（可跳号）.mp3 按 SRT 每条起始时间混到成片音轨。SRT 条数须与 mp3 数量一致（与 gen_srt_from_clips + 同一套对白一致）。需 ffmpeg。",
    inputSchema: z.object({
      video_path: z.string().describe("成片 MP4，相对仓库根"),
      srt_path: z.string().describe("与成片对齐的 UTF-8 SRT"),
      tts_dir: z.string().describe("含数字命名 .mp3 的目录，如 video/automation/tts_out"),
      output_path: z.string().describe("输出 MP4，相对仓库根"),
      original_volume: z
        .number()
        .optional()
        .describe("保留原音轨音量 0～1，默认 0.4"),
      dry_run: z
        .boolean()
        .optional()
        .describe("为 true 时只打印 ffmpeg 命令 JSON"),
    }),
  },
  async ({
    video_path,
    srt_path,
    tts_dir,
    output_path,
    original_volume,
    dry_run,
  }) => {
    const root = resolveProjectRoot();
    const scriptPath = path.join(root, "video", "automation", "mix_tts_from_srt.py");
    await stat(scriptPath);
    const videoAbs = resolveUserPath(video_path);
    const srtAbs = resolveUserPath(srt_path);
    const ttsDirAbs = resolveUserPath(tts_dir);
    const outputAbs = resolveUserPath(output_path);
    await stat(videoAbs);
    await stat(srtAbs);
    await stat(ttsDirAbs);
    await mkdir(path.dirname(outputAbs), { recursive: true });
    const text = await runMixTtsSrtPy(
      videoAbs,
      srtAbs,
      ttsDirAbs,
      outputAbs,
      original_volume,
      Boolean(dry_run)
    );
    return { content: [{ type: "text", text }] };
  }
);

server.registerTool(
  "volc_merge_local_videos",
  {
    title: "本地 MP4 按顺序拼接（ffmpeg）",
    description:
      "将多条本地 MP4 无损拼接（优先 -c copy），失败则自动重编码。需本机已安装 ffmpeg（brew install ffmpeg）。路径可为相对仓库根或绝对路径。",
    inputSchema: z.object({
      input_paths: z
        .array(z.string())
        .min(2)
        .describe(
          "按播放顺序排列，如 [\"video/generated/第01镜_场1-1A_jimeng.mp4\", ...]，或绝对路径"
        ),
      output_filename: z
        .string()
        .optional()
        .describe(
          "输出文件名，默认 merged_<时间戳>.mp4；不含 .mp4 会自动补上。写入 VOLC_MERGE_OUTPUT_DIR 或 video/output"
        ),
      force_reencode: z
        .boolean()
        .optional()
        .describe("为 true 时跳过流复制，直接 libx264+aac 重编码（编码不一致时可用）"),
    }),
  },
  async ({ input_paths, output_filename, force_reencode }) => {
    const resolved = input_paths.map((p) => resolveUserPath(p));
    for (const abs of resolved) {
      await stat(abs);
    }
    const outDir = resolveMergeOutputDir();
    await mkdir(outDir, { recursive: true });
    const outName = output_filename
      ? safeVideoFilename(output_filename)
      : safeVideoFilename(`merged_${new Date().toISOString().replace(/[:.]/g, "-")}`);
    const outputPath = path.join(outDir, outName);

    const listContent = `${resolved.map(concatFileLine).join("\n")}\n`;
    const listPath = path.join(
      tmpdir(),
      `volc-merge-${process.pid}-${Date.now()}.txt`
    );
    await writeFile(listPath, listContent, "utf8");
    try {
      if (force_reencode) {
        await runFfmpeg([
          "-y",
          "-f",
          "concat",
          "-safe",
          "0",
          "-i",
          listPath,
          "-c:v",
          "libx264",
          "-preset",
          "fast",
          "-crf",
          "20",
          "-c:a",
          "aac",
          "-b:a",
          "128k",
          outputPath,
        ]);
      } else {
        try {
          await runFfmpeg([
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            listPath,
            "-c",
            "copy",
            outputPath,
          ]);
        } catch {
          await runFfmpeg([
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            listPath,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            outputPath,
          ]);
        }
      }
    } finally {
      await unlink(listPath).catch(() => {});
    }

    const st = await stat(outputPath);
    const text = JSON.stringify(
      {
        outputPath,
        filename: outName,
        bytes: st.size,
        mode: force_reencode ? "reencode" : "copy_or_reencode",
      },
      null,
      2
    );
    return { content: [{ type: "text", text }] };
  }
);

server.registerTool(
  "volc_visual_submit",
  {
    title: "调用火山 visual 接口（JSON Body）",
    description:
      "使用 AK/SK 签名，向 visual.volcengineapi.com 提交 JSON。action/version/body 须与官方「即梦视频」接口文档一致。",
    inputSchema: z.object({
      action: z
        .string()
        .describe("接口 Action，例如文档中的 CVSync2AsyncSubmitTask（以文档为准）"),
      version: z
        .string()
        .optional()
        .describe("接口 Version，默认 2022-08-31"),
      body: z
        .any()
        .describe("请求 Body，与官方接口一致（含 req_key、prompt 等）"),
    }),
  },
  async ({ action, version, body }) => {
    const payload = JSON.stringify({
      action,
      version: version || "2022-08-31",
      body: body || {},
    });
    const out = await runPython(payload);

    // 尝试解析响应并归档
    try {
      const result = JSON.parse(out);
      // 即梦响应格式：result.data.task_id 或 result.task_id
      const taskId = result?.data?.task_id || result?.task_id;
      if (taskId) {
        // 归档任务
        runArchivePy([
          "add",
          action,
          taskId,
          JSON.stringify({ version: version || "2022-08-31", body: body || {} }),
        ]);
      }
    } catch (e) {
      // 忽略解析错误
    }

    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "jimeng_image_submit",
  {
    title: "即梦AI图片生成4.0",
    description:
      "调用即梦AI图片生成4.0 API (req_key: jimeng_t2i_v40)，支持文生图和图生图。文档：https://www.volcengine.com/docs/85621/1817045",
    inputSchema: z.object({
      prompt: z.string().describe("图片描述文本，中英文均可，最长800字符"),
      image_urls: z.array(z.string()).optional().describe("参考图片URL数组，最多10张，用于图生图或角色参考"),
      width: z.number().optional().describe("输出图片宽度，如1024"),
      height: z.number().optional().describe("输出图片高度，如1024"),
      force_single: z.boolean().optional().describe("是否强制生成单张图片，默认true"),
    }),
  },
  async ({ prompt, image_urls, width, height, force_single }) => {
    const body = {
      req_key: "jimeng_t2i_v40",
      prompt,
      force_single: force_single !== false,
    };
    if (image_urls && image_urls.length > 0) {
      body.image_urls = image_urls;
    }
    if (width && height) {
      body.width = width;
      body.height = height;
    } else {
      // 默认9:16竖屏比例 1024x1856
      body.width = 1024;
      body.height = 1856;
    }
    const payload = JSON.stringify({
      action: "CVSync2AsyncSubmitTask",
      version: "2022-08-31",
      body,
    });
    const out = await runPython(payload);

    // 归档图片任务
    try {
      const result = JSON.parse(out);
      const taskId = result?.data?.task_id || result?.task_id;
      if (taskId) {
        runArchivePy([
          "add",
          "jimeng_image",
          taskId,
          JSON.stringify({ req_key: "jimeng_t2i_v40", prompt }),
        ]);
      }
    } catch (e) {}

    return { content: [{ type: "text", text: out }] };
  }
);

server.registerTool(
  "volc_list_tasks",
  {
    title: "列出归档的任务",
    description: "列出本地归档的火山引擎任务记录。",
    inputSchema: z.object({
      limit: z.number().optional().describe("显示条数，默认20"),
    }),
  },
  async ({ limit }) => {
    const out = await runArchivePy(["list", String(limit || 20)]);
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
