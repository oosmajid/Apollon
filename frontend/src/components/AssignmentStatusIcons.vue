<script setup>
defineProps({
  statuses: {
    type: Array,
    default: () => [] // e.g., ['completed', 'missed', 'pending']
  }
});
</script>

<template>
  <div class="status-container">
    <div v-for="(status, index) in statuses" :key="index" class="status-icon-wrapper">
      <i
        v-if="status === 'completed'"
        class="fa-solid fa-circle-check icon-completed"
        title="تکمیل شده"
      ></i>
      <i
        v-else-if="status === 'missed'"
        class="fa-solid fa-circle-xmark icon-missed"
        title="انجام نشده"
      ></i>
      <i
        v-else
        class="fa-solid fa-circle icon-pending"
        title="در انتظار"
      ></i>
    </div>
  </div>
</template>

<style scoped>
.status-container {
  display: flex;
  gap: 4px;
  align-items: center;
}
.status-icon-wrapper i {
  font-size: 1rem;
}
.icon-completed {
  color: #22c55e; /* green-500 */
}
.icon-missed {
  color: #ef4444; /* red-500 */
}
.icon-pending {
  color: #e2e8f0; /* slate-200 */
}
[data-theme="dark"] .icon-pending {
    color: #475569; /* slate-600 */
}
</style>