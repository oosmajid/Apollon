<script setup>
import { useDataStore } from '@/stores/dataStore.js'
import BaseTable from '@/components/BaseTable.vue'
import AssignmentStatusIcons from '@/components/AssignmentStatusIcons.vue'
import { onMounted, ref } from 'vue'
import { useLayoutStore } from '@/stores/layout.js'
import HeartRating from '@/components/HeartRating.vue'
import BaseModal from '@/components/BaseModal.vue'
import anonymousAvatar from '@/assets/avatar-anonymous.svg'

const layoutStore = useLayoutStore()
const dataStore = useDataStore()
onMounted(() => {
  layoutStore.setPageTitle('کل هنرجویان')
})

// --- منطق مودال افزودن هنرجو ---
const isAddModalOpen = ref(false)
const newStudent = ref({
  name: '',
  phone: '',
  birthYear: '',
  city: '',
})

function openAddStudentModal() {
  newStudent.value = { name: '', phone: '', birthYear: '', city: '' }
  isAddModalOpen.value = true
}

function handleAddStudent() {
  if (newStudent.value.name && newStudent.value.phone) {
    dataStore.addStudent(newStudent.value)
    isAddModalOpen.value = false
  } else {
    alert('لطفاً نام و شماره تلفن را وارد کنید.')
  }
}

const tableColumns = [
  { key: 'actions', label: '', sortable: false, filterable: false },
  { key: 'name', label: 'نام هنرجو', sortable: true, filterable: true },
  { key: 'phone', label: 'شماره تلفن', sortable: false, filterable: true },
  { key: 'course', label: 'دوره', sortable: true, filterable: true },
  { key: 'term', label: 'ترم', sortable: true, filterable: true },
  { key: 'apollonyar', label: 'آپولون‌یار', sortable: true, filterable: true },
  { key: 'assignmentStatus', label: 'وضعیت تکالیف', sortable: false, filterable: false },
  { key: 'daysSinceLastContact', label: 'آخرین تماس (روز)', sortable: true, filterable: false },
  { key: 'accountStatus', label: 'وضعیت', sortable: true, filterable: true },
  { key: 'studentType', label: 'نوع', sortable: true, filterable: true },
  { key: 'enrollmentStatus', label: 'حضور', sortable: true, filterable: true },
  { key: 'accessStatus', label: 'دسترسی', sortable: true, filterable: true },
  { key: 'watchTime', label: 'مشاهده دوره', sortable: true, filterable: false },
  { key: 'hearts', label: 'جان', sortable: true, filterable: false },
  { key: 'score', label: 'امتیاز', sortable: true, filterable: false },
]
</script>

