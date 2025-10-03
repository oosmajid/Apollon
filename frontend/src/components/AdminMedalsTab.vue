<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '@/stores/dataStore.js'
import BaseTable from '@/components/BaseTable.vue'
import BaseModal from '@/components/BaseModal.vue'

const dataStore = useDataStore()

// --- وضعیت مودال‌ها ---
const isStudentsModalOpen = ref(false)
const isDescriptionModalOpen = ref(false)
const showMedalModal = ref(false)
const showDeleteModal = ref(false)
const isEditMode = ref(false)

// --- داده‌های مدال ---
const selectedMedal = ref(null)
const currentMedal = ref(null)
const iconPreview = ref('')

function openStudentsModal(medal) {
  selectedMedal.value = medal
  isStudentsModalOpen.value = true
}

function openDescriptionModal(medal) {
  selectedMedal.value = medal
  isDescriptionModalOpen.value = true
}

function openAddModal() {
  isEditMode.value = false
  currentMedal.value = {
    name: '',
    description: '',
    icon: 'fa-solid fa-question-circle',
    iconFile: null,
  }
  iconPreview.value = ''
  showMedalModal.value = true
}

function openEditModal(medal) {
  isEditMode.value = true
  currentMedal.value = JSON.parse(JSON.stringify(medal))
  iconPreview.value = ''
  showMedalModal.value = true
}

