<script setup>
import { ref, onMounted } from 'vue'

import { useLayoutStore } from '@/stores/layout.js'

const layoutStore = useLayoutStore()

// 1. یک متغیر برای نگهداری وضعیت تم می‌سازیم
// مقدار اولیه را از حافظه localStorage می‌خوانیم
const currentTheme = ref(localStorage.getItem('theme') || 'light');

// 2. تابعی که تم را تغییر می‌دهد
function toggleTheme() {
  currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light';
  // مقدار جدید را در localStorage ذخیره می‌کنیم
  localStorage.setItem('theme', currentTheme.value);
  // اتریبیوت data-theme را روی تگ <html> تنظیم می‌کنیم
  document.documentElement.setAttribute('data-theme', currentTheme.value);
}

// 3. وقتی کامپوننت برای اولین بار نمایش داده شد، تم ذخیره شده را اعمال می‌کنیم
onMounted(() => {
  document.documentElement.setAttribute('data-theme', currentTheme.value);
});
</script>

<template>
  <header class="main-header">
    <h1 id="page-title">{{ layoutStore.pageTitle }}</h1>
    <div class="header-actions">
      <div class="theme-switcher">
        <button id="theme-toggle-btn" @click="toggleTheme">
          <i :class="currentTheme === 'light' ? 'fa-solid fa-moon' : 'fa-solid fa-sun'"></i>
        </button>
      </div>
      <div class="profile-menu">
        <span id="apollonyar-name">خوش آمدید، علی رضایی</span>
        <a href="#" class="logout-btn" title="خروج">
          <i class="fa-solid fa-arrow-right-from-bracket"></i>
        </a>
      </div>
    </div>
  </header>
</template>

<style scoped>
/* استایل‌ها بدون تغییر باقی می‌مانند */
.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    flex-wrap: wrap;
    gap: 15px;
}

.main-header h1 {
    font-size: 28px;
    font-weight: 700;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 20px;
}

#theme-toggle-btn {
    background: none;
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}
#theme-toggle-btn:hover {
    background-color: var(--primary-color);
    color: #fff;
    border-color: var(--primary-color);
}

.profile-menu {
    display: flex;
    align-items: center;
    gap: 15px;
}
.profile-menu #apollonyar-name {
    font-weight: 500;
}
.logout-btn {
    color: var(--danger-color);
    font-size: 1.2rem;
    text-decoration: none;
}
.logout-btn:hover {
    opacity: 0.8;
}
</style>