<template>
  <div class="view-container">
    <div class="view-header">
      <button @click="openAddStudentModal" class="btn">
        <i class="fa-solid fa-user-plus"></i> افزودن هنرجوی جدید
      </button>
    </div>

    <BaseTable :columns="tableColumns" :data="dataStore.studentsWithDetails" :rows-per-page="15">
      <template #cell-actions="{ item }">
        <RouterLink
          :to="{ name: 'student-profile', params: { id: item.id } }"
          class="btn-sm btn-icon-only"
          title="مشاهده پروفایل"
        >
          <i class="fa-solid fa-user"></i>
        </RouterLink>
      </template>
      <template #cell-assignmentStatus="{ item }">
        <AssignmentStatusIcons :statuses="item.assignmentStatus" />
      </template>
      <template #cell-hearts="{ item }">
        <HeartRating :count="item.hearts" />
      </template>
      <template #cell-score="{ item }">
        <div v-if="item.score" class="score-cell">
          <span>{{ item.score }}</span>
          <i class="fa-solid fa-star score-icon"></i>
        </div>
        <span v-else>-</span>
      </template>

      <template #cell-accountStatus="{ item }">
        <span class="status-bubble" :class="`status-${item.accountStatus}`">{{
          item.accountStatus
        }}</span>
      </template>
      <template #cell-studentType="{ item }">
        <span class="status-bubble type">{{ item.studentType }}</span>
      </template>
      <template #cell-enrollmentStatus="{ item }">
        <span class="status-bubble presence">{{ item.enrollmentStatus }}</span>
      </template>
      <template #cell-accessStatus="{ item }">
        <span
          class="status-bubble"
          :class="
            item.accessStatus && item.accessStatus.includes('فعال')
              ? 'access-active'
              : 'access-inactive'
          "
          >{{ item.accessStatus }}</span
        >
      </template>
    </BaseTable>
  </div>

  <BaseModal :show="isAddModalOpen" @close="isAddModalOpen = false">
    <template #header><h2>افزودن هنرجوی جدید</h2></template>
    <form @submit.prevent="handleAddStudent" class="modal-form profile-edit-form">
      <div class="form-group profile-image-editor">
        <img :src="anonymousAvatar" alt="عکس هنرجو" />
        <label for="profile-image-upload" class="edit-photo-btn">
          <i class="fa-solid fa-camera"></i>
          <input type="file" id="profile-image-upload" hidden />
        </label>
      </div>
      <div class="form-group">
        <label for="profile-name">نام و نام خانوادگی</label>
        <input type="text" id="profile-name" v-model="newStudent.name" required />
      </div>
      <div class="form-group">
        <label for="profile-phone">شماره تلفن</label>
        <input type="tel" id="profile-phone" v-model="newStudent.phone" required />
      </div>
      <div class="form-group">
        <label for="profile-birth-year">سال تولد</label>
        <input type="number" id="profile-birth-year" v-model="newStudent.birthYear" />
      </div>
      <div class="form-group">
        <label for="profile-city">شهر</label>
        <input type="text" id="profile-city" v-model="newStudent.city" />
      </div>
      <div class="modal-actions">
        <button
          @click="isAddModalOpen = false"
          type="button"
          class="btn-outline"
          style="min-width: 120px"
        >
          انصراف
        </button>
        <button type="submit" class="btn">ثبت هنرجو</button>
      </div>
    </form>
  </BaseModal>
</template>

<style scoped>
.view-container {
  padding-top: 20px;
}
.view-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}
.btn-icon-only {
  width: 32px;
  height: 32px;
  padding: 0;
  font-size: 1rem;
}

/* --- استایل‌های کپی شده از پروفایل برای مودال --- */
.modal-form .form-group {
  margin-bottom: 20px;
  text-align: right;
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
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}
.profile-edit-form {
  text-align: center;
}
.profile-image-editor {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 20px;
}
.profile-image-editor img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--border-color);
}
.edit-photo-btn {
  position: absolute;
  bottom: 0px;
  left: 0px;
  width: 36px;
  height: 36px;
  background-color: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition: background-color 0.2s;
  padding: 0;
}
.edit-photo-btn:hover {
  background-color: var(--primary-hover);
}
.edit-photo-btn i {
  color: #fff;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  line-height: 1;
}
.score-cell {
  display: flex;
  align-items: center;
  gap: 5px;
}
.score-icon {
  color: var(--star-color);
}

/* --- تغییر جدید: استایل‌های حباب‌ها --- */
.status-bubble {
  padding: 6px 14px;
  border-radius: 99px;
  white-space: nowrap;
}
.status-bubble.type {
  background-color: #e0e7ff;
  color: #3730a3;
}
.status-bubble.status-آزاد {
  background-color: var(--success-bg);
  color: var(--success-text);
}
.status-bubble.status-انصراف {
  background-color: #e5e7eb;
  color: #374151;
}
.status-bubble.status-مسدود {
  background-color: #fee2e2;
  color: #b91c1c;
}
.status-bubble.presence {
  background-color: #f3e8ff;
  color: #6b21a8;
}
.status-bubble.access-active {
  background-color: var(--success-bg);
  color: var(--success-text);
}
.status-bubble.access-inactive {
  background-color: #ffedd5;
  color: #9a3412;
}
</style>
