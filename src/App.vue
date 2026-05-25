<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { listen } from "@tauri-apps/api/event";
import { invoke } from "@tauri-apps/api/core";
import DropZone from "./components/DropZone.vue";
import FormatPicker from "./components/FormatPicker.vue";
import ConvertPanel from "./components/ConvertPanel.vue";
import ResultCard from "./components/ResultCard.vue";
import type { ConvertResult } from "./components/ResultCard.vue";

interface FileEntry {
  path: string;
  outputPath: string;
}

const selectedFormat = ref("word");
const files = ref<FileEntry[]>([]);
const converting = ref(false);
const progress = ref(0);
const progressMsg = ref("");
const currentFileName = ref("");
const results = ref<ConvertResult[]>([]);

let unlisten: (() => void) | null = null;

onMounted(async () => {
  unlisten = await listen<{ percent: number; message: string; output?: string; error?: string }>(
    "conversion-progress",
    (event) => {
      const data = event.payload;
      if (!data.error && !data.output) {
        progress.value = data.percent;
        progressMsg.value = data.message;
      }
    }
  );
});

onUnmounted(() => {
  if (unlisten) unlisten();
});

function fileName(p: string): string {
  const parts = p.replace(/\\/g, "/").split("/");
  return parts[parts.length - 1] || p;
}

function onFormatSelected(format: string) {
  selectedFormat.value = format;
}

function onFilesSelected(paths: string[]) {
  const extMap: Record<string, string> = {
    word: "docx", excel: "xlsx", ppt: "pptx", txt: "txt", image: "png", ocr: "docx",
  };
  const ext = extMap[selectedFormat.value] || "docx";
  for (const p of paths) {
    if (!files.value.some((f) => f.path === p)) {
      const inputDir = p.replace(/\\/g, "/").split("/").slice(0, -1).join("/");
      const baseName = fileName(p).replace(/\.pdf$/i, "");
      files.value.push({ path: p, outputPath: `${inputDir}/${baseName}.${ext}` });
    }
  }
}

function onRemoveFile(index: number) {
  files.value.splice(index, 1);
  results.value = [];
}

async function onChooseOutput(index: number) {
  try {
    const extMap: Record<string, string> = {
      word: "docx", excel: "xlsx", ppt: "pptx", txt: "txt", image: "png", ocr: "docx",
    };
    const ext = extMap[selectedFormat.value] || "docx";
    const inputFile = files.value[index].path;
    const inputDir = inputFile.replace(/\\/g, "/").split("/").slice(0, -1).join("/");
    const baseName = fileName(inputFile).replace(/\.pdf$/i, "");
    const defaultPath = `${inputDir}/${baseName}.${ext}`;

    // Dynamic import — matches pattern used by DropZone.vue which works
    const { save } = await import("@tauri-apps/plugin-dialog");
    const saved = await save({
      defaultPath,
      filters: [{ name: selectedFormat.value.toUpperCase(), extensions: [ext] }],
    });
    if (saved) {
      const updated = [...files.value];
      updated[index] = { ...updated[index], outputPath: saved };
      files.value = updated;
    }
  } catch (e) {
    alert("Save dialog failed: " + (e instanceof Error ? e.message : String(e)));
  }
}

async function startBatch() {
  if (files.value.length === 0 || converting.value) return;

  console.warn("[BATCH START]", files.value.length, "files, format:", selectedFormat.value);
  converting.value = true;
  results.value = [];

  for (let i = 0; i < files.value.length; i++) {
    const f = files.value[i];
    currentFileName.value = `[${i + 1}/${files.value.length}] ${fileName(f.path)}`;
    progress.value = 0;
    progressMsg.value = "Starting...";

    try {
      const output = await invoke<string>("convert_pdf", {
        input: f.path,
        format: selectedFormat.value,
        output: f.outputPath || null,
      });
      results.value.push({ input: f.path, output });
    } catch (e) {
      const errStr = typeof e === "string" ? e : String(e);
      results.value.push({ input: f.path, error: errStr });
    }
  }

  currentFileName.value = "";
  progress.value = 0;
  progressMsg.value = "";
  converting.value = false;
}

function onReset() {
  files.value = [];
  results.value = [];
  progress.value = 0;
  progressMsg.value = "";
  currentFileName.value = "";
}
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <h1>PDFGOD</h1>
      <p class="subtitle">Free PDF Converter</p>
    </header>

    <main class="app-main">
      <FormatPicker
        :disabled="converting"
        @format-selected="onFormatSelected"
      />

      <!-- File zone -->
      <div class="file-zone">
        <DropZone
          v-if="!converting"
          :compact="files.length > 0"
          @files-selected="onFilesSelected"
        />

        <!-- File list -->
        <div v-if="files.length > 0" class="file-list">
          <div
            v-for="(f, i) in files"
            :key="f.path"
            class="file-item"
          >
            <div class="file-item-top">
              <span class="file-index">{{ i + 1 }}</span>
              <p class="file-name">{{ fileName(f.path) }}</p>
              <button
                v-if="!converting"
                class="btn-remove"
                @click="onRemoveFile(i)"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <div class="file-item-output-row">
              <svg class="output-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              <span class="output-path" :title="f.outputPath">{{ f.outputPath }}</span>
              <button
                v-if="!converting"
                class="btn-browse"
                @click="onChooseOutput(i)"
              >
                Browse
              </button>
            </div>
          </div>
        </div>
      </div>

      <ConvertPanel
        :file-count="files.length"
        :converting="converting"
        :has-results="results.length > 0"
        :current-file="currentFileName"
        :progress="progress"
        :progress-msg="progressMsg"
        @convert="startBatch"
      />

      <ResultCard
        :results="results"
        @reset="onReset"
      />
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background: #0f0f0f;
  color: #e0e0e0;
  min-height: 100vh;
  overflow-x: hidden;
  overflow-y: auto;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 20px;
}

.app-header {
  text-align: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.app-header h1 {
  font-size: 26px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 2px;
}

.subtitle {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  max-width: 520px;
  margin: 0 auto;
  width: 100%;
}

.file-zone {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 240px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  flex-direction: column;
  padding: 8px 10px;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  gap: 6px;
}

.file-item-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-index {
  font-size: 11px;
  color: #555;
  background: #222;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  flex-shrink: 0;
}

.file-name {
  font-size: 13px;
  color: #ccc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.file-item-output-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-left: 30px;
}

.output-icon {
  color: #666;
  flex-shrink: 0;
}

.output-path {
  font-size: 11px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.btn-browse {
  background: #2a2a2a;
  border: 1px solid #444;
  color: #ccc;
  font-size: 11px;
  cursor: pointer;
  padding: 3px 10px;
  border-radius: 4px;
  flex-shrink: 0;
  transition: all 0.15s;
}

.btn-browse:hover {
  background: #667eea;
  border-color: #667eea;
  color: #fff;
}

.btn-remove {
  background: none;
  border: none;
  color: #555;
  cursor: pointer;
  padding: 4px;
  flex-shrink: 0;
  border-radius: 4px;
}

.btn-remove:hover {
  color: #ff6060;
  background: rgba(255, 80, 80, 0.1);
}
</style>
