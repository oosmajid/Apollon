<script setup>
import { onMounted, computed } from 'vue';
import { useLayoutStore } from '@/stores/layout.js';
import { useDataStore } from '@/stores/dataStore.js';
import BaseTable from '@/components/BaseTable.vue';
import dayjs from 'dayjs';
import jalali from 'dayjs-jalali';

dayjs.extend(jalali);
dayjs.locale('fa');

const layoutStore = useLayoutStore();
const dataStore = useDataStore();

onMounted(() => {
  layoutStore.setPageTitle('داشبورد');
});

// --- ۱. محاسبه داده‌های کارت‌های اطلاعات سریع ---
const statCards = computed(() => [
  { id: 1, title: "تماس‌های در انتظار", value: dataStore.calls.filter(c => c.callStatus === 'برای انجام').length, icon: 'fa-solid fa-phone-volume' },
  { id: 2, title: "کل هنرجویان", value: dataStore.students.length, icon: 'fa-solid fa-users' },
  { id: 3, title: "شاخص سوم", value: 'N/A', icon: 'fa-solid fa-chart-pie' },
  { id: 4, title: "شاخص چهارم", value: 'N/A', icon: 'fa-solid fa-chart-line' },
  { id: 5, title: "شاخص پنجم", value: 'N/A', icon: 'fa-solid fa-gauge-high' },
]);

// --- ۲. آماده‌سازی داده‌های جدول اصلی ---
const tableData = computed(() => {
  const calculatePercentage = (part, whole) => {
    if (!part || !whole) return '0.0';
    return ((part / whole) * 100).toFixed(1);
  };
  const parsePersianDate = (persianDate) => {
    if (!persianDate) return null;
    const parts = persianDate.split('/');
    return dayjs(`${parts[0]}-${parts[1]}-${parts[2]}`, { jalali: true });
  };
  
  const uniqueCombinations = dataStore.studentsWithDetails.reduce((acc, student) => {
    if (student.apollonyarId && student.termId) {
      const key = `${student.apollonyarId}-${student.termId}`;
      if (!acc[key]) acc[key] = { apollonyarId: student.apollonyarId, termId: student.termId };
    }
    return acc;
  }, {});

  return Object.values(uniqueCombinations).map(combo => {
    const relevantStudents = dataStore.studentsWithDetails.filter(s => s.apollonyarId === combo.apollonyarId && s.termId === combo.termId);
    const studentsAtStart = relevantStudents.length;
    if (studentsAtStart === 0) return null;

    const apollonyarInfo = dataStore.apollonyars.find(a => a.id === combo.apollonyarId);
    const termInfo = dataStore.terms.find(t => t.id === combo.termId);
    const courseInfo = dataStore.courses.find(c => c.id === termInfo?.courseId);

    const today = dayjs();
    const startDate = parsePersianDate(termInfo.startDate);
    const endDate = parsePersianDate(termInfo.endDate);
    let courseStage = 'نامشخص';
    if (startDate?.isValid() && endDate?.isValid()) {
      if (today.isBefore(startDate)) courseStage = 'شروع نشده';
      else if (today.isAfter(endDate)) courseStage = 'خاتمه یافته';
      else courseStage = `روز ${today.diff(startDate, 'day') + 1} دوره`;
    }

    const currentActiveStudents = relevantStudents.filter(s => s.status === 'فعال' && s.studentType === 'ترمی').length;
    const inactiveInstallment = relevantStudents.filter(s => s.accessStatus === 'غیرفعال (بدهی)').length;
    const inactiveAssignment = relevantStudents.filter(s => s.accessStatus === 'غیرفعال (تکلیف)').length;
    const droppedOut = relevantStudents.filter(s => s.status === 'انصراف').length;
    const changedTerm = Math.floor(Math.random() * (studentsAtStart / 10));

    const row = {
      id: `${combo.apollonyarId}-${combo.termId}`,
      apollonyarName: apollonyarInfo?.name, apollonyarPhone: apollonyarInfo?.phone,
      courseName: courseInfo?.name, termName: termInfo?.name, courseStage,
      toDoCalls: dataStore.calls.filter(c => c.apollonyarId === combo.apollonyarId && c.termId === combo.termId && c.callStatus === 'برای انجام').length,
      burntCalls: dataStore.calls.filter(c => c.apollonyarId === combo.apollonyarId && c.termId === combo.termId && c.callStatus === 'سوخته').length,
      studentsAtStart,
      currentActiveStudents: { count: currentActiveStudents, percent: calculatePercentage(currentActiveStudents, studentsAtStart) },
      inactiveInstallment: { count: inactiveInstallment, percent: calculatePercentage(inactiveInstallment, studentsAtStart) },
      inactiveAssignment: { count: inactiveAssignment, percent: calculatePercentage(inactiveAssignment, studentsAtStart) },
      droppedOut: { count: droppedOut, percent: calculatePercentage(droppedOut, studentsAtStart) },
      changedTerm: { count: changedTerm, percent: calculatePercentage(changedTerm, studentsAtStart) },
    };
    dataStore.medals.forEach(medal => {
      const count = relevantStudents.filter(s => s.earnedMedalIds.includes(medal.id)).length;
      row[`medal_${medal.id}`] = { count: count, percent: calculatePercentage(count, studentsAtStart) };
    });
    return row;
  }).filter(Boolean);
});

