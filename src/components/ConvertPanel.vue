<script setup lang="ts">
defineProps<{
  fileCount: number;
  converting: boolean;
  hasResults: boolean;
  currentFile: string;
  progress: number;
  progressMsg: string;
}>();

defineEmits<{ convert: [] }>();
</script>

<template>
  <div class="convert-panel">
    <button
      v-if="!converting"
      class="btn-convert"
      :disabled="fileCount === 0"
      @click="$emit('convert')"
    >
      <template v-if="fileCount === 0">Add Files to Start</template>
      <template v-else-if="hasResults">Convert Again ({{ fileCount }} File{{ fileCount > 1 ? 's' : '' }})</template>
      <template v-else>Convert {{ fileCount }} File{{ fileCount > 1 ? 's' : '' }}</template>
    </button>

    <div v-if="converting" class="progress-section">
      <p class="current-file">{{ currentFile }}</p>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }" />
      </div>
      <p class="progress-text">{{ progressMsg }}</p>
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

.btn-convert:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-convert:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.progress-section {
  width: 100%;
}

.current-file {
  font-size: 12px;
  color: #888;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
</style>
