<script setup>
defineProps({
  count: { type: Number, default: 0 }
});
</script>

<template>
  <div class="hearts-container">
    <i v-for="i in count" :key="`full-${i}`" class="fa-solid fa-heart full-heart"></i>
    <i v-for="i in (3 - count)" :key="`empty-${i}`" class="fa-solid fa-heart empty-heart"></i>
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