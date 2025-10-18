<script setup>
import { ref, computed, onMounted } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import BaseTable from '@/components/BaseTable.vue'
import api from '@/services/api'

const assignmentFiles = ref([])

// Load assignment files data on mount
onMounted(async () => {
  console.log('[AdminAssignmentFilesTab] Mounting component...')
  try {
    console.log('[AdminAssignmentFilesTab] Fetching assignment files...')
    const response = await api.getAssignmentFiles()
    console.log('[AdminAssignmentFilesTab] Response received:', response)
    console.log('[AdminAssignmentFilesTab] Response data:', response.data)

    // Check if response.data is paginated (has 'results' key) or direct array
    if (response.data && response.data.results) {
      assignmentFiles.value = response.data.results
      console.log('[AdminAssignmentFilesTab] Using paginated data, files count:', assignmentFiles.value.length)
    } else if (Array.isArray(response.data)) {
      assignmentFiles.value = response.data
      console.log('[AdminAssignmentFilesTab] Using direct array, files count:', assignmentFiles.value.length)
    } else {
      console.error('[AdminAssignmentFilesTab] Unexpected response format:', response.data)
      assignmentFiles.value = []
    }
  } catch (error) {
    console.error("[AdminAssignmentFilesTab] Failed to fetch assignment files:", error)
    console.error("[AdminAssignmentFilesTab] Error details:", error.response?.data || error.message)
  }
})

// --- وضعیت مودال‌ها ---
const showFileModal = ref(false)
const showDeleteModal = ref(false)
const isEditMode = ref(false)

// --- داده‌های فایل فعلی ---
const currentFile = ref(null)
const selectedFile = ref(null)

// Transform files data for table display
const filesForTable = computed(() => {
  return assignmentFiles.value.map(file => ({
    ...file,
    fileUrl: file.file,
    fileName: file.file ? file.file.split('/').pop() : '-',
  }))
})

// --- ستون‌های جدول اصلی ---
const tableColumns = [
  { key: 'title', label: 'عنوان فایل', sortable: true, filterable: true },
  { key: 'fileName', label: 'نام فایل', sortable: true, filterable: true },
  { key: 'description', label: 'توضیحات', sortable: false, filterable: false },
  { key: 'actions', label: '', sortable: false, filterable: false },
]

// --- توابع باز کردن مودال ---
function openAddModal() {
  isEditMode.value = false
  currentFile.value = {
    title: '',
    description: '',
    file: null,
  }
  selectedFile.value = null
  showFileModal.value = true
}

function openEditModal(file) {
  isEditMode.value = true
  currentFile.value = JSON.parse(JSON.stringify(file))
  selectedFile.value = null
  showFileModal.value = true
}

// --- مدیریت فایل ---
function handleFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    console.log('File selected:', file.name)
  }
}

// --- توابع ثبت و حذف ---
async function handleSubmit() {
  try {
    // اگر عنوان خالی است، خطا بده
    if (!currentFile.value.title || currentFile.value.title.trim() === '') {
      alert('لطفاً عنوان فایل را وارد کنید.')
      return
    }

    // در حالت افزودن، فایل الزامی است
    if (!isEditMode.value && !selectedFile.value) {
      alert('لطفاً یک فایل انتخاب کنید.')
      return
    }

    // ایجاد FormData برای آپلود فایل
    const formData = new FormData()
    formData.append('title', currentFile.value.title)
    if (currentFile.value.description) {
      formData.append('description', currentFile.value.description)
    }

    // اگر فایل جدیدی انتخاب شده، اضافه کن
    if (selectedFile.value) {
      formData.append('file', selectedFile.value)
    }

    if (isEditMode.value) {
      await api.updateAssignmentFile(currentFile.value.id, formData)
      console.log('Assignment file updated successfully')
    } else {
      await api.createAssignmentFile(formData)
      console.log('Assignment file created successfully')
    }

    // Refresh files data
    const response = await api.getAssignmentFiles()
    assignmentFiles.value = response.data?.results || response.data || []
    showFileModal.value = false
  } catch (error) {
    console.error('Failed to save assignment file:', error)
    if (error.response?.data?.title) {
      alert(`خطا: ${error.response.data.title[0]}`)
    } else {
      alert('خطا در ذخیره فایل. لطفاً دوباره تلاش کنید.')
    }
  }
}

