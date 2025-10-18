<script setup>
import { ref, onMounted } from 'vue';
import BaseTable from '@/components/BaseTable.vue';
import BaseModal from '@/components/BaseModal.vue';
import AssignmentSubmission from '@/components/AssignmentSubmission.vue';
import { useLayoutStore } from '@/stores/layout.js';
import api from '@/services/api';

const layoutStore = useLayoutStore();
const assignments = ref([]);
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0
});
const loading = ref(false);

async function loadAssignments(page = 1) {
  loading.value = true;
  try {
    const params = {
      page,
      page_size: pagination.value.pageSize,
    };

    const response = await api.getAssignments(params);

    // فرمت پاسخ Django pagination
    assignments.value = response.data.results || response.data;
    pagination.value.total = response.data.count || assignments.value.length;
    pagination.value.page = page;
    pagination.value.totalPages = Math.ceil(pagination.value.total / pagination.value.pageSize);
  } catch (error) {
    console.error("Failed to fetch assignments:", error);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  layoutStore.setPageTitle('تکالیف');
  await loadAssignments();
});

// تابع تغییر صفحه
function handlePageChange(page) {
  loadAssignments(page);
}

const isModalOpen = ref(false);
const selectedAssignment = ref(null);

function openEvaluationModal(assignment) {
  // کپی عمیق برای جلوگیری از تغییرات ناخواسته
  const assignmentCopy = JSON.parse(JSON.stringify(assignment));
  // مرتب‌سازی نسخه‌های ارسالی بر اساس تاریخ (جدیدترین اول)
  if (assignmentCopy.submissions) {
    assignmentCopy.submissions.sort((a, b) => b.date.localeCompare(a.date));
  }
  selectedAssignment.value = assignmentCopy;
  isModalOpen.value = true;
}

async function submitEvaluation() {
  try {
    // این باید از فرم ارزیابی گرفته شود - فعلاً placeholder
    const gradeData = {
      grade: 5, // این باید از فرم گرفته شود
      feedback: 'ارزیابی انجام شد' // این باید از فرم گرفته شود
    };

    // فرض می‌کنیم که آخرین submission را ارزیابی می‌کنیم
    const latestSubmission = selectedAssignment.value.submissions?.[0];
    if (latestSubmission) {
      await api.gradeSubmission(latestSubmission.id, gradeData);

      // آپدیت کردن لیست تکالیف
      await loadAssignments(pagination.value.page);
    }

    isModalOpen.value = false;
  } catch (error) {
    console.error("Failed to submit evaluation:", error);
    alert('خطا در ثبت ارزیابی. لطفاً دوباره تلاش کنید.');
  }
}

const tableColumns = [
  { key: 'actions', label: '', sortable: false, filterable: false },
  { key: 'studentName', label: 'نام هنرجو', sortable: true, filterable: true },
  { key: 'assignmentTitle', label: 'عنوان تکلیف', sortable: true, filterable: true },
  { key: 'course', label: 'دوره', sortable: true, filterable: true },
  { key: 'apollonyar', label: 'آپولون‌یار', sortable: true, filterable: true },
  { key: 'assessorApollonyar', label: 'شخص مصحح', sortable: true, filterable: true },
  { key: 'submissionDate', label: 'تاریخ ارسال', sortable: true, filterable: false },
  { key: 'reviewDate', label: 'تاریخ بررسی', sortable: true, filterable: false },
  { key: 'status', label: 'وضعیت بررسی', sortable: true, filterable: true },
  { key: 'grade', label: 'نمره', sortable: true, filterable: true },
];
</script>

<template>
  <div class="view-container">
    <BaseTable
      :columns="tableColumns"
      :data="assignments"
      :rows-per-page="pagination.pageSize"
      :server-side="true"
      :total-items="pagination.total"
      :current-page="pagination.page"
      :loading="loading"
      @page-change="handlePageChange"
    >
      <template #cell-actions="{ item }">
        <div class="action-buttons">
          <button @click="openEvaluationModal(item)" class="btn-sm btn-icon-only" title="مشاهده تکلیف">
            <i class="fa-solid fa-eye"></i>
          </button>
          <RouterLink :to="{ name: 'student-profile', params: { id: item.studentId } }" class="btn-sm btn-icon-only" title="مشاهده پروفایل">
            <i class="fa-solid fa-user"></i>
          </RouterLink>
        </div>
      </template>
      
      <template #cell-status="{ item }">
        <span class="status-badge" :class="item.status === 'بررسی شده' ? 'checked' : 'not-checked'">
          {{ item.status }}
        </span>
      </template>
      
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

  <BaseModal :show="isModalOpen" @close="isModalOpen = false" size="lg">
    <template #header>
      <h2>ارزیابی تکلیف: {{ selectedAssignment?.studentName }} - {{ selectedAssignment?.assignmentTitle }}</h2>
    </template>
    <div v-if="selectedAssignment" class="modal-body-content">
      <div class="submissions-wrapper">
        <AssignmentSubmission
          v-for="submission in selectedAssignment.submissions"
          :key="submission.version"
          :submission="submission"
          :template-files="selectedAssignment.templateFiles"
        />
      </div>
      <div class="evaluation-footer">
        <button @click="submitEvaluation" class="btn">ثبت نهایی ارزیابی</button>
      </div>
    </div>
  </BaseModal>
</template>

<style scoped>
.view-container { padding-top: 20px; }
.btn-icon-only {
  width: 32px;
  height: 32px;
  padding: 0;
  font-size: 1rem;
}
.status-badge { padding: 4px 12px; border-radius: 99px; font-size: 11px; white-space: nowrap; }
.status-badge.checked { background-color: var(--success-bg); color: var(--success-text); }
.status-badge.not-checked { background-color: #ffedd5; color: #9a3412; }

.status-badge.grade-failed {
  background-color: #fee2e2;
  color: #b91c1c;
  display: inline-flex;
  align-items: center;
}
.star-rating {
  color: var(--star-color);
}
.star-rating .fa-star {
  margin: 0 1px;
}

/* استایل‌های مودال */
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
.evaluation-footer { 
  border-top: 1px solid var(--border-color); 
  padding-top: 20px; 
  margin-top: 20px; 
  text-align: center; 
}
.action-buttons {
  display: flex;
  gap: 8px;
}
</style>