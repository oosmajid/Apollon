<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '@/stores/dataStore.js'
import { useLayoutStore } from '@/stores/layout.js'
import AppHeader from '@/components/AppHeader.vue'
import MedalsGrid from '@/components/MedalsGrid.vue'
import BaseModal from '@/components/BaseModal.vue'
import BaseTable from '@/components/BaseTable.vue'
import HeartRating from '@/components/HeartRating.vue'
import AssignmentSubmission from '@/components/AssignmentSubmission.vue'
import DetailedProgressBar from '@/components/DetailedProgressBar.vue'

const dataStore = useDataStore()
const layoutStore = useLayoutStore()
const route = useRoute()

// --- جدید: منطق نمایش Alert Bar ---
const alertInfo = computed(() => {
  if (!student.value) return { show: false, reason: '' }

  const status = student.value.status
  const accessStatus = student.value.accessStatus

  let reason = ''
  if (status === 'مسدود') reason = 'وضعیت مسدود'
  else if (status === 'انصراف') reason = 'انصراف شما از دوره'
  else if (accessStatus === 'غیرفعال (بدهی)') reason = 'بدهی مالی'
  else if (accessStatus === 'غیرفعال (تکلیف)') reason = 'عدم ارسال به موقع تکلیف'

  return {
    show: !!reason,
    reason: reason,
  }
})

const studentId = parseInt(route.params.id)
const student = computed(() => dataStore.getStudentById(studentId))

const paymentHistory = computed(() => {
  return dataStore.getPaymentsForStudent(studentId)
})

const course = computed(() => {
  if (!student.value) return null
  return dataStore.courses.find((c) => c.id === student.value.courseId)
})

// متغیرهای جدید برای مودال آپلود تکلیف
const newSubmissionFiles = ref({}) // آبجکتی برای نگهداری فایل‌ها به ازای هر الگو
const newSubmissionNotes = ref('') // متغیری برای یادداشت هنرجو

// --- Medal Details Modal ---
const isMedalModalOpen = ref(false)
const selectedMedal = ref(null)
const medalAwardDescription = ref('')

function handleMedalClick(medal) {
  selectedMedal.value = medal
  const isEarned = student.value.earnedMedalIds.includes(medal.id)

  if (isEarned) {
    const awardLog = student.value.actionLogs.find(
      (log) => log.action.includes(medal.name) && log.action.includes('اعطای مدال'),
    )
    medalAwardDescription.value = awardLog
      ? awardLog.description
      : 'شما این مدال را با تلاش خود کسب کرده‌اید!'
  } else {
    medalAwardDescription.value = ''
  }

  isMedalModalOpen.value = true
}

// --- Assignment Modals ---
const isAssignmentViewModalOpen = ref(false) // مودال مشاهده
const isAssignmentUploadModalOpen = ref(false) // مودال آپلود
const selectedAssignment = ref(null)

// برای باز کردن مودال مشاهده (فقط خواندنی)
function openAssignmentViewModal(assignment) {
  const assignmentCopy = JSON.parse(JSON.stringify(assignment))
  if (assignmentCopy.submissions) {
    assignmentCopy.submissions.sort((a, b) => b.date.localeCompare(a.date))
  }
  selectedAssignment.value = assignmentCopy
  isAssignmentViewModalOpen.value = true
}

// برای باز کردن مودال آپلود
function openAssignmentUploadModal(assignment) {
  selectedAssignment.value = assignment
  newSubmissionFiles.value = {} // پاک کردن فایل‌های قبلی
  newSubmissionNotes.value = '' // پاک کردن یادداشت قبلی
  isAssignmentUploadModalOpen.value = true
}

function handleUpload() {
  console.log('Assignment Submitted with data:', {
    assignmentId: selectedAssignment.value.id,
    files: newSubmissionFiles.value,
    notes: newSubmissionNotes.value,
  })
  alert('تکلیف شما با موفقیت ارسال شد. (شبیه‌سازی)')
  isAssignmentUploadModalOpen.value = false
}

