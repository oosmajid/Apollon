<script setup>
import BaseTable from '@/components/BaseTable.vue';
import { ref, onMounted } from 'vue';
import { useLayoutStore } from '@/stores/layout.js';
import api from '@/services/api';

const layoutStore = useLayoutStore();
const installments = ref([]);
onMounted(async () => {
  layoutStore.setPageTitle('پیگیری اقساط');
  try {
    // <--- ۳. داده‌ها را از API جدید فراخوانی کنید
    const response = await api.getInstallments();
    installments.value = response.data;
  } catch (error) {
    console.error("Failed to fetch installments:", error);
  }
});

// ستون جدید "actions" اضافه شد
const tableColumns = [
  { key: 'actions', label: '', sortable: false, filterable: false }, 
  { key: 'studentName', label: 'نام هنرجو', sortable: true, filterable: true },
  { key: 'phone', label: 'شماره تلفن', sortable: false, filterable: true },
  { key: 'dueDate', label: 'تاریخ جدید قسط', sortable: true, filterable: false },
  { key: 'amount', label: 'مبلغ قسط', sortable: true, filterable: false },
  { key: 'daysRemaining', label: 'روزهای مانده/گذشته', sortable: true, filterable: false },
  { key: 'paymentStatus', label: 'وضعیت پرداخت', sortable: true, filterable: true },
  { key: 'term', label: 'ترم', sortable: true, filterable: true },
  { key: 'course', label: 'دوره', sortable: true, filterable: true },
  { key: 'apollonyar', label: 'آپولون‌یار', sortable: true, filterable: true },
  { key: 'lastContactDate', label: 'آخرین تماس پیگیری', sortable: true, filterable: false },
  { key: 'courseStatus', label: 'وضعیت دوره', sortable: true, filterable: true },
];
</script>

<template>
  <div class="view-container">
    <BaseTable :columns="tableColumns" :data="installments" :rows-per-page="20">
      <template #cell-daysRemaining="{ item }">
        <span :class="item.daysRemaining < 0 ? 'days-past' : 'days-future'">
          {{ Math.abs(item.daysRemaining) }}
        </span>
      </template>
      <template #cell-paymentStatus="{ item }">
        <span class="status-badge" :class="item.paymentStatus ? item.paymentStatus.replace(' ', '-') : 'unknown'">
          {{ item.paymentStatus || 'نامشخص' }}
        </span>
      </template>
       <template #cell-courseStatus="{ item }">
        <span class="status-badge" :class="item.courseStatus === 'فعال' ? 'active' : 'inactive'">
          {{ item.courseStatus }}
        </span>
      </template>
      <template #cell-actions="{ item }">
        <RouterLink :to="{ name: 'student-profile', params: { id: item.studentId } }" class="btn-sm btn-icon-only" title="مشاهده پروفایل">
           <i class="fa-solid fa-user"></i>
        </RouterLink>
      </template>
    </BaseTable>
  </div>
</template>

<style scoped>
.view-container { padding-top: 20px; }
.days-past { color: var(--danger-color); font-weight: bold; }
.days-future { color: var(--success-text); }
.status-badge { padding: 4px 12px; border-radius: 99px; font-size: 11px; white-space: nowrap; }

/* استایل‌های جدید برای وضعیت پرداخت */
.status-badge.پرداخت-شده { background-color: var(--success-bg); color: var(--success-text); }
.status-badge.سررسید-شده { background-color: #fee2e2; color: #b91c1c; }
.status-badge.درآینده { background-color: #e0e7ff; color: #3730a3; }

.status-badge.active { background-color: var(--success-bg); color: var(--success-text); }
.status-badge.inactive { background-color: #fee2e2; color: #b91c1c; }

.btn-icon-only {
  width: 32px;
  height: 32px;
  padding: 0;
  font-size: 1rem;
}
</style>