<script setup lang="ts">
import { ref } from "vue";
import { listen } from "@tauri-apps/api/event";
import DropZone from "./components/DropZone.vue";
import FormatPicker from "./components/FormatPicker.vue";
import ConvertPanel from "./components/ConvertPanel.vue";
import ResultCard from "./components/ResultCard.vue";

const selectedFile = ref("");
const selectedFormat = ref("word");
const converting = ref(false);
const progress = ref(0);
const progressMsg = ref("");
const resultPath = ref("");
const errorMsg = ref("");

listen<{ percent: number; message: string; output?: string; error?: string }>(
  "conversion-progress",
  (event) => {
    const data = event.payload;
    if (data.error) {
      errorMsg.value = data.error;
      converting.value = false;
    } else if (data.output) {
      progress.value = 100;
      progressMsg.value = "Complete!";
      resultPath.value = data.output;
      converting.value = false;
    } else {
      progress.value = data.percent;
      progressMsg.value = data.message;
    }
  }
);

function onFileSelected(path: string) {
  selectedFile.value = path;
  resultPath.value = "";
  errorMsg.value = "";
}

function onFormatSelected(format: string) {
  selectedFormat.value = format;
}

function onReset() {
  selectedFile.value = "";
  resultPath.value = "";
  errorMsg.value = "";
  progress.value = 0;
  progressMsg.value = "";
}
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <h1>PDFGOD</h1>
      <p class="subtitle">Free PDF Converter - Convert PDF to Word, Excel, PPT, TXT, Images</p>
    </header>

    <main class="app-main">
      <DropZone
        v-if="!selectedFile"
        @file-selected="onFileSelected"
      />

      <template v-else>
        <div class="file-info">
          <span class="file-label">Selected:</span>
          <span class="file-path">{{ selectedFile }}</span>
          <button class="btn-reset" @click="onReset">Change</button>
        </div>

        <FormatPicker
          :disabled="converting"
          @format-selected="onFormatSelected"
        />

        <ConvertPanel
          :file="selectedFile"
          :format="selectedFormat"
          :converting="converting"
          :progress="progress"
          :progress-msg="progressMsg"
          :error="errorMsg"
          @start="converting = true"
        />

        <ResultCard
          v-if="resultPath"
          :path="resultPath"
          :format="selectedFormat"
          @reset="onReset"
        />
      </template>
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
  overflow: hidden;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 24px;
}

.app-header {
  text-align: center;
  margin-bottom: 32px;
}

.app-header h1 {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 2px;
}

.subtitle {
  font-size: 13px;
  color: #888;
  margin-top: 6px;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  max-width: 520px;
  margin: 0 auto;
  width: 100%;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  background: #1a1a1a;
  border-radius: 10px;
  font-size: 13px;
}

.file-label {
  color: #888;
  white-space: nowrap;
}

.file-path {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #c0c0ff;
}

.btn-reset {
  background: none;
  border: 1px solid #444;
  color: #aaa;
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
}

.btn-reset:hover {
  border-color: #667eea;
  color: #667eea;
}
</style>
