<script setup>
import { ref, computed, onMounted } from 'vue'
import BaseTable from '@/components/BaseTable.vue'
import BaseModal from '@/components/BaseModal.vue'
import api from '@/services/api'

const groups = ref([])

// Load groups data on mount
onMounted(async () => {
  try {
    const response = await api.getGroups()
    groups.value = response.data
  } catch (error) {
    console.error("Failed to fetch groups:", error)
  }
})

// --- وضعیت مودال‌ها ---
const showGroupModal = ref(false)
const showDeleteModal = ref(false)
const isEditMode = ref(false)

// --- داده‌های گروه فعلی ---
const currentGroup = ref(null)

// --- توابع باز کردن مودال ---
function openAddModal() {
  isEditMode.value = false
  currentGroup.value = {
    name: '',
  }
  showGroupModal.value = true
}

function openEditModal(group) {
  isEditMode.value = true
  // کپی عمیق برای جلوگیری از تغییر ناخواسته
  currentGroup.value = JSON.parse(JSON.stringify(group))
  showGroupModal.value = true
}

// --- توابع ثبت و حذف ---
async function handleSubmit() {
  try {
    if (isEditMode.value) {
      await api.updateGroup(currentGroup.value.id, currentGroup.value)
      console.log('Group updated successfully')
    } else {
      await api.createGroup(currentGroup.value)
      console.log('Group created successfully')
    }
    // Refresh groups data
    const response = await api.getGroups()
    groups.value = response.data
    showGroupModal.value = false
  } catch (error) {
    console.error('Failed to save group:', error)
    alert('خطا در ذخیره گروه. لطفاً دوباره تلاش کنید.')
  }
}

async function handleDelete() {
  try {
    await api.deleteGroup(currentGroup.value.id)
    console.log('Group deleted successfully')
    // Refresh groups data
    const response = await api.getGroups()
    groups.value = response.data
    showDeleteModal.value = false
    showGroupModal.value = false
  } catch (error) {
    console.error('Failed to delete group:', error)
    alert('خطا در حذف گروه. لطفاً دوباره تلاش کنید.')
  }
}

const modalTitle = computed(() => {
  return isEditMode.value ? 'ویرایش گروه' : 'افزودن گروه جدید'
})

// تعریف ستون‌های جدید جدول
const tableColumns = [
  { key: 'name', label: 'نام گروه', sortable: true, filterable: true },
  { key: 'studentCount', label: 'تعداد هنرجویان', sortable: true, filterable: false },
  { key: 'actions', label: '', sortable: false, filterable: false },
]
</script>

<template>
  <div>
    <div class="pane-header">
      <h2>مدیریت گروه‌ها</h2>
      <button @click="openAddModal" class="btn">
        <i class="fa-solid fa-plus"></i> افزودن گروه جدید
      </button>
    </div>

    <BaseTable :columns="tableColumns" :data="groups" :rows-per-page="10">
      <template #cell-actions="{ item }">
        <button @click="openEditModal(item)" class="btn-sm">
          <i class="fa-solid fa-cogs"></i> ویرایش
        </button>
      </template>
    </BaseTable>

    <BaseModal :show="showGroupModal" @close="showGroupModal = false">
      <template #header>
        <h2>{{ modalTitle }}</h2>
      </template>

      <form v-if="currentGroup" @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label for="group-name">نام گروه</label>
          <input type="text" id="group-name" v-model="currentGroup.name" required />
        </div>

        <div class="modal-actions">
          <button
            v-if="isEditMode"
            @click.prevent="showDeleteModal = true"
            type="button"
            class="btn btn-danger-outline"
          >
            حذف گروه
          </button>
          <div style="flex-grow: 1"></div>
          <button @click="showGroupModal = false" type="button" class="btn btn-outline">
            انصراف
          </button>
          <button type="submit" class="btn">{{ isEditMode ? 'ذخیره تغییرات' : 'ثبت' }}</button>
        </div>
      </form>
    </BaseModal>

    <BaseModal :show="showDeleteModal" @close="showDeleteModal = false">
      <template #header>
        <h2>تأیید حذف گروه</h2>
      </template>
      <p v-if="currentGroup">آیا از حذف گروه «{{ currentGroup.name }}» اطمینان دارید؟</p>
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

.modal-form .form-group {
  margin-bottom: 20px;
}

.modal-form label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.modal-form input {
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
