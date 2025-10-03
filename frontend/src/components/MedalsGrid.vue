<script setup>
import { computed } from 'vue';
import { useDataStore } from '@/stores/dataStore.js';

const dataStore = useDataStore();

const props = defineProps({
  earnedMedalIds: {
    type: Array,
    default: () => []
  }
});

// ۱. تعریف رویدادی که به والد ارسال می‌شود
const emit = defineEmits(['medal-click']);

const sortedMedals = computed(() => {
  const earnedSet = new Set(props.earnedMedalIds);
  return [...dataStore.medals].sort((a, b) => {
    const aEarned = earnedSet.has(a.id) ? 1 : 0;
    const bEarned = earnedSet.has(b.id) ? 1 : 0;
    return bEarned - aEarned;
  });
});
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h4>مدال‌های کسب شده</h4>
      </div>
    <div class="medals-grid">
      <div
        v-for="medal in sortedMedals"
        :key="medal.id"
        class="medal"
        :class="{ active: props.earnedMedalIds.includes(medal.id) }"
        :title="medal.name"
        @click="emit('medal-click', medal)" 
      >
        <i :class="medal.icon"></i>
        <span>{{ medal.name }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* استایل‌ها بدون تغییر باقی می‌مانند */
.card { background-color: var(--surface-color); border-radius: var(--border-radius); padding: 25px; box-shadow: var(--shadow-color) 0px 7px 29px 0px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.medals-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 25px; text-align: center; }
.medal { transition: transform 0.2s ease-in-out; }
.medal:hover { transform: translateY(-5px); cursor: pointer; }
.medal i { font-size: 2.5rem; display: block; margin-bottom: 8px; }
.medal.active i, .medal.active span { color: var(--star-color); }
.medal:not(.active) i, .medal:not(.active) span { color: var(--border-color); opacity: 0.7; }
</style>