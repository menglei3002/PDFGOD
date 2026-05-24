<script setup lang="ts">
const props = defineProps<{
  path: string;
  format: string;
}>();

const emit = defineEmits<{ reset: [] }>();

function getFileName(): string {
  const parts = props.path.replace(/\\/g, "/").split("/");
  return parts[parts.length - 1] || "output";
}

</script>

<template>
  <div class="result-card">
    <div class="result-icon">✅</div>
    <p class="result-title">Conversion Complete!</p>
    <p class="result-file">{{ getFileName() }}</p>
    <p class="result-path">{{ path }}</p>
    <button class="btn-reset" @click="emit('reset')">Convert Another File</button>
  </div>
</template>

<style scoped>
.result-card {
  width: 100%;
  padding: 24px;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 14px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.result-icon {
  font-size: 40px;
}

.result-title {
  font-size: 18px;
  font-weight: 600;
  color: #4caf50;
}

.result-file {
  font-size: 14px;
  color: #ccc;
  word-break: break-all;
}

.result-path {
  font-size: 11px;
  color: #555;
  word-break: break-all;
  max-width: 100%;
}

.btn-reset {
  margin-top: 8px;
  padding: 10px 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-reset:hover {
  opacity: 0.9;
}
</style>
