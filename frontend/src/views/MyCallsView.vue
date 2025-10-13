<script setup>
import BaseTable from '@/components/BaseTable.vue';
import HeartRating from '@/components/HeartRating.vue'; // کامپوننت قلب را import کنید
import { ref, onMounted } from 'vue';
import { useLayoutStore } from '@/stores/layout.js';
import api from '@/services/api'

const layoutStore = useLayoutStore();
const calls = ref([])
onMounted(async () => {
    layoutStore.setPageTitle('تماس‌های من');
    try {
        // فرض می‌کنیم API برای تماس‌ها در آینده فیلتر بر اساس آپولون‌یار را پشتیبانی خواهد کرد
        const response = await api.getCalls(); // یا یک API اختصاصی مانند getMyCalls
        calls.value = response.data;
    } catch (error) {
        console.error("Failed to fetch calls:", error);
    }
});


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
    <BaseTable :columns="tableColumns" :data="calls" :rows-per-page="20">
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