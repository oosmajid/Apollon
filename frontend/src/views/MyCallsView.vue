<script setup>
import BaseTable from '@/components/BaseTable.vue';
import HeartRating from '@/components/HeartRating.vue'; // کامپوننت قلب را import کنید
import { ref, onMounted } from 'vue';
import { useLayoutStore } from '@/stores/layout.js';
import api from '@/services/api'

const layoutStore = useLayoutStore();
const calls = ref([]);
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0
});
const loading = ref(false);

async function loadCalls(page = 1) {
  loading.value = true;
  try {
    const params = {
      page,
      page_size: pagination.value.pageSize,
    };

    const response = await api.getCalls(params);

    // فرمت پاسخ Django pagination
    calls.value = response.data.results || response.data;
    pagination.value.total = response.data.count || calls.value.length;
    pagination.value.page = page;
    pagination.value.totalPages = Math.ceil(pagination.value.total / pagination.value.pageSize);
  } catch (error) {
    console.error("Failed to fetch calls:", error);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
    layoutStore.setPageTitle('تماس‌های من');
    await loadCalls();
});

// تابع تغییر صفحه
function handlePageChange(page) {
  loadCalls(page);
}


const tableColumns = [
  { key: 'actions', label: '', sortable: false, filterable: false },
  { key: 'studentName', label: 'نام هنرجو', sortable: true, filterable: true },
  { key: 'phone', label: 'شماره تلفن', sortable: false, filterable: true },
  { key: 'topic', label: 'موضوع تماس', sortable: true, filterable: true },
  { key: 'callStatus', label: 'وضعیت تماس', sortable: true, filterable: true },
  { key: 'previousCallDate', label: 'تاریخ تماس قبلی', sortable: true, filterable: false },
  { key: 'daysToCallWindow', label: 'بازه تماس (روز)', sortable: true, filterable: false },
  { key: 'previousCallTopic', label: 'موضوع تماس قبلی', sortable: true, filterable: true },
  { key: 'apollonyar', label: 'آپولون‌یار', sortable: true, filterable: true },
  { key: 'hearts', label: 'جان', sortable: true, filterable: false },
  { key: 'course', label: 'دوره', sortable: true, filterable: true },
  { key: 'term', label: 'ترم', sortable: true, filterable: true },
];
</script>


<template>
  <div class="view-container">
    <BaseTable
      :columns="tableColumns"
      :data="calls"
      :rows-per-page="pagination.pageSize"
      :server-side="true"
      :total-items="pagination.total"
      :current-page="pagination.page"
      :loading="loading"
      @page-change="handlePageChange"
    >
      <template #cell-actions="{ item }">
        <RouterLink :to="{ name: 'student-profile', params: { id: item.studentId } }" class="btn-sm btn-icon-only" title="مشاهده پروفایل">
          <i class="fa-solid fa-user"></i>
        </RouterLink>
      </template>
      <template #cell-hearts="{ item }">
        <HeartRating :count="item.hearts" />
      </template>
    </BaseTable>
  </div>
</template>

<style scoped>
.view-container { padding-top: 20px; }
.btn-icon-only {
  width: 32px;
  height: 32px;
  padding: 0;
  font-size: 1rem;
}
</style>