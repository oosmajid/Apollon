<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '@/stores/dataStore.js'
import BaseModal from '@/components/BaseModal.vue'
import BaseTable from '@/components/BaseTable.vue'

const dataStore = useDataStore()

// --- وضعیت مودال‌ها ---
const showCourseModal = ref(false)
const showDeleteModal = ref(false)
const isEditMode = ref(false)

// --- داده‌های دوره فعلی ---
const currentCourse = ref(null)

// --- ستون‌های جدول اصلی ---
const tableColumns = [
  { key: 'name', label: 'نام دوره', sortable: true, filterable: true },
  { key: 'totalStudents', label: 'تعداد کل هنرجویان', sortable: true, filterable: false },
  { key: 'graduates', label: 'تعداد فارغ‌التحصیلان', sortable: true, filterable: false },
  { key: 'assignmentCount', label: 'تعداد تکالیف', sortable: true, filterable: false },
  { key: 'callCount', label: 'تعداد تماس‌ها', sortable: true, filterable: false },
  { key: 'actions', label: '', sortable: false, filterable: false },
]

// --- توابع باز کردن مودال ---
function openAddModal() {
  isEditMode.value = false
  currentCourse.value = {
    name: '',
    assignmentsDef: [],
    callsDef: [],
  }
  showCourseModal.value = true
}

function openEditModal(course) {
  isEditMode.value = true
  currentCourse.value = JSON.parse(JSON.stringify(course))
  showCourseModal.value = true
}

// --- توابع مدیریت تکالیف و تماس‌ها در مودال ---
function addAssignment() {
  if (!currentCourse.value.assignmentsDef) {
    currentCourse.value.assignmentsDef = []
  }
  currentCourse.value.assignmentsDef.push({
    id: `new_a_${Date.now()}`,
    title: '',
    description: '',
    files: [],
  })
}

function removeAssignment(index) {
  currentCourse.value.assignmentsDef.splice(index, 1)
}

// تابع جدید برای مدیریت فایل‌ها (نمونه)
function handleFileUpload(event, assignment) {
  const files = event.target.files
  assignment.files = Array.from(files) // ذخیره فایل‌ها در آبجکت تکلیف
  console.log(`Uploaded ${files.length} files for assignment:`, assignment.title)
}

function addCall() {
  if (!currentCourse.value.callsDef) {
    currentCourse.value.callsDef = []
  }
  currentCourse.value.callsDef.push({ id: `new_c_${Date.now()}`, topic: '', description: '' })
}

function removeCall(index) {
  currentCourse.value.callsDef.splice(index, 1)
}

// --- توابع ثبت و حذف ---
function handleSubmit() {
  if (isEditMode.value) {
    console.log('Updating course:', currentCourse.value)
  } else {
    console.log('Adding new course:', currentCourse.value)
  }
  showCourseModal.value = false
}

function handleDeleteCourse() {
  console.log('Deleting course:', currentCourse.value.id)
  showDeleteModal.value = false
  showCourseModal.value = false
}

const modalTitle = computed(() => {
  return isEditMode.value ? 'ویرایش دوره' : 'افزودن دوره جدید'
})
</script>

