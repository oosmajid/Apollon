<script setup>
import { ref, computed, onMounted } from 'vue'
import BaseTable from '@/components/BaseTable.vue'
import BaseModal from '@/components/BaseModal.vue'
import dayjs from 'dayjs'
import jalali from 'dayjs-jalali'
import api from '@/services/api'

dayjs.extend(jalali)
dayjs.locale('fa')

const terms = ref([])
const courses = ref([])
const assignmentFiles = ref([])

// Load data on mount
onMounted(async () => {
  try {
    const [termsRes, coursesRes, filesRes] = await Promise.all([
      api.getTerms(),
      api.getCourses(),
      api.getAssignmentFiles()
    ])
    terms.value = termsRes.data?.results || termsRes.data || []
    courses.value = coursesRes.data?.results || coursesRes.data || []
    assignmentFiles.value = filesRes.data?.results || filesRes.data || []
  } catch (error) {
    console.error("Failed to fetch data:", error)
  }
})

// --- وضعیت مودال‌ها ---
const showTermModal = ref(false)
const showDeleteModal = ref(false)
const isEditMode = ref(false)

// --- داده‌های ترم فعلی ---
const currentTerm = ref(null)

// Transform terms data for table display
const termsForTable = computed(() => {
  return terms.value.map(term => ({
    ...term,
    course: term.course?.name || '-',
    studentsCount: term.students_count || 0,
  }))
})

// --- توابع باز کردن مودال ---
function openAddModal() {
  isEditMode.value = false
  currentTerm.value = {
    name: '',
    course: courses.value.length > 0 ? courses.value[0].id : null,
    start_date: '',
    end_date: '',
    assignmentsDef: [],
    callsDef: [],
  }
  showTermModal.value = true
}