// --- ۳. ساخت ستون‌های جدول ---
const tableColumns = computed(() => {
  const staticColumns = [
    { key: 'apollonyarName', label: 'نام آپولون‌یار' }, { key: 'apollonyarPhone', label: 'شماره تلفن' }, { key: 'courseName', label: 'دوره' }, { key: 'termName', label: 'ترم' }, { key: 'courseStage', label: 'مرحله دوره' }, { key: 'toDoCalls', label: 'تماس‌های در انتظار' }, { key: 'burntCalls', label: 'تماس‌های سوخته' }, { key: 'studentsAtStart', label: 'هنرجویان روز شروع' }, { key: 'currentActiveStudents', label: 'هنرجویان فعلی' }, { key: 'inactiveInstallment', label: 'غیرفعال (قسط)' }, { key: 'inactiveAssignment', label: 'غیرفعال (تکلیف)' }, { key: 'droppedOut', label: 'انصرافی' }, { key: 'changedTerm', label: 'تغییر ترم' },
  ];
  const medalColumns = dataStore.medals.map(medal => ({ key: `medal_${medal.id}`, label: `دارای مدال ${medal.name}` }));
  return [...staticColumns, ...medalColumns].map(col => ({ ...col, sortable: true, filterable: true }));
});

const formatCountPercent = (data) => {
    if (data && typeof data.count !== 'undefined') return `${data.count} (${data.percent || '0.0'}٪)`;
    return data;
};
</script>

<template>
  <div class="dashboard-container">
    <div class="stats-cards-grid">
      <div v-for="card in statCards" :key="card.id" class="stat-card">
        <div class="card-icon"><i :class="card.icon"></i></div>
        <div class="card-info"><span class="card-title">{{ card.title }}</span><span class="card-value">{{ card.value }}</span></div>
      </div>
    </div>
    <div class="dashboard-table">
      <BaseTable :columns="tableColumns" :data="tableData" :rows-per-page="10">
        <template #cell-currentActiveStudents="{ item }">{{ formatCountPercent(item.currentActiveStudents) }}</template>
        <template #cell-inactiveInstallment="{ item }">{{ formatCountPercent(item.inactiveInstallment) }}</template>
        <template #cell-inactiveAssignment="{ item }">{{ formatCountPercent(item.inactiveAssignment) }}</template>
        <template #cell-droppedOut="{ item }">{{ formatCountPercent(item.droppedOut) }}</template>
        <template #cell-changedTerm="{ item }">{{ formatCountPercent(item.changedTerm) }}</template>
        <template v-for="col in tableColumns.filter(c => c.key.startsWith('medal_'))" :key="col.key" v-slot:[`cell-${col.key}`]="{ item }">
          <span v-if="item[col.key]">{{ formatCountPercent(item[col.key]) }}</span><span v-else>0 (0.0%)</span>
        </template>
      </BaseTable>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container { display: flex; flex-direction: column; gap: 30px; padding-top: 20px; }
.stats-cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
.stat-card { background-color: var(--surface-color); border-radius: var(--border-radius); padding: 20px; display: flex; align-items: center; gap: 20px; box-shadow: var(--shadow-color) 0px 4px 12px; }
.card-icon { background-color: var(--background-color); color: var(--primary-color); width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0; }
.card-info { display: flex; flex-direction: column; gap: 5px; }
.card-title { color: var(--text-secondary); font-size: 0.9rem; }
.card-value { font-size: 1.5rem; font-weight: 700; }
.dashboard-table { margin-top: 10px; }
</style>