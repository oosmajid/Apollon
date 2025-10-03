<script setup>
import { useDataStore } from '@/stores/dataStore.js';
import BaseTable from '@/components/BaseTable.vue';
import HeartRating from '@/components/HeartRating.vue'; // کامپوننت قلب را import کنید
import { onMounted } from 'vue';
import { useLayoutStore } from '@/stores/layout.js';

const dataStore = useDataStore();
const layoutStore = useLayoutStore();
onMounted(() => {
  layoutStore.setPageTitle('تماس‌های من');
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
    <BaseTable :columns="tableColumns" :data="dataStore.callsForTable" :rows-per-page="20">
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