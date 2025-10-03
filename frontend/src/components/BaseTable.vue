<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

// =================================================================
// Props: ورودی‌های کامپوننت
// =================================================================
const props = defineProps({
  columns: { type: Array, required: true },
  data: { type: Array, required: true },
  rowsPerPage: { type: Number, default: 10 },
  selectable: { type: Boolean, default: false }, // جدید: فعال‌سازی انتخاب
  modelValue: { type: Array, default: () => [] }, // جدید: v-model برای آیتم‌های انتخاب شده
})

// جدید: تعریف event برای v-model
const emit = defineEmits(['update:modelValue'])

// =================================================================
// بخش فیلتر کردن پیشرفته
// =================================================================
const filters = ref({})
const filterPopup = ref({
  show: false,
  columnKey: null,
  style: {},
  options: [],
  searchTerm: '',
})

// --- تغییر جدید: منطق مربوط به "انتخاب همه" در فیلتر ---
const isAllFilterOptionsSelected = computed(() => {
  if (!filterPopup.value.options) return false
  return filterPopup.value.options.every((opt) => opt.checked)
})

function toggleAllFilterOptions() {
  const newValue = !isAllFilterOptionsSelected.value
  filterPopup.value.options.forEach((opt) => (opt.checked = newValue))
}
// --- پایان تغییر جدید ---

function getUniqueValues(columnKey) {
  const values = props.data.map((item) => item[columnKey])
  return [...new Set(values)].sort()
}

function openFilterPopup(columnKey, event) {
  if (filterPopup.value.show && filterPopup.value.columnKey === columnKey) {
    closeFilterPopup()
    return
  }
  const rect = event.target.getBoundingClientRect()
  filterPopup.value = {
    show: true,
    columnKey,
    style: { top: `${rect.bottom + 5}px`, right: `${window.innerWidth - rect.right}px` },
    options: getUniqueValues(columnKey).map((val) => ({
      value: val,
      checked: filters.value[columnKey]?.includes(val) ?? true,
    })),
    searchTerm: '',
  }
}

function closeFilterPopup() {
  filterPopup.value.show = false
}

function applyFilters() {
  const key = filterPopup.value.columnKey
  const selectedValues = filterPopup.value.options
    .filter((opt) => opt.checked)
    .map((opt) => opt.value)

  if (selectedValues.length === getUniqueValues(key).length || selectedValues.length === 0) {
    delete filters.value[key]
  } else {
    filters.value[key] = selectedValues
  }
  closeFilterPopup()
}

const filteredPopupOptions = computed(() => {
  if (!filterPopup.value.searchTerm) return filterPopup.value.options
  return filterPopup.value.options.filter((opt) =>
    String(opt.value).toLowerCase().includes(filterPopup.value.searchTerm.toLowerCase()),
  )
})

const filteredData = computed(() => {
  const activeFilters = Object.entries(filters.value)
  if (!activeFilters.length) return props.data
  return props.data.filter((item) => {
    return activeFilters.every(([key, values]) => values.includes(item[key]))
  })
})

