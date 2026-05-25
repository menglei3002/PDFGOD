<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { getCurrentWindow } from "@tauri-apps/api/window";

defineProps<{ compact?: boolean }>();

const emit = defineEmits<{
  "files-selected": [paths: string[]];
}>();

const dragging = ref(false);
let unlisten: (() => void) | null = null;

onMounted(async () => {
  unlisten = await getCurrentWindow().onDragDropEvent((event) => {
    if (event.payload.type === "over") {
      dragging.value = true;
    } else if (event.payload.type === "leave") {
      dragging.value = false;
    } else if (event.payload.type === "drop") {
      dragging.value = false;
      const paths = event.payload.paths.filter((p) =>
        p.toLowerCase().endsWith(".pdf")
      );
      if (paths.length > 0) {
        emit("files-selected", paths);
      }
    }
  });
});

onUnmounted(() => {
  if (unlisten) unlisten();
});

function onDragOver(e: DragEvent) {
  e.preventDefault();
}

function onDrop(e: DragEvent) {
  e.preventDefault();
}

async function onBrowse() {
  try {
    const { open } = await import("@tauri-apps/plugin-dialog");
    const selected = await open({
      filters: [{ name: "PDF Files", extensions: ["pdf"] }],
      multiple: true,
    });
    if (selected) {
      const paths = Array.isArray(selected) ? selected : [selected];
      emit("files-selected", paths);
    }
  } catch {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".pdf";
    input.multiple = true;
    input.onchange = () => {
      const files = Array.from(input.files || []);
      const paths = files.map((f) => (f as any).path || f.name);
      emit("files-selected", paths);
    };
    input.click();
  }
}
</script>

<template>
  <div
    class="dropzone"
    :class="{ dragging, compact }"
    @dragover="onDragOver"
    @drop="onDrop"
    @click="onBrowse"
  >
    <div class="dropzone-icon">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="12" y1="18" x2="12" y2="12"/>
        <polyline points="9 15 12 12 15 15"/>
      </svg>
    </div>
    <p class="dropzone-title">{{ compact ? 'Add More PDF Files' : 'Drop PDF files here' }}</p>
    <p class="dropzone-hint">or click to browse</p>
  </div>
</template>

<style scoped>
.dropzone {
  width: 100%;
  border: 2px dashed #444;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s;
  gap: 8px;
}

.dropzone:not(.compact) {
  height: 220px;
}

.dropzone.compact {
  height: 80px;
  border-radius: 10px;
  flex-direction: row;
  gap: 12px;
  padding: 0 16px;
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
  font-size: 15px;
  font-weight: 600;
  color: #ccc;
}

.dropzone.compact .dropzone-title {
  font-size: 13px;
}

.dropzone-hint {
  font-size: 12px;
  color: #666;
}

.dropzone.compact .dropzone-hint {
  display: none;
}
</style>
