<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '@/stores/dataStore.js'
import BaseTable from '@/components/BaseTable.vue'
import BaseModal from '@/components/BaseModal.vue'

const dataStore = useDataStore()

// --- وضعیت‌های داخلی ---
const selectedStudentIds = ref([])
const isApollonyarModalOpen = ref(false)
const isGroupModalOpen = ref(false)
const isDeleteModalOpen = ref(false) // جدید: مودال حذف هنرجو
const studentToDelete = ref(null) // جدید: هنرجوی در حال حذف
const selectedApollonyarId = ref(null)
const selectedGroupId = ref(null)

// --- داده‌های computed ---
const tableColumns = [
  { key: 'name', label: 'نام هنرجو', sortable: true, filterable: true },
  { key: 'phone', label: 'شماره تلفن', sortable: false, filterable: true },
  { key: 'course', label: 'دوره', sortable: true, filterable: true },
  { key: 'term', label: 'ترم', sortable: true, filterable: true },
  { key: 'apollonyar', label: 'آپولون‌یار', sortable: true, filterable: true },
  { key: 'group', label: 'گروه', sortable: true, filterable: true },
  { key: 'actions', label: '', sortable: false, filterable: false, width: '100px' },
]

const hasSelection = computed(() => selectedStudentIds.value.length > 0)

// --- توابع ---
function openApollonyarModal() {
  selectedApollonyarId.value = null
  isApollonyarModalOpen.value = true
}

function openGroupModal() {
  selectedGroupId.value = null
  isGroupModalOpen.value = true
}

// جدید: باز کردن مودال تایید حذف
function openDeleteModal(student) {
  studentToDelete.value = student
  isDeleteModalOpen.value = true
}

// جدید: اجرای حذف هنرجو
function confirmDeleteStudent() {
  if (studentToDelete.value) {
    dataStore.removeStudent(studentToDelete.value.id)
  }
  isDeleteModalOpen.value = false
  studentToDelete.value = null
}

function assignApollonyar() {
  // این تابع نیازی به تغییر ندارد
  dataStore.assignApollonyarToStudents(selectedStudentIds.value, selectedApollonyarId.value)
  selectedStudentIds.value = []
  isApollonyarModalOpen.value = false
}

// جدید: حذف تخصیص آپولون‌یار
function unassignApollonyar() {
  dataStore.assignApollonyarToStudents(selectedStudentIds.value, null)
  selectedStudentIds.value = []
  isApollonyarModalOpen.value = false
}

function assignGroup() {
  // این تابع نیازی به تغییر ندارد
  dataStore.assignGroupToStudents(selectedStudentIds.value, selectedGroupId.value)
  selectedStudentIds.value = []
  isGroupModalOpen.value = false
}

// جدید: حذف تخصیص گروه
function unassignGroup() {
  dataStore.assignGroupToStudents(selectedStudentIds.value, null)
  selectedStudentIds.value = []
  isGroupModalOpen.value = false
}
</script>