function handleFileSelect(event, templateId) {
  const file = event.target.files[0]
  if (file) {
    newSubmissionFiles.value[templateId] = {
      file: file,
      name: file.name,
      previewUrl: URL.createObjectURL(file), // ایجاد پیش‌نمایش موقت
    }
  }
}

const progressPercent = computed(() => {
  if (!student.value || !student.value.totalWatchTime) return 0
  return (student.value.watchTime / student.value.totalWatchTime) * 100
})

const studentAssignments = computed(() => {
  if (!student.value) return []
  return dataStore.getAssignmentsForStudentProfile(studentId, student.value.courseId)
})

const assignmentColumns = [
  { key: 'title', label: 'عنوان تکلیف' },
  { key: 'dueDate', label: 'مهلت ارسال' },
  { key: 'submissionDate', label: 'تاریخ ارسال' },
  { key: 'status', label: 'وضعیت بررسی' },
  { key: 'grade', label: 'نمره', width: '100px' },
  { key: 'actions', label: '', sortable: false, filterable: false, width: '220px' },
]

const logColumns = [
  { key: 'action', label: 'اقدام' },
  { key: 'dateTime', label: 'تاریخ و ساعت' },
  { key: 'author', label: 'توسط' },
]

onMounted(() => {
  layoutStore.setPageTitle('آکادمی هنرهای دیجیتال رایان')
})
</script>

