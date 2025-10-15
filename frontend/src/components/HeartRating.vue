<script setup>
import { computed } from 'vue'

const props = defineProps({
  count: { type: Number, default: 0 }
});

const safeCount = computed(() => {
  const num = Number(props.count);
  if (isNaN(num) || num < 0) return 0;
  if (num > 3) return 3;
  return Math.floor(num);
});

const emptyCount = computed(() => {
  return Math.max(0, 3 - safeCount.value);
});
</script>

<template>
  <div class="hearts-container">
    <i v-for="i in safeCount" :key="`full-${i}`" class="fa-solid fa-heart full-heart"></i>
    <i v-for="i in emptyCount" :key="`empty-${i}`" class="fa-solid fa-heart empty-heart"></i>
  </div>
</template>

<style scoped>
.hearts-container {
  display: flex;
  gap: 2px;
}
.full-heart {
  color: var(--heart-color);
}
.empty-heart {
  color: var(--border-color);
}
</style>