<template>
  <div>
    <div class="pane-header">
      <h2>مدیریت هنرجویان</h2>
      <div class="actions-group">
        <button class="btn-sm btn-outline" :disabled="!hasSelection" @click="openGroupModal">
          <i class="fa-solid fa-users-rectangle"></i> تغییر گروه
        </button>
        <button class="btn-sm btn-outline" :disabled="!hasSelection" @click="openApollonyarModal">
          <i class="fa-solid fa-user-astronaut"></i> تغییر آپولون‌یار
        </button>
        <span v-if="hasSelection" class="selection-count">
          {{ selectedStudentIds.length }} هنرجو انتخاب شده
        </span>
      </div>
    </div>

    <BaseTable
      :columns="tableColumns"
      :data="dataStore.studentsWithDetails"
      :rows-per-page="50"
      v-model="selectedStudentIds"
      selectable
    >
      <template #cell-actions="{ item }">
        <div class="action-buttons">
          <RouterLink
            :to="{ name: 'student-profile', params: { id: item.id } }"
            class="btn-sm btn-icon-only"
            title="مشاهده پروفایل"
          >
            <i class="fa-solid fa-user"></i>
          </RouterLink>
          <button
            @click="openDeleteModal(item)"
            class="btn-sm btn-icon-only btn-danger"
            title="حذف هنرجو"
          >
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>
      </template>
    </BaseTable>

    <BaseModal :show="isApollonyarModalOpen" @close="isApollonyarModalOpen = false">
      <template #header><h2>تخصیص آپولون‌یار</h2></template>
      <form @submit.prevent="assignApollonyar" class="modal-form">
        <div class="form-group">
          <label for="apollonyar-select">آپولون‌یار جدید را انتخاب کنید</label>
          <select id="apollonyar-select" v-model="selectedApollonyarId">
            <option :value="null" disabled>یک آپولون‌یار انتخاب کنید...</option>
            <option v-for="ap in dataStore.apollonyars" :key="ap.id" :value="ap.id">
              {{ ap.name }}
            </option>
          </select>
        </div>
        <div class="modal-actions">
          <button @click="unassignApollonyar" type="button" class="btn btn-danger-outline">
            حذف آپولون‌یار فعلی
          </button>
          <div class="spacer"></div>
          <button @click="isApollonyarModalOpen = false" type="button" class="btn btn-outline">
            انصراف
          </button>
          <button type="submit" class="btn">ثبت تغییرات</button>
        </div>
      </form>
    </BaseModal>

    <BaseModal :show="isGroupModalOpen" @close="isGroupModalOpen = false">
      <template #header><h2>تخصیص گروه</h2></template>
      <form @submit.prevent="assignGroup" class="modal-form">
        <div class="form-group">
          <label for="group-select">گروه جدید را انتخاب کنید</label>
          <select id="group-select" v-model="selectedGroupId">
            <option :value="null" disabled>یک گروه انتخاب کنید...</option>
            <option v-for="group in dataStore.groups" :key="group.id" :value="group.id">
              {{ group.name }}
            </option>
          </select>
        </div>
        <div class="modal-actions">
          <button @click="unassignGroup" type="button" class="btn btn-danger-outline">
            حذف گروه فعلی
          </button>
          <div class="spacer"></div>
          <button @click="isGroupModalOpen = false" type="button" class="btn btn-outline">
            انصراف
          </button>
          <button type="submit" class="btn">ثبت تغییرات</button>
        </div>
      </form>
    </BaseModal>

    <BaseModal :show="isDeleteModalOpen" @close="isDeleteModalOpen = false">
      <template #header><h2>تأیید حذف هنرجو</h2></template>
      <p v-if="studentToDelete">
        آیا از حذف هنرجو «{{ studentToDelete.name }}» اطمینان دارید؟ این عمل قابل بازگشت نیست.
      </p>
      <div class="modal-actions">
        <button @click="isDeleteModalOpen = false" class="btn btn-outline">انصراف</button>
        <button @click="confirmDeleteStudent" class="btn btn-danger">بله، حذف کن</button>
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
.actions-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.selection-count {
  font-size: 0.9rem;
  color: var(--text-secondary);
}
.btn-outline:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-buttons {
  display: flex;
  gap: 8px;
}
.btn-icon-only {
  width: 32px;
  height: 32px;
  padding: 0;
  font-size: 1rem;
}
.btn-icon-only.btn-danger {
  background-color: transparent;
  color: var(--danger-color);
  border: 1px solid var(--danger-color);
}
.btn-icon-only.btn-danger:hover {
  background-color: var(--danger-color);
  color: #fff;
}

/* استایل‌های مودال */
.modal-form .form-group {
  margin-bottom: 20px;
}
.modal-form label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
}
.modal-form select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
}
.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}
.modal-actions .spacer {
  flex-grow: 1;
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
}
.btn-outline {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.btn-outline:hover {
  background-color: var(--background-color);
}
</style>
