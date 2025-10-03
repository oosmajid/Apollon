<script setup>
import { RouterView } from 'vue-router'
import AppSidebar from '../components/AppSidebar.vue'
import AppHeader from '../components/AppHeader.vue'

// استور را برای کلاس دینامیک nav-collapsed نیاز داریم
import { useLayoutStore } from '@/stores/layout.js'
const layoutStore = useLayoutStore()
</script>

<template>
  <div class="grid-container" :class="{ 'nav-collapsed': layoutStore.isSidebarCollapsed }">
    <AppSidebar :is-collapsed="layoutStore.isSidebarCollapsed" />
    <main class="main-content">
      <AppHeader />
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  height: 100vh;
  transition: grid-template-columns 0.3s ease-in-out;
}

/* استایل برای حالت بسته بودن سایدبار */
.grid-container.nav-collapsed {
  grid-template-columns: 90px 1fr;
}

.main-content {
  padding: 30px;
  overflow-y: auto;
  min-width: 0; /* برای جلوگیری از سرریز شدن گرید */
}
</style>