// =================================================================
// Hooks: onMounted و onUnmounted (ادغام شده)
// =================================================================
onMounted(() => {
  document.addEventListener('click', closeFilterPopupOnClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', closeFilterPopupOnClickOutside)
})

function closeFilterPopupOnClickOutside(event) {
  if (filterPopup.value.show) {
    const popupElement = document.querySelector('.filter-popup')
    const filterIcons = document.querySelectorAll('.filter-icon')
    const clickedOnIcon = Array.from(filterIcons).some((icon) => icon.contains(event.target))
    if (popupElement && !popupElement.contains(event.target) && !clickedOnIcon) {
      closeFilterPopup()
    }
  }
}

// =================================================================
// بخش مرتب‌سازی (Sort)
// =================================================================
const sortCriteria = ref([])

const sortedData = computed(() => {
  let dataToSort = [...filteredData.value]
  if (!sortCriteria.value.length) return dataToSort

  return dataToSort.sort((a, b) => {
    for (const criterion of sortCriteria.value) {
      const valA = a[criterion.key]
      const valB = b[criterion.key]
      if (valA < valB) return criterion.direction === 'asc' ? -1 : 1
      if (valA > valB) return criterion.direction === 'asc' ? 1 : -1
    }
    return 0
  })
})

function handleSort(key) {
  const existingIndex = sortCriteria.value.findIndex((c) => c.key === key)

  if (existingIndex > -1) {
    const currentDirection = sortCriteria.value[existingIndex].direction
    if (currentDirection === 'asc') {
      sortCriteria.value[existingIndex].direction = 'desc'
    } else {
      sortCriteria.value.splice(existingIndex, 1)
    }
  } else {
    sortCriteria.value.push({ key, direction: 'asc' })
  }
}

function getSortDirection(key) {
  const criterion = sortCriteria.value.find((c) => c.key === key)
  return criterion ? criterion.direction : ''
}

// =================================================================
// بخش صفحه‌بندی (Pagination)
// =================================================================
const currentPage = ref(1)

const pageCount = computed(() => {
  if (props.rowsPerPage === 0) return 1
  return Math.ceil(sortedData.value.length / props.rowsPerPage)
})

const paginatedData = computed(() => {
  if (props.rowsPerPage === 0) return sortedData.value
  const start = (currentPage.value - 1) * props.rowsPerPage
  const end = start + props.rowsPerPage
  return sortedData.value.slice(start, end)
})

function changePage(page) {
  if (page > 0 && page <= pageCount.value) {
    currentPage.value = page
  }
}

watch(pageCount, (newPageCount) => {
  if (currentPage.value > newPageCount) {
    currentPage.value = newPageCount || 1
  }
})

// =================================================================
// بخش انتخاب ردیف‌ها (Row Selection) - جدید
// =================================================================
const internalSelection = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const isAllSelected = computed(() => {
  // حالا بررسی می‌کند که آیا تمام آیتم‌های فیلتر شده انتخاب شده‌اند یا خیر
  const allFilteredIds = new Set(sortedData.value.map((item) => item.id))
  const selectedIds = new Set(internalSelection.value)
  return allFilteredIds.size > 0 && Array.from(allFilteredIds).every((id) => selectedIds.has(id))
})

function toggleSelectAll() {
  // حالا تمام آیتم‌های فیلتر شده را انتخاب/عدم انتخاب می‌کند
  const allFilteredIds = sortedData.value.map((item) => item.id)

  if (isAllSelected.value) {
    // اگر همه انتخاب شده بودند، همه را از انتخاب خارج کن
    internalSelection.value = []
  } else {
    // در غیر این صورت، همه را انتخاب کن
    internalSelection.value = allFilteredIds
  }
}
</script>

<template>
  <div>
    <div class="table-container">
      <table>
        <thead>
          <tr class="header-row">
            <th v-if="selectable" class="checkbox-col">
              <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" />
            </th>
            <th v-for="col in columns" :key="col.key" :style="{ width: col.width }">
              <div
                class="header-content"
                :class="{ sortable: col.sortable }"
                @click="col.sortable && handleSort(col.key)"
              >
                <span>{{ col.label }}</span>
                <span v-if="col.sortable" class="sort-icon">
                  <i
                    v-if="getSortDirection(col.key) === 'asc'"
                    class="fa-solid fa-arrow-down-short-wide"
                  ></i>
                  <i
                    v-else-if="getSortDirection(col.key) === 'desc'"
                    class="fa-solid fa-arrow-up-wide-short"
                  ></i>
                  <i v-else class="fa-solid fa-sort"></i>
                </span>
                <i
                  v-if="col.filterable"
                  class="fa-solid fa-filter filter-icon"
                  :class="{ active: filters[col.key] }"
                  @click.stop="openFilterPopup(col.key, $event)"
                ></i>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="paginatedData.length === 0">
            <td :colspan="columns.length + (selectable ? 1 : 0)" class="no-data-cell">
              داده‌ای برای نمایش وجود ندارد.
            </td>
          </tr>
          <tr
            v-for="item in paginatedData"
            :key="item.id"
            :class="{ 'selected-row': selectable && internalSelection.includes(item.id) }"
          >
            <td v-if="selectable" class="checkbox-col">
              <input type="checkbox" :value="item.id" v-model="internalSelection" />
            </td>
            <td v-for="col in columns" :key="col.key">
              <slot :name="`cell-${col.key}`" :item="item">{{ item[col.key] }}</slot>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="filterPopup.show" class="filter-popup" :style="filterPopup.style">
        <input
          type="text"
          v-model="filterPopup.searchTerm"
          placeholder="جستجو در گزینه‌ها..."
          class="popup-search"
        />
        <div class="options-list">
          <div class="option-item select-all-item">
            <input
              type="checkbox"
              id="select-all-filter"
              :checked="isAllFilterOptionsSelected"
              @change="toggleAllFilterOptions"
            />
            <label for="select-all-filter">انتخاب همه</label>
          </div>
          <div v-for="option in filteredPopupOptions" :key="option.value" class="option-item">
            <input type="checkbox" v-model="option.checked" :id="`opt-${option.value}`" />
            <label :for="`opt-${option.value}`">{{ option.value }}</label>
          </div>
        </div>
        <button @click="applyFilters" class="btn-apply-filter">اعمال فیلتر</button>
      </div>
    </div>

    <div v-if="pageCount > 1" class="pagination-container">
      <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="page-btn">
        ‹
      </button>
      <span v-if="pageCount > 5 && currentPage > 3">...</span>
      <button
        v-for="page in pageCount"
        :key="page"
        v-show="Math.abs(page - currentPage) < 2 || page === 1 || page === pageCount"
        @click="changePage(page)"
        class="page-btn"
        :class="{ active: currentPage === page }"
      >
        {{ page }}
      </button>
      <span v-if="pageCount > 5 && currentPage < pageCount - 2">...</span>
      <button
        @click="changePage(currentPage + 1)"
        :disabled="currentPage === pageCount"
        class="page-btn"
      >
        ›
      </button>
    </div>
  </div>
</template>

<style scoped>
.table-container {
  background-color: var(--surface-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-color) 0px 7px 29px 0px;
  overflow-x: auto;
  position: relative;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  padding: 14px 12px;
  text-align: right;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}
thead {
  background-color: var(--background-color);
}
th {
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
  user-select: none;
  position: sticky;
  top: 0;
  background-color: var(--background-color);
}
.header-content {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 10px;
}
.header-content.sortable {
  cursor: pointer;
}
.sort-icon {
  color: #ccc;
}
.sort-icon .fa-arrow-down-short-wide,
.sort-icon .fa-arrow-up-wide-short {
  color: var(--primary-color);
}
.filter-icon {
  cursor: pointer;
  color: #ccc;
  margin-right: auto;
}
.filter-icon.active {
  color: var(--primary-color);
}
.no-data-cell {
  text-align: center;
  color: var(--text-secondary);
  padding: 30px 0;
}
tbody tr:hover {
  background-color: var(--background-color);
}
/* استایل‌های جدید برای انتخاب */
.checkbox-col {
  width: 40px;
  text-align: center;
}
.selected-row td {
  background-color: #e9e7f8 !important;
}
[data-theme='dark'] .selected-row td {
  background-color: #2a2c4e !important;
}

/* Filter Popup Styles */
.filter-popup {
  position: fixed;
  display: flex;
  flex-direction: column;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  width: 250px;
  z-index: 100;
  padding: 10px;
}
.popup-search {
  width: 100%;
  padding: 8px;
  margin-bottom: 10px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}
.options-list {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 10px;
}
.option-item {
  display: flex;
  align-items: center;
  padding: 5px;
  cursor: pointer;
}
.option-item input {
  margin-left: 8px;
}
/* تغییر جدید: استایل برای آیتم "انتخاب همه" */
.select-all-item {
  font-weight: 500;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 5px;
  margin-bottom: 5px;
}
.btn-apply-filter {
  width: 100%;
  background-color: var(--primary-color);
  color: #fff;
  border: none;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
}
/* Pagination Styles */
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 5px;
}
.page-btn {
  background-color: var(--surface-color);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.page-btn:hover,
.page-btn.active {
  background-color: var(--primary-color);
  color: #fff;
  border-color: var(--primary-color);
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
