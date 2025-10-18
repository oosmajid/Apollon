<script setup>
import { computed, ref, onMounted } from 'vue';
import api from '@/services/api';

const medals = ref([])
const isLoading = ref(true)

const props = defineProps({
  earnedMedalIds: {
    type: Array,
    default: () => []
  }
});

// ۱. تعریف رویدادی که به والد ارسال می‌شود
const emit = defineEmits(['medal-click']);

// Load medals data on mount
onMounted(async () => {
  try {
    isLoading.value = true
    const response = await api.getMedals()
    medals.value = response.data
  } catch (error) {
    console.error("Failed to fetch medals:", error)
  } finally {
    isLoading.value = false
  }
})

const sortedMedals = computed(() => {
  const earnedSet = new Set(props.earnedMedalIds);
  return [...medals.value].sort((a, b) => {
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
    <div class="medals-grid" v-if="!isLoading && sortedMedals.length > 0">
      <div
        v-for="medal in sortedMedals"
        :key="medal.id"
        class="medal"
        :class="{ active: props.earnedMedalIds.includes(medal.id) }"
        :title="medal.name"
        @click="emit('medal-click', medal)" 
      >
        <i :class="medal.icon || 'fa-solid fa-award'" :style="{ color: medal.icon ? 'inherit' : '#ccc' }"></i>
        <span>{{ medal.name }}</span>
      </div>
    </div>
    <div v-else-if="!isLoading && sortedMedals.length === 0" class="empty-state">
      <i class="fa-solid fa-award"></i>
      <span>هیچ مدالی یافت نشد</span>
    </div>
    <div v-else class="loading-state">
      <i class="fa-solid fa-spinner fa-spin"></i>
      <span>در حال بارگذاری مدال‌ها...</span>
    </div>
  </div>
</template>

<style scoped>
/* استایل‌ها بدون تغییر باقی می‌مانند */
.card { 
  background-color: var(--surface-color); 
  border-radius: var(--border-radius); 
  padding: 25px; 
  box-shadow: var(--shadow-color) 0px 7px 29px 0px; 
}
.card-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 20px; 
}
.medals-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); 
  gap: 20px; 
  text-align: center; 
}
.medal { 
  transition: transform 0.2s ease-in-out; 
  padding: 15px;
  border-radius: 8px;
  border: 2px solid transparent;
}
.medal:hover { 
  transform: translateY(-5px); 
  cursor: pointer; 
  border-color: var(--primary-color, #6a5acd);
}
.medal i { 
  font-size: 2.5rem; 
  display: block; 
  margin-bottom: 8px; 
}
.medal.active { 
  background-color: rgba(255, 215, 0, 0.1);
  border-color: var(--star-color, #facc15);
}
.medal.active i, 
.medal.active span { 
  color: var(--star-color, #facc15); 
  font-weight: bold;
}
.medal:not(.active) i, 
.medal:not(.active) span { 
  color: var(--border-color, #ccc); 
  opacity: 0.5; 
}
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  gap: 15px;
}

.loading-state i {
  font-size: 2rem;
  color: var(--primary-color, #6a5acd);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  gap: 15px;
}

.empty-state i {
  font-size: 3rem;
  color: var(--border-color, #ccc);
  opacity: 0.5;
}

.empty-state span {
  font-size: 1rem;
  font-weight: 500;
}

/* Responsive design */
@media (max-width: 768px) {
  .medals-grid {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 15px;
  }
  .medal i {
    font-size: 2rem;
  }
  .medal span {
    font-size: 0.8rem;
  }
  .loading-state i,
  .empty-state i {
    font-size: 2.5rem;
  }
}

@media (max-width: 480px) {
  .medals-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
  .medal {
    padding: 10px;
  }
  .medal i {
    font-size: 1.8rem;
  }
  .medal span {
    font-size: 0.75rem;
  }
  .loading-state i,
  .empty-state i {
    font-size: 2rem;
  }
}
</style>