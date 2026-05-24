<script setup lang="ts">
import { invoke } from "@tauri-apps/api/core";

const props = defineProps<{
  file: string;
  format: string;
  converting: boolean;
  progress: number;
  progressMsg: string;
  error: string;
}>();

const emit = defineEmits<{ start: [] }>();

async function convert() {
  emit("start");
  // The actual invoke is async but progress comes via events
  // We fire-and-forget the invoke; events handle progress/result
  invoke("convert_pdf", {
    input: props.file,
    format: props.format,
  }).catch((e) => {
    console.error("Conversion error:", e);
  });
}
</script>

<template>
  <div class="convert-panel">
    <button
      v-if="!converting && !error"
      class="btn-convert"
      @click="convert"
    >
      Convert to {{ format.toUpperCase() }}
    </button>

    <div v-if="converting" class="progress-section">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: progress + '%' }"
        />
      </div>
      <p class="progress-text">{{ progressMsg }}</p>
    </div>

    <div v-if="error" class="error-box">
      <p class="error-title">Conversion Failed</p>
      <p class="error-msg">{{ error }}</p>
    </div>
  </div>
</template>

<style scoped>
.convert-panel {
  width: 100%;
}

.btn-convert {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-convert:hover {
  opacity: 0.9;
}

.progress-section {
  width: 100%;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #2a2a2a;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: width 0.3s;
}

.progress-text {
  text-align: center;
  font-size: 13px;
  color: #888;
  margin-top: 8px;
}

.error-box {
  padding: 14px;
  background: rgba(255, 80, 80, 0.1);
  border: 1px solid rgba(255, 80, 80, 0.3);
  border-radius: 10px;
}

.error-title {
  font-size: 14px;
  font-weight: 600;
  color: #ff6060;
  margin-bottom: 6px;
}

.error-msg {
  font-size: 12px;
  color: #cc6666;
}
</style>