<template>
  <div class="student-profile-page">
    <AppHeader />
    <main class="profile-grid" v-if="student">
      <aside class="profile-sidebar">
        <div class="profile-card card">
          <div class="profile-image">
            <img src="https://picsum.photos/120/120" alt="عکس هنرجو" />
          </div>
          <h2 class="profile-name">{{ student.name }}</h2>
          <ul class="profile-details">
            <li>
              <i class="fa-solid fa-mobile-screen-button"></i> <span>{{ student.phone }}</span>
            </li>
            <li>
              <i class="fa-solid fa-cake-candles"></i>
              <span>متولد {{ student.birthYear || 'نامشخص' }}</span>
            </li>
            <li>
              <i class="fa-solid fa-location-dot"></i> <span>{{ student.city || 'نامشخص' }}</span>
            </li>
          </ul>
        </div>
        <div class="payments-card card">
          <div class="payments-header">
            <h4>وضعیت پرداخت‌ها</h4>
          </div>
          <ul v-if="paymentHistory.length" class="payment-list">
            <li v-for="payment in paymentHistory" :key="payment.id" class="payment-item">
              <div class="payment-info">
                <i class="fa-solid fa-wallet payment-icon" :class="payment.type"></i>
                <div>
                  <span class="payment-amount"
                    >{{ Number(payment.amount).toLocaleString('fa-IR') }} تومان</span
                  >
                  <small class="payment-date">{{ payment.date }} - {{ payment.method }}</small>
                </div>
              </div>
              <div class="payment-status">
                <span class="status-badge" :class="payment.status.replace(' ', '-')">{{
                  payment.status
                }}</span>
              </div>
            </li>
          </ul>
          <p v-else class="no-data">سابقه‌ای یافت نشد.</p>
        </div>
      </aside>

      <div class="profile-main-content">
        <div class="course-selector card">
          <label for="course-select">نمایش اطلاعات برای دوره:</label>
          <select id="course-select">
            <option :value="student.course">{{ student.course }}</option>
          </select>
        </div>

        <div v-if="alertInfo.show" class="alert-bar">
          <i class="fa-solid fa-circle-exclamation"></i>
          <span>
            به دلیل «{{ alertInfo.reason }}» دسترسی شما به دوره محدود شده است. جهت توضیحات بیش‌تر با
            آپولون‌یار خودتان در تماس باشید.
          </span>
        </div>

        <div class="stats-grid-container">
          <div class="stat-card card">
            <div class="card-title"><h4>نوع</h4></div>
            <p>
              <span class="status-bubble type">{{ student.studentType }}</span>
            </p>
          </div>
          <div class="stat-card card">
            <div class="card-title"><h4>وضعیت</h4></div>
            <p>
              <span class="status-bubble" :class="`status-${student.status}`">{{
                student.status
              }}</span>
            </p>
          </div>
          <div class="stat-card card">
            <div class="card-title"><h4>حضور</h4></div>
            <p>
              <span class="status-bubble presence">{{ student.enrollmentStatus }}</span>
            </p>
          </div>
          <div class="stat-card card">
            <div class="card-title"><h4>دسترسی</h4></div>
            <p>
              <span
                class="status-bubble"
                :class="
                  student.accessStatus && student.accessStatus.includes('فعال')
                    ? 'access-active'
                    : 'access-inactive'
                "
                >{{ student.accessStatus }}</span
              >
            </p>
          </div>
          <div class="stat-card card">
            <div class="card-title"><h4>ترم</h4></div>
            <p>{{ student.term }}</p>
            <small class="term-dates"
              ><i class="fa-solid fa-calendar-alt"></i
              ><span>{{ student.termStartDate }} تا {{ student.termEndDate }}</span></small
            >
          </div>
          <div class="stat-card card">
            <div class="card-title"><h4>آپولون‌یار</h4></div>
            <p>{{ student.apollonyar }}</p>
            <small class="term-dates"
              ><i class="fa-brands fa-telegram"></i
              ><span dir="ltr">{{ student.apollonyarTelegramId }}</span></small
            >
          </div>
          <div class="stat-card card">
            <div class="card-title"><h4>جان</h4></div>
            <div class="icon-value-wrapper"><HeartRating :count="student.hearts" /></div>
          </div>
          <div class="stat-card card">
            <div class="card-title"><h4>امتیاز</h4></div>
            <div class="icon-value-wrapper">
              <p>{{ student.score }} <i class="fa-solid fa-star score-icon"></i></p>
            </div>
          </div>
        </div>

        <MedalsGrid
          :earned-medal-ids="student.earnedMedalIds || []"
          @medal-click="handleMedalClick"
        />

        <div class="progress-section card">
          <div class="progress-header">
            <h4>پیشرفت دوره</h4>
            <span class="total-progress-text"
              >{{ student.watchTime }} از {{ student.totalWatchTime }} ساعت ({{
                Math.round(progressPercent)
              }}٪)</span
            >
          </div>
          <DetailedProgressBar
            v-if="course"
            :chapters="course.chapters || []"
            :progress-data="student.chapterProgress || []"
          />
        </div>

        <div class="card">
          <div class="card-header"><h4>تکالیف</h4></div>
          <BaseTable
            :columns="assignmentColumns"
            :data="studentAssignments || []"
            :rows-per-page="10"
          >
            <template #cell-actions="{ item }">
              <div class="action-buttons">
                <button
                  @click="openAssignmentViewModal(item)"
                  class="btn-sm btn-icon-only"
                  :disabled="!item.submissionDate"
                  title="مشاهده جزئیات"
                >
                  <i class="fa-solid fa-eye"></i>
                </button>
                <button @click="openAssignmentUploadModal(item)" class="btn-sm btn-outline">
                  <i class="fa-solid fa-upload"></i>
                  <span>{{ item.submissionDate ? 'ارسال مجدد' : 'ارسال تکلیف' }}</span>
                </button>
              </div>
            </template>
            <template #cell-submissionDate="{ item }"
              ><span v-if="item.submissionDate">{{ item.submissionDate }}</span
              ><span v-else class="status-badge not-submitted">ارسال نشده</span></template
            >
            <template #cell-status="{ item }"
              ><span
                v-if="item.status"
                class="status-badge"
                :class="item.status.includes('بررسی') ? 'checked' : 'not-checked'"
                >{{ item.status }}</span
              ><span v-else>-</span></template
            >
            <template #cell-grade="{ item }">
              <div v-if="item.grade === 'مردود'" class="status-badge grade-failed">
                {{ item.grade }}
              </div>
              <div v-else-if="typeof item.grade === 'number'" class="star-rating">
                <i v-for="star in item.grade" :key="star" class="fa-solid fa-star"></i>
              </div>
              <span v-else>-</span>
            </template>
          </BaseTable>
        </div>

        <div class="card">
          <div class="card-header"><h4>لاگ اقدامات</h4></div>
          <BaseTable :columns="logColumns" :data="student.actionLogs || []" :rows-per-page="5" />
        </div>
      </div>
    </main>
    <div v-else class="loading-state"><h2>در حال بارگذاری اطلاعات هنرجو...</h2></div>

    <BaseModal :show="isMedalModalOpen" @close="isMedalModalOpen = false">
      <template #header><h2 v-if="selectedMedal">جزئیات مدال</h2></template>
      <div v-if="selectedMedal" class="medal-modal-content">
        <i :class="selectedMedal.icon" class="modal-medal-icon"></i>
        <h3>{{ selectedMedal.name }}</h3>
        <p class="medal-description">{{ selectedMedal.description }}</p>
        <div v-if="student.earnedMedalIds.includes(selectedMedal.id)" class="award-reason">
          <i class="fa-solid fa-quote-left"></i>
          <p>{{ medalAwardDescription }}</p>
        </div>
      </div>
    </BaseModal>

    <BaseModal
      :show="isAssignmentViewModalOpen"
      @close="isAssignmentViewModalOpen = false"
      size="lg"
    >
      <template #header
        ><h2>جزئیات تکلیف: {{ selectedAssignment?.title }}</h2></template
      >
      <div v-if="selectedAssignment" class="modal-body-content">
        <div class="submissions-wrapper">
          <AssignmentSubmission
            v-for="submission in selectedAssignment.submissions"
            :key="submission.version"
            :submission="submission"
            :template-files="selectedAssignment.templateFiles"
            is-read-only
          />
        </div>
      </div>
    </BaseModal>

    <BaseModal
      :show="isAssignmentUploadModalOpen"
      @close="isAssignmentUploadModalOpen = false"
      size="lg"
    >
      <template #header>
        <h2>ارسال تکلیف: {{ selectedAssignment?.title }}</h2>
      </template>
      <div v-if="selectedAssignment" class="upload-modal-content">
        <div class="upload-grid">
          <div class="upload-column">
            <h5>فایل‌های الگو (برای دانلود)</h5>
            <div
              v-for="template in selectedAssignment.templateFiles"
              :key="template.id"
              class="template-file-row"
            >
              <a :href="template.url" target="_blank" class="template-preview">
                <img :src="template.url" :alt="template.name" />
                <span>{{ template.name }}</span>
              </a>
            </div>
          </div>

          <div class="upload-column">
            <h5>فایل‌های ارسالی شما</h5>
            <div
              v-for="template in selectedAssignment.templateFiles"
              :key="template.id"
              class="upload-file-row"
            >
              <div class="upload-preview">
                <img
                  v-if="newSubmissionFiles[template.id]"
                  :src="newSubmissionFiles[template.id].previewUrl"
                  alt="Preview"
                />
                <i v-else class="fa-solid fa-file-image"></i>
              </div>
              <label :for="`file-input-${template.id}`" class="btn-sm btn-outline">
                <i class="fa-solid fa-upload"></i>
                <span>{{ newSubmissionFiles[template.id] ? 'تغییر فایل' : 'انتخاب فایل' }}</span>
              </label>
              <input
                :id="`file-input-${template.id}`"
                type="file"
                @change="handleFileSelect($event, template.id)"
                hidden
              />
            </div>
          </div>
        </div>

        <div class="notes-section">
          <label for="student-notes">توضیحات و یادداشت شما (اختیاری)</label>
          <textarea
            id="student-notes"
            v-model="newSubmissionNotes"
            rows="3"
            placeholder="اگر نکته‌ای برای آپولون‌یار خود دارید، اینجا بنویسید..."
          ></textarea>
        </div>

        <div class="modal-actions">
          <button
            @click="isAssignmentUploadModalOpen = false"
            type="button"
            class="btn btn-outline"
          >
            انصراف
          </button>
          <button @click="handleUpload" type="button" class="btn">ارسال نهایی تکلیف</button>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<style scoped>
