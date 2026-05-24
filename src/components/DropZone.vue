<script setup lang="ts">
import { ref } from "vue";

const emit = defineEmits<{
  "file-selected": [path: string];
}>();

const dragging = ref(false);

function onDragOver(e: DragEvent) {
  e.preventDefault();
  dragging.value = true;
}

function onDragLeave() {
  dragging.value = false;
}

function onDrop(e: DragEvent) {
  e.preventDefault();
  dragging.value = false;
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    const file = files[0];
    if (file.name.toLowerCase().endsWith(".pdf")) {
      emit("file-selected", (file as any).path || file.name);
    }
  }
}

async function onBrowse() {
  try {
    const { open } = await import("@tauri-apps/plugin-dialog");
    const selected = await open({
      filters: [{ name: "PDF Files", extensions: ["pdf"] }],
      multiple: false,
    });
    if (selected) {
      emit("file-selected", selected as string);
    }
  } catch {
    // Fallback: use browser file input
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".pdf";
    input.onchange = () => {
      const file = input.files?.[0];
      if (file) {
        emit("file-selected", (file as any).path || file.name);
      }
    };
    input.click();
  }
}
</script>

<template>
  <div
    class="dropzone"
    :class="{ dragging }"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
    @click="onBrowse"
  >
    <div class="dropzone-icon">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="12" y1="18" x2="12" y2="12"/>
        <polyline points="9 15 12 12 15 15"/>
      </svg>
    </div>
    <p class="dropzone-title">Drop your PDF here</p>
    <p class="dropzone-hint">or click to browse</p>
  </div>
</template>

<style scoped>
.dropzone {
  width: 100%;
  height: 220px;
  border: 2px dashed #444;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s;
  gap: 10px;
}

.dropzone:hover,
.dropzone.dragging {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.08);
}

.dropzone-icon {
  color: #555;
  transition: color 0.25s;
}

.dropzone:hover .dropzone-icon,
.dropzone.dragging .dropzone-icon {
  color: #667eea;
}

.dropzone-title {
  font-size: 16px;
  font-weight: 600;
  color: #ccc;
}

.dropzone-hint {
  font-size: 13px;
  color: #666;
}
</style>