<template>
  <div>
    <div class="pane-header">
      <h2>مدیریت دوره‌ها</h2>
      <button @click="openAddModal" class="btn">
        <i class="fa-solid fa-plus"></i> افزودن دوره جدید
      </button>
    </div>

    <BaseTable :columns="tableColumns" :data="dataStore.coursesForTable" :rows-per-page="10">
      <template #cell-actions="{ item }">
        <button @click="openEditModal(item)" class="btn-sm">
          <i class="fa-solid fa-cogs"></i> ویرایش
        </button>
      </template>
    </BaseTable>

    <BaseModal :show="showCourseModal" @close="showCourseModal = false" size="xl">
      <template #header>
        <h2>{{ modalTitle }}</h2>
      </template>

      <div v-if="currentCourse" class="course-form-grid">
        <div class="form-group">
          <label for="course-name">نام دوره</label>
          <input
            type="text"
            id="course-name"
            v-model="currentCourse.name"
            required
            class="form-control"
          />
        </div>

        <div class="definition-section bg-soft">
          <div class="definition-header">
            <h4>تکالیف دوره</h4>
            <button @click="addAssignment" class="btn-sm btn-outline">
              <i class="fa-solid fa-plus"></i> افزودن تکلیف
            </button>
          </div>
          <div class="table-responsive">
            <table class="definition-table">
              <thead>
                <tr>
                  <th>نام تکلیف</th>
                  <th>توضیحات</th>
                  <th>فایل‌های الگو</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(assignment, index) in currentCourse.assignmentsDef"
                  :key="assignment.id"
                >
                  <td>
                    <input
                      type="text"
                      v-model="assignment.title"
                      placeholder="مثلا: کار با لایه‌ها"
                    />
                  </td>
                  <td>
                    <textarea
                      v-model="assignment.description"
                      rows="2"
                      placeholder="توضیحات برای هنرجو"
                    ></textarea>
                  </td>
                  <td>
                    <div class="file-upload-wrapper">
                      <label
                        :for="`file-upload-${index}`"
                        class="btn-sm btn-icon-only"
                        title="آپلود فایل"
                      >
                        <i class="fa-solid fa-upload"></i>
                      </label>
                      <input
                        type="file"
                        :id="`file-upload-${index}`"
                        @change="handleFileUpload($event, assignment)"
                        multiple
                        hidden
                      />
                      <span>({{ (assignment.files && assignment.files.length) || 0 }} فایل)</span>
                    </div>
                  </td>
                  <td>
                    <button
                      @click="removeAssignment(index)"
                      class="btn-sm btn-icon-only btn-danger"
                      title="حذف تکلیف"
                    >
                      <i class="fa-solid fa-trash-can"></i>
                    </button>
                  </td>
                </tr>
                <tr
                  v-if="!currentCourse.assignmentsDef || currentCourse.assignmentsDef.length === 0"
                >
                  <td colspan="4" class="empty-state">هنوز تکلیفی تعریف نشده است.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="definition-section bg-soft">
          <div class="definition-header">
            <h4>تماس‌های دوره</h4>
            <button @click="addCall" class="btn-sm btn-outline">
              <i class="fa-solid fa-plus"></i> افزودن تماس
            </button>
          </div>
          <div class="table-responsive">
            <table class="definition-table">
              <thead>
                <tr>
                  <th>موضوع تماس</th>
                  <th>توضیحات داخلی</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(call, index) in currentCourse.callsDef" :key="call.id">
                  <td>
                    <input type="text" v-model="call.topic" placeholder="مثلا: تماس هفته اول" />
                  </td>
                  <td>
                    <textarea
                      v-model="call.description"
                      rows="2"
                      placeholder="یادآوری برای آپولون‌یار"
                    ></textarea>
                  </td>
                  <td>
                    <button
                      @click="removeCall(index)"
                      class="btn-sm btn-icon-only btn-danger"
                      title="حذف تماس"
                    >
                      <i class="fa-solid fa-trash-can"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="!currentCourse.callsDef || currentCourse.callsDef.length === 0">
                  <td colspan="3" class="empty-state">هنوز تماسی تعریف نشده است.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="modal-actions">
        <button
          v-if="isEditMode"
          @click="showDeleteModal = true"
          type="button"
          class="btn btn-danger-outline"
        >
          حذف دوره
        </button>
        <div style="flex-grow: 1"></div>
        <button @click="showCourseModal = false" type="button" class="btn btn-outline">
          انصراف
        </button>
        <button @click="handleSubmit" type="submit" class="btn">
          {{ isEditMode ? 'ذخیره تغییرات' : 'ثبت دوره' }}
        </button>
      </div>
    </BaseModal>

    <BaseModal :show="showDeleteModal" @close="showDeleteModal = false">
      <template #header>
        <h2>تأیید حذف دوره</h2>
      </template>
      <p v-if="currentCourse">
        آیا از حذف دوره «{{ currentCourse.name }}» اطمینان دارید؟ تمام اطلاعات مرتبط با این دوره
        برای همیشه پاک خواهد شد.
      </p>
      <div class="modal-actions">
        <button @click="showDeleteModal = false" class="btn btn-outline">انصراف</button>
        <button @click="handleDeleteCourse" class="btn btn-danger">بله، حذف کن</button>
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

.course-form-grid {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-group .form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
  font-family: 'Vazirmatn', sans-serif;
}

.definition-section {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 20px;
}

/* استایل جدید برای پس‌زمینه */
.bg-soft {
  background-color: var(--background-color);
}

.definition-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.definition-header h4 {
  margin: 0;
}

.table-responsive {
  overflow-x: auto;
}

.definition-table {
  width: 100%;
  border-collapse: collapse;
}
.definition-table th,
.definition-table td {
  padding: 10px;
  text-align: right;
  vertical-align: top;
  border-bottom: 1px solid var(--border-color);
}
.definition-table thead th {
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
  background-color: var(--surface-color);
}
.definition-table input,
.definition-table textarea {
  width: 100%;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background-color: var(--surface-color); /* تغییر برای کنتراست بهتر */
}
.definition-table td {
  min-width: 200px;
}
.definition-table td:last-child {
  width: 50px;
  min-width: 50px;
  text-align: center;
  vertical-align: middle;
}

.file-upload-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}
.file-upload-wrapper label {
  cursor: pointer;
}
.file-upload-wrapper span {
  font-size: 0.8rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.empty-state {
  text-align: center;
  color: var(--text-secondary);
  padding: 20px !important;
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
.btn-icon-only {
  width: 32px;
  height: 32px;
  padding: 0;
  font-size: 1rem;
}
.btn-icon-only.btn-danger {
  background-color: transparent;
  color: var(--danger-color);
}
.btn-icon-only.btn-danger:hover {
  background-color: var(--danger-color);
  color: #fff;
}
</style>