async function handleDeleteFile() {
  try {
    await api.deleteAssignmentFile(currentFile.value.id)
    console.log('Assignment file deleted successfully')
    // Refresh files data
    const response = await api.getAssignmentFiles()
    assignmentFiles.value = response.data?.results || response.data || []
    showDeleteModal.value = false
    showFileModal.value = false
  } catch (error) {
    console.error('Failed to delete assignment file:', error)
    alert('خطا در حذف فایل. لطفاً دوباره تلاش کنید.')
  }
}

const modalTitle = computed(() => {
  return isEditMode.value ? 'ویرایش فایل تکلیف' : 'افزودن فایل تکلیف جدید'
})
</script>

<template>
  <div>
    <div class="pane-header">
      <h2>مدیریت فایل‌های تکالیف</h2>
      <button @click="openAddModal" class="btn">
        <i class="fa-solid fa-plus"></i> افزودن فایل جدید
      </button>
    </div>

    <BaseTable :columns="tableColumns" :data="filesForTable" :rows-per-page="10">
      <template #cell-description="{ item }">
        <span class="description-text">{{ item.description || '-' }}</span>
      </template>
      <template #cell-actions="{ item }">
        <button @click="openEditModal(item)" class="btn-sm">
          <i class="fa-solid fa-cogs"></i> ویرایش
        </button>
      </template>
    </BaseTable>

    <BaseModal :show="showFileModal" @close="showFileModal = false" size="lg">
      <template #header>
        <h2>{{ modalTitle }}</h2>
      </template>

      <div v-if="currentFile" class="file-form">
        <div class="form-group">
          <label for="file-title">عنوان فایل <span class="required">*</span></label>
          <input
            type="text"
            id="file-title"
            v-model="currentFile.title"
            required
            class="form-control"
            placeholder="مثلاً: فایل راهنمای تکلیف هفته اول"
          />
          <small class="form-hint">عنوان باید یکتا باشد</small>
        </div>

        <div class="form-group">
          <label for="file-description">توضیحات</label>
          <textarea
            id="file-description"
            v-model="currentFile.description"
            class="form-control"
            rows="3"
            placeholder="توضیحات اختیاری در مورد این فایل..."
          ></textarea>
        </div>

        <div class="form-group">
          <label for="file-upload">
            فایل
            <span v-if="!isEditMode" class="required">*</span>
            <span v-else class="optional">(اختیاری برای ویرایش)</span>
          </label>
          <input
            type="file"
            id="file-upload"
            @change="handleFileChange"
            class="form-control"
            accept=".pdf,.doc,.docx,.txt,.zip,.rar"
          />
          <small class="form-hint">
            فرمت‌های مجاز: PDF, Word, Text, ZIP, RAR
          </small>
          <div v-if="selectedFile" class="selected-file-info">
            <i class="fa-solid fa-file"></i>
            <span>{{ selectedFile.name }}</span>
            <span class="file-size">({{ (selectedFile.size / 1024).toFixed(2) }} KB)</span>
          </div>
          <div v-else-if="isEditMode && currentFile.file" class="current-file-info">
            <i class="fa-solid fa-file"></i>
            <span>فایل فعلی: {{ currentFile.file.split('/').pop() }}</span>
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
          حذف فایل
        </button>
        <div style="flex-grow: 1"></div>
        <button @click="showFileModal = false" type="button" class="btn btn-outline">
          انصراف
        </button>
        <button @click="handleSubmit" type="submit" class="btn">
          {{ isEditMode ? 'ذخیره تغییرات' : 'ثبت فایل' }}
        </button>
      </div>
    </BaseModal>

    <BaseModal :show="showDeleteModal" @close="showDeleteModal = false">
      <template #header>
        <h2>تأیید حذف فایل</h2>
      </template>
      <p v-if="currentFile">
        آیا از حذف فایل «{{ currentFile.title }}» اطمینان دارید؟ این عملیات غیرقابل بازگشت است.
      </p>
      <div class="modal-actions">
        <button @click="showDeleteModal = false" class="btn btn-outline">انصراف</button>
        <button @click="handleDeleteFile" class="btn btn-danger">بله، حذف کن</button>
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

.file-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: var(--text-secondary);
  font-weight: 500;
}

.form-group .required {
  color: var(--danger-color);
}

.form-group .optional {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: normal;
}

.form-group .form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
  font-family: 'Vazirmatn', sans-serif;
  color: var(--text-primary);
}

.form-group textarea.form-control {
  resize: vertical;
  min-height: 80px;
}

.form-hint {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.selected-file-info,
.current-file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background-color: var(--surface-color);
  border-radius: 6px;
  margin-top: 8px;
  color: var(--text-primary);
}

.file-size {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.description-text {
  display: block;
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