.student-profile-page {
  background-color: var(--background-color);
  min-height: 100vh;
  padding: 30px;
}
.card {
  background-color: var(--surface-color);
  border-radius: var(--border-radius);
  padding: 25px;
  box-shadow: var(--shadow-color) 0px 7px 29px 0px;
}
.profile-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 30px;
}
.profile-main-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}
.profile-sidebar .profile-card {
  text-align: center;
}
.profile-image img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid var(--primary-color);
  object-fit: cover;
  margin-bottom: 15px;
}
.profile-name {
  margin-bottom: 20px;
  font-size: 1.5rem;
}
.profile-details {
  list-style: none;
  text-align: right;
}
.profile-details li {
  margin-bottom: 15px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
}
.profile-details li i {
  margin-left: 12px;
  color: var(--primary-color);
  width: 20px;
  text-align: center;
}
.course-selector {
  display: flex;
  align-items: center;
  gap: 15px;
}
.course-selector select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
}
.stats-grid-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.stat-card {
  text-align: center;
  display: flex;
  flex-direction: column;
}
.stat-card .card-title {
  justify-content: center;
  color: var(--text-secondary);
  margin-bottom: 15px;
}
.stat-card p {
  font-size: 1rem;
  font-weight: 500;
  margin: 0;
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stat-card .term-dates {
  font-size: 0.75rem;
  color: var(--text-secondary);
  background-color: var(--background-color);
  padding: 4px 8px;
  border-radius: 12px;
  margin-top: 10px;
  white-space: nowrap;
}
.stat-card .term-dates i {
  margin-left: 5px;
}
.status-bubble {
  padding: 6px 14px;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 500;
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
.icon-value-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 5px;
  flex-grow: 1;
}
.icon-value-wrapper p {
  font-size: 1.2rem;
  font-weight: 700;
}
.score-icon {
  color: var(--star-color);
}
.progress-section h4 {
  margin-bottom: 15px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}
.btn-sm.btn-outline {
  height: 32px;
  padding: 0 14px;
  font-size: 13px;
}
.btn-icon-only {
  width: 32px;
  height: 32px;
  padding: 0;
  font-size: 1rem;
}
.btn-icon-only:disabled {
  background-color: var(--border-color);
  color: var(--text-secondary);
  cursor: not-allowed;
  opacity: 0.6;
}
.status-badge {
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 11px;
  white-space: nowrap;
}
.status-badge.checked {
  background-color: var(--success-bg);
  color: var(--success-text);
}
.status-badge.not-checked {
  background-color: #ffedd5;
  color: #9a3412;
}
.status-badge.not-submitted {
  background-color: #e5e7eb;
  color: #374151;
}
.grade-failed {
  background-color: #fee2e2;
  color: #b91c1c;
}
.star-rating {
  color: var(--star-color);
  white-space: nowrap;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.progress-header h4 {
  margin-bottom: 0;
}
.total-progress-text {
  color: var(--text-secondary);
  font-weight: 500;
}
.modal-body-content {
  display: flex;
  flex-direction: column;
}
.submissions-wrapper {
  max-height: 60vh;
  overflow-y: auto;
  padding: 5px 15px 5px 5px;
  margin: 0 -15px 0 -5px;
}
.medal-modal-content {
  text-align: center;
}
.modal-medal-icon {
  font-size: 4rem;
  color: var(--star-color);
  margin-bottom: 15px;
}
.modal-medal-content h3 {
  font-size: 1.5rem;
  margin-bottom: 10px;
}
.medal-description {
  background-color: var(--background-color);
  padding: 10px 15px;
  border-radius: 8px;
  font-size: 0.9rem;
  line-height: 1.7;
  margin-bottom: 20px;
  text-align: justify;
}
.award-reason {
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
  margin-top: 20px;
  color: var(--text-secondary);
  font-style: italic;
}
.award-reason i {
  margin-bottom: 10px;
  color: var(--primary-color);
}
.loading-state {
  text-align: center;
  padding: 50px;
  color: var(--text-secondary);
}

/* استایل‌های مودال آپلود */
.upload-modal-content p {
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: 20px;
}
.dropzone {
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius);
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition:
    border-color 0.3s,
    background-color 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 15px;
  background-color: var(--background-color);
}
.dropzone:hover {
  border-color: var(--primary-color);
  background-color: #f4f7fc;
}
[data-theme='dark'] .dropzone:hover {
  background-color: #1a233b;
}
.dropzone i {
  font-size: 3rem;
  color: var(--primary-color);
}
.dropzone span {
  font-weight: 500;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}
/* استایل‌های جدید برای Alert Bar */
.alert-bar {
  background-color: #fee2e2; /* red-100 */
  color: #b91c1c; /* red-700 */
  border: 1px solid #fecaca; /* red-200 */
  border-radius: var(--border-radius);
  padding: 15px 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 0.95rem;
}
.alert-bar i {
  font-size: 1.2rem;
}
[data-theme='dark'] .alert-bar {
  background-color: #451b1b;
  color: #fca5a5; /* red-300 */
  border-color: #7f1d1d;
}
/* --- استایل‌های بخش پرداخت‌ها --- */
.profile-sidebar {
  display: flex;
  flex-direction: column;
  gap: 25px;
}
.payments-card {
  text-align: right;
}
.payments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}
.payments-header h4 {
  margin: 0;
}
.payment-list {
  list-style: none;
  max-height: 400px;
  overflow-y: auto;
  padding-left: 10px;
}
.payment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}
.payment-item:last-child {
  border-bottom: none;
}
.payment-info {
  display: flex;
  align-items: center;
  gap: 15px;
}
.payment-icon {
  font-size: 1.5rem;
}
.payment-icon.واریز {
  color: var(--success-text);
}
.payment-icon.قسط {
  color: var(--warning-text);
}
.payment-amount {
  display: block;
  font-weight: 500;
}
.payment-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
}
.status-badge.پرداخت-شده {
  background-color: var(--success-bg);
  color: var(--success-text);
}
.status-badge.سررسید-شده {
  background-color: #fee2e2;
  color: #b91c1c;
}
.status-badge.درآینده {
  background-color: #e0e7ff;
  color: #3730a3;
}
.no-data {
  color: var(--text-secondary);
  text-align: center;
  padding: 20px 0;
}
/* --- استایل‌های جدید مودال آپلود --- */
.upload-modal-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}
.upload-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 20px;
}
.upload-column h5 {
  text-align: center;
  margin-bottom: 15px;
  color: var(--text-secondary);
  font-weight: 400;
}
.template-file-row,
.upload-file-row {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
  border-radius: 8px;
  min-height: 80px;
}
.template-file-row:hover {
  background-color: var(--background-color);
}
.template-preview {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--text-primary);
  font-weight: 500;
}
.template-preview img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}
.upload-preview {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  border: 1px dashed var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--background-color);
}
.upload-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.upload-preview i {
  font-size: 1.5rem;
  color: var(--text-secondary);
}
.notes-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}
.notes-section textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
  font-family: 'Vazirmatn', sans-serif;
  resize: vertical;
}
</style>
