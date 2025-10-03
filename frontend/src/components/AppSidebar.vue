<template>
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="logo">
        <h2 class="logo-text">آکادمی رایان</h2>
        <button @click="layoutStore.toggleSidebar" id="sidebar-toggle-btn" :class="{ 'is-rotated': layoutStore.isSidebarCollapsed }" title="بستن منو">
          <i class="fa-solid fa-chevron-right"></i>
        </button>
      </div>
    <nav class="menu">
        <ul>
            <li>
            <RouterLink :to="{ name: 'dashboard' }" class="menu-item">
                <i class="fa-solid fa-chart-line"></i> <span class="menu-text">داشبورد</span>
            </RouterLink>
            </li>
            <li>
            <RouterLink :to="{ name: 'all-students' }" class="menu-item">
                <i class="fa-solid fa-users"></i> <span class="menu-text">کل هنرجویان</span>
            </RouterLink>
            </li>
            <li>
            <RouterLink :to="{ name: 'my-calls' }" class="menu-item">
                <i class="fa-solid fa-phone-volume"></i> <span class="menu-text">تماس‌های من</span>
            </RouterLink>
            </li>
            <li>
            <RouterLink :to="{ name: 'assignments' }" class="menu-item">
                <i class="fa-solid fa-file-pen"></i> <span class="menu-text">تکالیف</span>
            </RouterLink>
            </li>
            <li>
              <RouterLink :to="{ name: 'installments' }" class="menu-item">
                <i class="fa-solid fa-file-invoice-dollar"></i> <span class="menu-text">پیگیری اقساط</span>
              </RouterLink>
            </li>
            <li>
              <RouterLink :to="{ name: 'transactions' }" class="menu-item">
                <i class="fa-solid fa-money-bill-transfer"></i> <span class="menu-text">تراکنش‌ها</span>
              </RouterLink>
            </li>
            <li>
            <RouterLink :to="{ name: 'admin' }" class="menu-item">
                <i class="fa-solid fa-user-shield"></i> <span class="menu-text">پنل ادمین</span>
            </RouterLink>
            </li>
        </ul>
    </nav>
    </aside>
  </template>

<script setup>
import { useLayoutStore } from '@/stores/layout.js'

// پراپی که از والد فرستاده شده را تعریف می‌کنیم
defineProps({
  isCollapsed: Boolean
})

const layoutStore = useLayoutStore()
</script>
  
<style scoped>
/* Sidebar Styles */
.sidebar {
  width: var(--sidebar-width);
  background-color: var(--surface-color);
  height: 100%;
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  z-index: 100;
  /* انیمیشن برای تغییر عرض اضافه شد */
  transition: width 0.3s ease-in-out;
}

/* استایل‌های حالت بسته */
.sidebar.collapsed {
  width: 90px;
}

.sidebar.collapsed .logo-text,
.sidebar.collapsed .menu-text {
  display: none;
}

.sidebar.collapsed .menu ul li a {
  justify-content: center;
}

/* بقیه استایل‌ها */
.logo {
    padding: 25px;
    text-align: center;
    border-bottom: 1px solid var(--border-color);
    position: relative;
}
.logo h2 {
    color: var(--primary-color);
    font-weight: 700;
}
.menu ul {
    list-style: none;
    padding: 20px 0;
}
.menu ul li a {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px 25px;
    margin: 5px 15px;
    text-decoration: none;
    color: var(--text-secondary);
    font-weight: 500;
    border-radius: var(--border-radius);
    transition: background-color 0.2s, color 0.2s;
}
.menu ul li a i {
    font-size: 1.1em;
}
.menu ul li a:hover {
    background-color: var(--background-color);
    color: var(--primary-color);
}
.menu ul li a.active {
    background-color: var(--primary-color);
    color: #fff;
    box-shadow: 0 4px 8px rgba(106, 90, 205, 0.3);
}
#sidebar-toggle-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 1.2rem;
    cursor: pointer;
    position: absolute;
    left: 20px;
    top: 28px;
    transition: transform 0.3s ease-in-out;
}
#sidebar-toggle-btn.is-rotated {
    transform: rotate(180deg);
}
.menu ul li a.router-link-exact-active {
  background-color: var(--primary-color);
  color: #fff; /* رنگ متن سفید و کاملاً خوانا */
  box-shadow: 0 4px 8px rgba(106, 90, 205, 0.3);
}

/* استایل هاور را هم برای لینک فعال کمی تغییر می‌دهیم */
.menu ul li a.router-link-exact-active:hover {
  background-color: var(--primary-hover);
}
</style>