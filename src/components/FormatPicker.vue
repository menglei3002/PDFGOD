<script setup lang="ts">
import { ref } from "vue";

defineProps<{ disabled: boolean }>();
const emit = defineEmits<{ "format-selected": [format: string] }>();

const formats = [
  { value: "word", label: "Word (.docx)", icon: "📝", desc: "Editable document" },
  { value: "excel", label: "Excel (.xlsx)", icon: "📊", desc: "Extract tables" },
  { value: "ppt", label: "PPT (.pptx)", icon: "📽", desc: "Presentation slides" },
  { value: "txt", label: "TXT (.txt)", icon: "📄", desc: "Plain text" },
  { value: "image", label: "Images (.png)", icon: "🖼", desc: "One image per page" },
  { value: "ocr", label: "OCR (Scan → Word)", icon: "🔍", desc: "Recognize scanned text" },
];

const active = ref("word");

function select(format: string) {
  active.value = format;
  emit("format-selected", format);
}
</script>

<template>
  <div class="format-picker">
    <p class="section-label">Output Format</p>
    <div class="format-grid">
      <button
        v-for="fmt in formats"
        :key="fmt.value"
        class="format-btn"
        :class="{ active: active === fmt.value }"
        :disabled="disabled"
        @click="select(fmt.value)"
      >
        <span class="format-icon">{{ fmt.icon }}</span>
        <span class="format-label">{{ fmt.label }}</span>
        <span class="format-desc">{{ fmt.desc }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.format-picker {
  width: 100%;
}

.section-label {
  font-size: 13px;
  color: #888;
  margin-bottom: 8px;
  font-weight: 500;
}

.format-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.format-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 6px;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  color: #ccc;
}

.format-btn:hover:not(:disabled) {
  border-color: #555;
  background: #222;
}

.format-btn.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.12);
  color: #fff;
}

.format-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.format-icon {
  font-size: 22px;
}

.format-label {
  font-size: 12px;
  font-weight: 600;
}

.format-desc {
  font-size: 10px;
  color: #666;
}

.format-btn.active .format-desc {
  color: #888;
}
</style>
