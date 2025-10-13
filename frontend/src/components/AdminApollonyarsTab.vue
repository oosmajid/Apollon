<script setup>
import { ref, computed, onMounted } from 'vue'
import BaseTable from '@/components/BaseTable.vue'
import BaseModal from '@/components/BaseModal.vue'
import api from '@/services/api'

const apollonyars = ref([])

// Load apollonyars data on mount
onMounted(async () => {
  try {
    const response = await api.getApollonyars()
    apollonyars.value = response.data
  } catch (error) {
    console.error("Failed to fetch apollonyars:", error)
  }
})

// Transform apollonyars data for table display
const apollonyarsForTable = computed(() => {
  return apollonyars.value.map(apollonyar => ({
    ...apollonyar,
    name: `${apollonyar.first_name || ''} ${apollonyar.last_name || ''}`.trim(),
    phone: apollonyar.phone_number,
    telegramId: apollonyar.telegram_id || '-',
    status: apollonyar.is_active ? 'آزاد' : 'مسدود',
    avgScore: apollonyar.avg_score || 0,
  }))
})

// --- وضعیت مودال‌ها ---
const showApollonyarModal = ref(false)
const showDeleteModal = ref(false)
const isEditMode = ref(false)

// --- داده‌های آپولون‌یار فعلی ---
const currentApollonyar = ref(null)

// --- توابع باز کردن مودال ---
function openAddModal() {
  isEditMode.value = false
  currentApollonyar.value = {
    name: '',
    phone: '',
    telegramId: '', // مقدار اولیه برای آیدی تلگرام
    status: 'آزاد', // مقدار پیش‌فرض
  }
  showApollonyarModal.value = true
}

function openEditModal(apollonyar) {
  isEditMode.value = true
  // کپی عمیق برای جلوگیری از تغییر ناخواسته
  currentApollonyar.value = JSON.parse(JSON.stringify(apollonyar))
  showApollonyarModal.value = true
}

// --- توابع ثبت و حذف ---
async function handleSubmit() {
  try {
    if (isEditMode.value) {
      await api.updateApollonyar(currentApollonyar.value.id, currentApollonyar.value)
      console.log('Apollonyar updated successfully')
    } else {
      await api.createApollonyar(currentApollonyar.value)
      console.log('Apollonyar created successfully')
    }
    // Refresh apollonyars data
    const response = await api.getApollonyars()
    apollonyars.value = response.data
    showApollonyarModal.value = false
  } catch (error) {
    console.error('Failed to save apollonyar:', error)
    alert('خطا در ذخیره آپولون‌یار. لطفاً دوباره تلاش کنید.')
  }
}

async function handleDelete() {
  try {
    await api.deleteApollonyar(currentApollonyar.value.id)
    console.log('Apollonyar deleted successfully')
    // Refresh apollonyars data
    const response = await api.getApollonyars()
    apollonyars.value = response.data
    showDeleteModal.value = false
    showApollonyarModal.value = false
  } catch (error) {
    console.error('Failed to delete apollonyar:', error)
    alert('خطا در حذف آپولون‌یار. لطفاً دوباره تلاش کنید.')
  }
}

const modalTitle = computed(() => {
  return isEditMode.value ? 'ویرایش آپولون‌یار' : 'افزودن آپولون‌یار جدید'
})

// تعریف ستون‌های جدید جدول
const tableColumns = [
  { key: 'name', label: 'نام و نام خانوادگی', sortable: true, filterable: true },
  { key: 'phone', label: 'شماره تلفن', sortable: false, filterable: true },
  { key: 'telegramId', label: 'آیدی تلگرام', sortable: true, filterable: true }, // ستون جدید
  { key: 'status', label: 'دسترسی', sortable: true, filterable: true },
  { key: 'avgScore', label: 'میانگین امتیاز', sortable: true, filterable: false },
  { key: 'actions', label: '', sortable: false, filterable: false },
]
</script>

<template>
  <div>
    <div class="pane-header">
      <h2>مدیریت آپولون‌یارها</h2>
      <button @click="openAddModal" class="btn">
        <i class="fa-solid fa-plus"></i> افزودن آپولون‌یار جدید
      </button>
    </div>

    <BaseTable :columns="tableColumns" :data="apollonyarsForTable" :rows-per-page="10">
      <template #cell-status="{ item }">
        <span
          class="status-bubble"
          :class="item.status === 'آزاد' ? 'status-active' : 'status-blocked'"
        >
          {{ item.status }}
        </span>
      </template>
      <template #cell-avgScore="{ item }">{{ item.avgScore }} ⭐</template>
      <template #cell-actions="{ item }">
        <button @click="openEditModal(item)" class="btn-sm">
          <i class="fa-solid fa-cogs"></i> ویرایش
        </button>
      </template>
    </BaseTable>

    <BaseModal :show="showApollonyarModal" @close="showApollonyarModal = false">
      <template #header>
        <h2>{{ modalTitle }}</h2>
      </template>

      <form v-if="currentApollonyar" @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label for="ap-name">نام و نام خانوادگی</label>
          <input type="text" id="ap-name" v-model="currentApollonyar.name" required />
        </div>

        <div class="form-group">
          <label for="ap-phone">شماره تلفن همراه</label>
          <input type="tel" id="ap-phone" v-model="currentApollonyar.phone" required />
        </div>

        <div class="form-group">
          <label for="ap-telegramId">آیدی تلگرام</label>
          <input type="text" id="ap-telegramId" v-model="currentApollonyar.telegramId" />
        </div>

        <div class="form-group-checkbox">
          <input
            type="checkbox"
            id="ap-status"
            :checked="currentApollonyar.status === 'مسدود'"
            @change="currentApollonyar.status = $event.target.checked ? 'مسدود' : 'آزاد'"
          />
          <label for="ap-status">مسدود شود</label>
        </div>

        <div class="modal-actions">
          <button
            v-if="isEditMode"
            @click.prevent="showDeleteModal = true"
            type="button"
            class="btn btn-danger-outline"
          >
            حذف آپولون‌یار
          </button>
          <div style="flex-grow: 1"></div>
          <button @click="showApollonyarModal = false" type="button" class="btn btn-outline">
            انصراف
          </button>
          <button type="submit" class="btn">{{ isEditMode ? 'ذخیره تغییرات' : 'ثبت' }}</button>
        </div>
      </form>
    </BaseModal>

    <BaseModal :show="showDeleteModal" @close="showDeleteModal = false">
      <template #header>
        <h2>تأیید حذف آپولون‌یار</h2>
      </template>
      <p v-if="currentApollonyar">آیا از حذف «{{ currentApollonyar.name }}» اطمینان دارید؟</p>
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

.status-bubble {
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}
.status-bubble.status-active {
  background-color: var(--success-bg);
  color: var(--success-text);
}
.status-bubble.status-blocked {
  background-color: #fee2e2;
  color: #b91c1c;
}

.modal-form .form-group {
  margin-bottom: 20px;
}
.modal-form .form-group-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}
.modal-form .form-group-checkbox label {
  cursor: pointer;
  margin-bottom: 0; /* ریست کردن مارجین پایین لیبل در حالت چک‌باکس */
}
.modal-form .form-group-checkbox input[type='checkbox'] {
  width: 18px; /* تنظیم اندازه چک‌باکس */
  height: 18px;
  cursor: pointer;
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
