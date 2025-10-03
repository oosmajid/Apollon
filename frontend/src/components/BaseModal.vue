<script setup>
defineProps({
  show: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'md'
  }
})
const emit = defineEmits(['close'])
</script>

<template>
  <Transition name="fade">
    <div v-if="show" class="modal-backdrop" @click.self="emit('close')">
      <div class="modal-content" :class="`modal-${size}`">
        <header class="modal-header">
          <slot name="header">عنوان پیش‌فرض</slot>
          <button @click="emit('close')" class="close-button">&times;</button>
        </header>
        <section class="modal-body">
          <slot></slot>
        </section>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 5000;
}
.modal-content {
  background-color: var(--surface-color);
  padding: 25px;
  border-radius: var(--border-radius);
  width: 90%;
  box-shadow: var(--shadow-color) 0px 7px 29px 0px;
  display: flex; /* برای کنترل بهتر ارتفاع */
  flex-direction: column; /* چیدمان عمودی */
  max-height: 90vh; /* حداکثر ارتفاع مودال */
}
/* تعریف اندازه‌های مختلف برای مودال */
.modal-content.modal-md {
  max-width: 500px; /* اندازه پیش‌فرض */
}
.modal-content.modal-lg {
  max-width: 800px; /* اندازه بزرگ */
}
.modal-content.modal-xl {
  max-width: 1140px; /* اندازه خیلی بزرگ */
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 15px;
  margin-bottom: 20px;
  flex-shrink: 0; /* جلوگیری از کوچک شدن هدر */
}
.modal-body {
  overflow-y: auto; /* افزودن اسکرول در صورت نیاز */
  padding-right: 10px; /* فاصله برای اسکرول‌بار */
  margin-right: -10px; /* جبران فاصله */
}
.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: var(--text-secondary);
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>