function handleIconUpload(event) {
  const file = event.target.files[0]
  if (file) {
    currentMedal.value.iconFile = file
    const reader = new FileReader()
    reader.onload = (e) => {
      iconPreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

function handleSubmit() {
  if (isEditMode.value) {
    console.log('Updating Medal:', currentMedal.value)
  } else {
    console.log('Adding new Medal:', currentMedal.value)
  }
  showMedalModal.value = false
}

function handleDelete() {
  console.log('Deleting Medal:', currentMedal.value.id)
  showDeleteModal.value = false
  showMedalModal.value = false
}

const modalTitle = computed(() => {
  return isEditMode.value ? 'ویرایش مدال' : 'افزودن مدال جدید'
})

const tableColumns = [
  { key: 'name', label: 'نام مدال', sortable: true, filterable: true },
  { key: 'description', label: 'توضیحات', sortable: false, filterable: false },
  { key: 'holderCount', label: 'هنرجویان دارای مدال', sortable: true, filterable: false },
  { key: 'actions', label: '', sortable: false, filterable: false },
]

const studentTableColumns = [
  { key: 'name', label: 'نام هنرجو', sortable: true, filterable: true },
  { key: 'phone', label: 'شماره تلفن', sortable: false, filterable: true },
  { key: 'course', label: 'دوره', sortable: true, filterable: true },
  { key: 'term', label: 'ترم', sortable: true, filterable: true },
  { key: 'apollonyar', label: 'آپولون‌یار', sortable: true, filterable: true },
  { key: 'medalAwardDate', label: 'تاریخ دریافت', sortable: true, filterable: false },
]
</script>

<template>
  <div>
    <div class="pane-header">
      <h2>مدیریت مدال‌ها</h2>
      <button @click="openAddModal" class="btn">
        <i class="fa-solid fa-plus"></i> افزودن مدال جدید
      </button>
    </div>

    <BaseTable :columns="tableColumns" :data="dataStore.medalsForTable" :rows-per-page="10">
      <template #cell-name="{ item }">
        <i :class="item.icon" class="medal-icon"></i> {{ item.name }}
      </template>

      <template #cell-description="{ item }">
        <button @click="openDescriptionModal(item)" class="btn-sm btn-outline">
          <i class="fa-solid fa-eye"></i> مشاهده
        </button>
      </template>

      <template #cell-holderCount="{ item }">
        <div class="holder-count-cell">
          <span>{{ item.holderCount }}</span>
          <button
            @click="openStudentsModal(item)"
            class="btn-sm btn-icon-only btn-outline"
            title="مشاهده لیست"
          >
            <i class="fa-solid fa-users"></i>
          </button>
        </div>
      </template>

      <template #cell-actions="{ item }">
        <button @click="openEditModal(item)" class="btn-sm">
          <i class="fa-solid fa-cogs"></i> ویرایش
        </button>
      </template>
    </BaseTable>

    <BaseModal :show="isStudentsModalOpen" @close="isStudentsModalOpen = false" size="xl">
      <template #header>
        <h2 v-if="selectedMedal">هنرجویان دارای مدال «{{ selectedMedal.name }}»</h2>
      </template>
      <div v-if="selectedMedal">
        <BaseTable
          :columns="studentTableColumns"
          :data="selectedMedal.students"
          :rows-per-page="5"
        />
      </div>
    </BaseModal>

    <BaseModal :show="isDescriptionModalOpen" @close="isDescriptionModalOpen = false">
      <template #header>
        <h2 v-if="selectedMedal">توضیحات مدال «{{ selectedMedal.name }}»</h2>
      </template>
      <div v-if="selectedMedal">
        <p class="description-text">{{ selectedMedal.description }}</p>
      </div>
    </BaseModal>

    <BaseModal :show="showMedalModal" @close="showMedalModal = false">
      <template #header>
        <h2>{{ modalTitle }}</h2>
      </template>
      <form v-if="currentMedal" @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label for="medal-name">نام مدال</label>
          <input type="text" id="medal-name" v-model="currentMedal.name" required />
        </div>
        <div class="form-group">
          <label for="medal-desc">توضیحات مدال</label>
          <textarea id="medal-desc" v-model="currentMedal.description" rows="3" required></textarea>
        </div>
        <div class="form-group">
          <label>آیکون مدال</label>
          <div class="icon-uploader">
            <div class="icon-preview">
              <img v-if="iconPreview" :src="iconPreview" alt="Medal Icon Preview" />
              <i v-else :class="currentMedal.icon"></i>
            </div>
            <label for="icon-upload-input" class="btn btn-outline upload-btn">
              <i class="fa-solid fa-upload"></i> انتخاب آیکون
            </label>
            <input
              id="icon-upload-input"
              type="file"
              @change="handleIconUpload"
              accept="image/*"
              hidden
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
            حذف مدال
          </button>
          <div style="flex-grow: 1"></div>
          <button @click="showMedalModal = false" type="button" class="btn btn-outline">
            انصراف
          </button>
          <button type="submit" class="btn">{{ isEditMode ? 'ذخیره تغییرات' : 'ثبت' }}</button>
        </div>
      </form>
    </BaseModal>

    <BaseModal :show="showDeleteModal" @close="showDeleteModal = false">
      <template #header>
        <h2>تأیید حذف مدال</h2>
      </template>
      <p v-if="currentMedal">آیا از حذف مدال «{{ currentMedal.name }}» اطمینان دارید؟</p>
      <div class="modal-actions">
        <button @click="showDeleteModal = false" class="btn btn-outline">انصراف</button>
        <button @click="handleDelete" class="btn btn-danger">بله، حذف کن</button>
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
.medal-icon {
  color: var(--star-color);
  font-size: 1.2rem;
  margin-left: 8px;
  vertical-align: middle;
}

.holder-count-cell {
  display: flex;
  align-items: center;
  gap: 15px;
  justify-content: flex-start;
}
.btn-icon-only {
  padding: 0;
  width: 32px;
  height: 32px;
}
.btn-outline {
  background-color: transparent;
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
}
.btn-outline:hover {
  background-color: var(--primary-color);
  color: #fff;
}
.description-text {
  line-height: 1.8;
  text-align: justify;
  color: var(--text-secondary);
}

/* --- استایل‌های مودال --- */
.modal-form .form-group {
  margin-bottom: 20px;
}
.modal-form label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
}
.modal-form input,
.modal-form textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
  font-family: 'Vazirmatn', sans-serif;
  color: var(--text-primary);
}

/* --- استایل آپلودر آیکون --- */
.icon-uploader {
  display: flex;
  align-items: center;
  gap: 20px;
}
.icon-preview {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: var(--background-color);
  border: 2px dashed var(--border-color);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2rem;
  color: var(--primary-color);
  overflow: hidden;
  flex-shrink: 0;
}
.icon-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.upload-btn {
  height: 40px;
  padding: 0 16px !important;
  cursor: pointer;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px;
  line-height: 1 !important;
  vertical-align: middle !important;
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