function openEditModal(term) {
  isEditMode.value = true
  const termCopy = JSON.parse(JSON.stringify(term))

  // تابع کمکی برای تبدیل تاریخ فارسی به فرمت استاندارد YYYY-MM-DD
  const formatToInputDate = (persianDate) => {
    if (!persianDate) return ''
    try {
      const persianMap = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
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
    course: termCopy.course?.id || termCopy.course,
    start_date: formatToInputDate(termCopy.start_date || termCopy.startDate),
    end_date: formatToInputDate(termCopy.end_date || termCopy.endDate),
    assignmentsDef: termCopy.assignment_defs || termCopy.assignmentsDef || [],
    callsDef: termCopy.call_defs || termCopy.callsDef || [],
  }
  showTermModal.value = true
}

// --- توابع مدیریت تکالیف ---
function addAssignment() {
  if (!currentTerm.value.assignmentsDef) {
    currentTerm.value.assignmentsDef = []
  }
  currentTerm.value.assignmentsDef.push({
    id: `new_a_${Date.now()}`,
    title: '',
    deadline: '',
    is_required: true,
    assignment_files: [],
  })
}

function removeAssignment(index) {
  currentTerm.value.assignmentsDef.splice(index, 1)
}

// --- توابع مدیریت تماس‌ها ---
function addCall() {
  if (!currentTerm.value.callsDef) {
    currentTerm.value.callsDef = []
  }
  currentTerm.value.callsDef.push({
    id: `new_c_${Date.now()}`,
    title: '',
    start_due_date: '',
    end_due_date: '',
  })
}

function removeCall(index) {
  currentTerm.value.callsDef.splice(index, 1)
}

// --- توابع ثبت و حذف ---
async function handleSubmit() {
  try {
    // آماده‌سازی داده‌ها برای ارسال
    const termData = {
      name: currentTerm.value.name,
      course: currentTerm.value.course,
      start_date: currentTerm.value.start_date,
      end_date: currentTerm.value.end_date,
    }

    let savedTerm
    if (isEditMode.value) {
      const response = await api.updateTerm(currentTerm.value.id, termData)
      savedTerm = response.data
      console.log('Term updated successfully')
    } else {
      const response = await api.createTerm(termData)
      savedTerm = response.data
      console.log('Term created successfully')
    }

    // ذخیره تکالیف
    if (currentTerm.value.assignmentsDef && currentTerm.value.assignmentsDef.length > 0) {
      for (const assignment of currentTerm.value.assignmentsDef) {
        const assignmentData = {
          term: savedTerm.id,
          title: assignment.title,
          deadline: assignment.deadline,
          is_required: assignment.is_required,
          assignment_files: assignment.assignment_files,
        }

        if (assignment.id && !assignment.id.toString().startsWith('new_')) {
          await api.updateAssignmentDef(assignment.id, assignmentData)
        } else if (assignment.title) {
          await api.createAssignmentDef(assignmentData)
        }
      }
    }

    // ذخیره تماس‌ها
    if (currentTerm.value.callsDef && currentTerm.value.callsDef.length > 0) {
      for (const call of currentTerm.value.callsDef) {
        const callData = {
          term: savedTerm.id,
          title: call.title,
          start_due_date: call.start_due_date,
          end_due_date: call.end_due_date,
        }

        if (call.id && !call.id.toString().startsWith('new_')) {
          await api.updateCallDef(call.id, callData)
        } else if (call.title) {
          await api.createCallDef(callData)
        }
      }
    }

    // Refresh terms data
    const response = await api.getTerms()
    terms.value = response.data?.results || response.data || []
    showTermModal.value = false
  } catch (error) {
    console.error('Failed to save term:', error)
    alert('خطا در ذخیره ترم. لطفاً دوباره تلاش کنید.')
  }
}

async function handleDeleteTerm() {
  try {
    await api.deleteTerm(currentTerm.value.id)
    console.log('Term deleted successfully')
    // Refresh terms data
    const response = await api.getTerms()
    terms.value = response.data?.results || response.data || []
    showDeleteModal.value = false
    showTermModal.value = false
  } catch (error) {
    console.error('Failed to delete term:', error)
    alert('خطا در حذف ترم. لطفاً دوباره تلاش کنید.')
  }
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

    <BaseTable :columns="tableColumns" :data="termsForTable" :rows-per-page="10">
      <template #cell-actions="{ item }">
        <button @click="openEditModal(item)" class="btn-sm">
          <i class="fa-solid fa-cogs"></i> ویرایش
        </button>
      </template>
    </BaseTable>

    <BaseModal :show="showTermModal" @close="showTermModal = false" size="xl">
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
          <select id="course-select" v-model="currentTerm.course" required>
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
              v-model="currentTerm.start_date"
              class="native-date-picker"
              required
            />
          </div>
          <div class="form-group">
            <label for="end-date">تاریخ پایان</label>
            <input
              type="date"
              id="end-date"
              v-model="currentTerm.end_date"
              class="native-date-picker"
              required
            />
          </div>
        </div>

        <!-- بخش تکالیف -->
        <div class="definition-section bg-soft">
          <div class="definition-header">
            <h4>تکالیف ترم</h4>
            <button @click="addAssignment" type="button" class="btn-sm btn-outline">
              <i class="fa-solid fa-plus"></i> افزودن تکلیف
            </button>
          </div>
          <div class="table-responsive">
            <table class="definition-table">
              <thead>
                <tr>
                  <th>عنوان تکلیف</th>
                  <th>مهلت ارسال</th>
                  <th>الزامی</th>
                  <th>فایل‌ها</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(assignment, index) in currentTerm.assignmentsDef"
                  :key="assignment.id"
                >
                  <td>
                    <input
                      type="text"
                      v-model="assignment.title"
                      placeholder="مثلا: تکلیف هفته اول"
                    />
                  </td>
                  <td>
                    <input
                      type="datetime-local"
                      v-model="assignment.deadline"
                    />
                  </td>
                  <td style="text-align: center;">
                    <input
                      type="checkbox"
                      v-model="assignment.is_required"
                    />
                  </td>
                  <td>
                    <select v-model="assignment.assignment_files" multiple style="min-height: 80px;">
                      <option v-for="file in assignmentFiles" :key="file.id" :value="file.id">
                        {{ file.title }}
                      </option>
                    </select>
                  </td>
                  <td>
                    <button
                      @click="removeAssignment(index)"
                      type="button"
                      class="btn-sm btn-icon-only btn-danger"
                      title="حذف تکلیف"
                    >
                      <i class="fa-solid fa-trash-can"></i>
                    </button>
                  </td>
                </tr>
                <tr
                  v-if="!currentTerm.assignmentsDef || currentTerm.assignmentsDef.length === 0"
                >
                  <td colspan="5" class="empty-state">هنوز تکلیفی تعریف نشده است.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- بخش تماس‌ها -->
        <div class="definition-section bg-soft">
          <div class="definition-header">
            <h4>تماس‌های ترم</h4>
            <button @click="addCall" type="button" class="btn-sm btn-outline">
              <i class="fa-solid fa-plus"></i> افزودن تماس
            </button>
          </div>
          <div class="table-responsive">
            <table class="definition-table">
              <thead>
                <tr>
                  <th>موضوع تماس</th>
                  <th>تاریخ شروع</th>
                  <th>تاریخ پایان</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(call, index) in currentTerm.callsDef" :key="call.id">
                  <td>
                    <input type="text" v-model="call.title" placeholder="مثلا: تماس هفته اول" />
                  </td>
                  <td>
                    <input
                      type="datetime-local"
                      v-model="call.start_due_date"
                    />
                  </td>
                  <td>
                    <input
                      type="datetime-local"
                      v-model="call.end_due_date"
                    />
                  </td>
                  <td>
                    <button
                      @click="removeCall(index)"
                      type="button"
                      class="btn-sm btn-icon-only btn-danger"
                      title="حذف تماس"
                    >
                      <i class="fa-solid fa-trash-can"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="!currentTerm.callsDef || currentTerm.callsDef.length === 0">
                  <td colspan="4" class="empty-state">هنوز تماسی تعریف نشده است.</td>
                </tr>
              </tbody>
            </table>
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

.definition-section {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 20px;
  margin-top: 20px;
}

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
.definition-table select,
.definition-table textarea {
  width: 100%;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background-color: var(--surface-color);
}

.definition-table td {
  min-width: 150px;
}

.definition-table td:last-child {
  width: 50px;
  min-width: 50px;
  text-align: center;
  vertical-align: middle;
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
