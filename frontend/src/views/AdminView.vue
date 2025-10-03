<script setup>
import { ref } from 'vue'
import AdminCoursesTab from '@/components/AdminCoursesTab.vue'
import AdminTermsTab from '@/components/AdminTermsTab.vue'
import AdminStudentsTab from '@/components/AdminStudentsTab.vue'
import AdminApollonyarsTab from '@/components/AdminApollonyarsTab.vue'
import AdminGroupsTab from '@/components/AdminGroupsTab.vue'
import AdminMedalsTab from '@/components/AdminMedalsTab.vue'
import AdminDiscountsTab from '@/components/AdminDiscountsTab.vue' // ۱. کامپوننت جدید را import کنید
import { onMounted } from 'vue'
import { useLayoutStore } from '@/stores/layout.js'
const layoutStore = useLayoutStore()
onMounted(() => {
  layoutStore.setPageTitle('پنل ادمین')
})
const activeTab = ref('courses')

function setActiveTab(tabName) {
  activeTab.value = tabName
}
</script>

<template>
  <div class="admin-panel card">
    <nav class="tabs-nav">
      <button
        @click="setActiveTab('courses')"
        :class="{ active: activeTab === 'courses' }"
        class="tab-button"
      >
        <i class="fa-solid fa-layer-group"></i> دوره‌ها
      </button>
      <button
        @click="setActiveTab('terms')"
        :class="{ active: activeTab === 'terms' }"
        class="tab-button"
      >
        <i class="fa-solid fa-calendar-alt"></i> ترم‌ها
      </button>
      <button
        @click="setActiveTab('apollonyars')"
        :class="{ active: activeTab === 'apollonyars' }"
        class="tab-button"
      >
        <i class="fa-solid fa-user-astronaut"></i> آپولون‌یارها
      </button>
      <button
        @click="setActiveTab('groups')"
        :class="{ active: activeTab === 'groups' }"
        class="tab-button"
      >
        <i class="fa-solid fa-users-rectangle"></i> گروه‌ها
      </button>
      <button
        @click="setActiveTab('students')"
        :class="{ active: activeTab === 'students' }"
        class="tab-button"
      >
        <i class="fa-solid fa-users"></i> هنرجویان
      </button>
      <button
        @click="setActiveTab('medals')"
        :class="{ active: activeTab === 'medals' }"
        class="tab-button"
      >
        <i class="fa-solid fa-award"></i> مدال‌ها
      </button>
      <button
        @click="setActiveTab('discounts')"
        :class="{ active: activeTab === 'discounts' }"
        class="tab-button"
      >
        <i class="fa-solid fa-percent"></i> کدهای تخفیف
      </button>
    </nav>

    <div class="tabs-content">
      <div v-if="activeTab === 'courses'"><AdminCoursesTab /></div>
      <div v-if="activeTab === 'terms'"><AdminTermsTab /></div>
      <div v-if="activeTab === 'apollonyars'"><AdminApollonyarsTab /></div>
      <div v-if="activeTab === 'groups'"><AdminGroupsTab /></div>
      <div v-if="activeTab === 'students'"><AdminStudentsTab /></div>
      <div v-if="activeTab === 'medals'"><AdminMedalsTab /></div>
      <div v-if="activeTab === 'discounts'"><AdminDiscountsTab /></div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background-color: var(--surface-color);
  border-radius: var(--border-radius);
  padding: 25px;
  box-shadow: var(--shadow-color) 0px 7px 29px 0px;
}
.tabs-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 25px;
}
.tab-button {
  background: none;
  border: none;
  padding: 15px 20px;
  cursor: pointer;
  color: var(--text-secondary);
  font-family: 'Vazirmatn', sans-serif;
  font-size: 1rem;
  border-bottom: 3px solid transparent;
  transition: color 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.tab-button.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.tab-button:hover:not(.active) {
  color: var(--text-primary);
}
</style>
