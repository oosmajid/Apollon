<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '@/stores/dataStore.js'
import BaseTable from '@/components/BaseTable.vue'
import BaseModal from '@/components/BaseModal.vue'
import dayjs from 'dayjs'
import jalali from 'dayjs-jalali'

// فعال‌سازی پلاگین جلالی برای کار با تاریخ‌ها
dayjs.extend(jalali)
dayjs.locale('fa')

const dataStore = useDataStore()

// --- وضعیت مودال‌ها ---
const showTermModal = ref(false)
const showDeleteModal = ref(false)
const isEditMode = ref(false)

// --- داده‌های ترم فعلی ---
const currentTerm = ref(null)

// --- لیست دوره‌ها برای دراپ‌다운 ---
const courses = computed(() => dataStore.courses)

// --- توابع باز کردن مودال ---
function openAddModal() {
  isEditMode.value = false
  currentTerm.value = {
    name: '',
    courseId: courses.value.length > 0 ? courses.value[0].id : '',
    startDate: '',
    endDate: '',
  }
  showTermModal.value = true
}

function openEditModal(term) {
  isEditMode.value = true
  // کپی عمیق برای جلوگیری از تغییر ناخواسته
  const termCopy = JSON.parse(JSON.stringify(term))

  // تابع کمکی برای تبدیل تاریخ فارسی به فرمت استاندارد YYYY-MM-DD
  const formatToInputDate = (persianDate) => {
    if (!persianDate) return ''
    try {
      const persianMap = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
      }
      const normalizedDate = String(persianDate).replace(/[۰-۹]/g, (d) => persianMap[d])
      const parsedDate = dayjs(normalizedDate, 'YYYY/MM/DD', 'fa')
      return parsedDate.isValid() ? parsedDate.format('YYYY-MM-DD') : ''
    } catch (e) {
      console.error('Date parsing error:', e)
      return ''
    }
  }

  currentTerm.value = {
    ...termCopy,
    startDate: formatToInputDate(termCopy.startDate),
    endDate: formatToInputDate(termCopy.endDate),
  }
  showTermModal.value = true
}

// --- توابع ثبت و حذف ---
function handleSubmit() {
  if (isEditMode.value) {
    console.log('Updating term:', currentTerm.value)
    // dataStore.updateTerm(currentTerm.value);
  } else {
    console.log('Adding new term:', currentTerm.value)
    // dataStore.addTerm(currentTerm.value);
  }
  showTermModal.value = false
}

function handleDeleteTerm() {
  console.log('Deleting term:', currentTerm.value.id)
  // dataStore.deleteTerm(currentTerm.value.id);
  showDeleteModal.value = false
  showTermModal.value = false
}

const modalTitle = computed(() => {
  return isEditMode.value ? 'ویرایش ترم' : 'افزودن ترم جدید'
})

// ستون‌های جدول
const tableColumns = [
  { key: 'name', label: 'نام ترم', sortable: true, filterable: true },
  { key: 'course', label: 'دوره', sortable: true, filterable: true },
  { key: 'startDate', label: 'تاریخ شروع', sortable: true, filterable: false },
  { key: 'endDate', label: 'تاریخ پایان', sortable: true, filterable: false },
  { key: 'studentsCount', label: 'هنرجویان', sortable: true, filterable: false },
  { key: 'actions', label: '', sortable: false, filterable: false },
]
</script>

<template>
  <div>
    <div class="pane-header">
      <h2>مدیریت ترم‌ها</h2>
      <button @click="openAddModal" class="btn">
        <i class="fa-solid fa-plus"></i> افزودن ترم جدید
      </button>
    </div>

    <BaseTable :columns="tableColumns" :data="dataStore.termsForTable" :rows-per-page="10">
      <template #cell-actions="{ item }">
        <button @click="openEditModal(item)" class="btn-sm">
          <i class="fa-solid fa-cogs"></i> ویرایش
        </button>
      </template>
    </BaseTable>

    <BaseModal :show="showTermModal" @close="showTermModal = false" size="lg">
      <template #header>
        <h2>{{ modalTitle }}</h2>
      </template>

      <form v-if="currentTerm" @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label for="term-name">نام ترم</label>
          <input type="text" id="term-name" v-model="currentTerm.name" required />
        </div>

        <div class="form-group">
          <label for="course-select">دوره</label>
          <select id="course-select" v-model="currentTerm.courseId" required>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.name }}
            </option>
          </select>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label for="start-date">تاریخ شروع</label>
            <input
              type="date"
              id="start-date"
              v-model="currentTerm.startDate"
              class="native-date-picker"
              required
            />
          </div>
          <div class="form-group">
            <label for="end-date">تاریخ پایان</label>
            <input
              type="date"
              id="end-date"
              v-model="currentTerm.endDate"
              class="native-date-picker"
              required
            />
          </div>
        </div>

        <div class="modal-actions">
          <button
            v-if="isEditMode"
            @click.prevent="showDeleteModal = true"
            type="button"
            class="btn btn-danger-outline"
          >
            حذف ترم
          </button>
          <div style="flex-grow: 1"></div>
          <button @click="showTermModal = false" type="button" class="btn btn-outline">
            انصراف
          </button>
          <button type="submit" class="btn">{{ isEditMode ? 'ذخیره تغییرات' : 'ثبت ترم' }}</button>
        </div>
      </form>
    </BaseModal>

    <BaseModal :show="showDeleteModal" @close="showDeleteModal = false">
      <template #header>
        <h2>تأیید حذف ترم</h2>
      </template>
      <p v-if="currentTerm">آیا از حذف ترم «{{ currentTerm.name }}» اطمینان دارید؟</p>
      <div class="modal-actions">
        <button @click="showDeleteModal = false" class="btn btn-outline">انصراف</button>
        <button @click="handleDeleteTerm" class="btn btn-danger">بله، حذف کن</button>
      </div>
    </BaseModal>
  </div>
</template>

<style scoped>
.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-form .form-group {
  margin-bottom: 20px;
}

.modal-form label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.modal-form input,
.modal-form select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
  font-family: 'Vazirmatn', sans-serif;
  color: var(--text-primary);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.native-date-picker {
  text-align: right;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 25px;
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}
.modal-actions .btn,
.modal-actions .btn-outline {
  width: auto;
  min-width: 100px;
}

.btn-outline {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.btn-outline:hover {
  background-color: var(--background-color);
}
.btn-danger-outline {
  background-color: transparent;
  border: 1px solid var(--danger-color);
  color: var(--danger-color);
}
.btn-danger-outline:hover {
  background-color: var(--danger-color);
  color: #fff;
}
.btn-danger {
  background-color: var(--danger-color);
  color: #fff;
}
</style>
