<script setup lang="ts">
export interface ConvertResult {
  input: string;
  output?: string;
  error?: string;
}

defineProps<{
  results: ConvertResult[];
}>();

const emit = defineEmits<{ reset: [] }>();

function fileName(p: string): string {
  const parts = p.replace(/\\/g, "/").split("/");
  return parts[parts.length - 1] || p;
}
</script>

<template>
  <div class="results-section" v-if="results.length > 0">
    <p class="results-title">Results ({{ results.filter(r => r.output).length }}/{{ results.length }} succeeded)</p>
    <div
      v-for="(r, i) in results"
      :key="i"
      class="result-item"
      :class="{ success: r.output, error: r.error }"
    >
      <div class="result-left">
        <span class="result-icon">{{ r.output ? 'OK' : 'FAIL' }}</span>
        <div class="result-info">
          <p class="result-file">{{ fileName(r.input) }}</p>
          <p class="result-path" v-if="r.output">{{ r.output }}</p>
          <p class="result-error" v-if="r.error">{{ r.error }}</p>
        </div>
      </div>
    </div>
    <button class="btn-new-task" @click="emit('reset')">New Task</button>
  </div>
</template>

<style scoped>
.results-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.results-title {
  font-size: 13px;
  color: #888;
  font-weight: 500;
  margin-bottom: 4px;
}

.result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 12px;
}

.result-item.success {
  background: rgba(76, 175, 80, 0.08);
  border: 1px solid rgba(76, 175, 80, 0.15);
}

.result-item.error {
  background: rgba(255, 80, 80, 0.06);
  border: 1px solid rgba(255, 80, 80, 0.12);
}

.result-left {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow: hidden;
}

.result-icon {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}

.success .result-icon {
  color: #4caf50;
  background: rgba(76, 175, 80, 0.15);
}

.error .result-icon {
  color: #ff6060;
  background: rgba(255, 80, 80, 0.12);
}

.result-info {
  overflow: hidden;
}

.result-file {
  color: #ccc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-path {
  color: #666;
  font-size: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}

.result-error {
  color: #cc6666;
  font-size: 10px;
  margin-top: 2px;
  word-break: break-all;
}

.btn-new-task {
  margin-top: 12px;
  padding: 10px 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  align-self: center;
}

.btn-new-task:hover {
  opacity: 0.9;
}
</style>
