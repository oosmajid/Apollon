// src/stores/layout.js
import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useLayoutStore = defineStore('layout', () => {
  const isSidebarCollapsed = ref(false)
  const pageTitle = ref('داشبورد')

  function toggleSidebar() {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
  }
  function setPageTitle(newTitle) {
    pageTitle.value = newTitle
  }

  return { isSidebarCollapsed, pageTitle, toggleSidebar, setPageTitle }
})