<script setup>
import { onMounted, computed, ref } from 'vue';
import { useLayoutStore } from '@/stores/layout.js';
import BaseTable from '@/components/BaseTable.vue';
import dayjs from 'dayjs';
import jalali from 'dayjs-jalali';
import api from '@/services/api';

dayjs.extend(jalali);
dayjs.locale('fa');

const layoutStore = useLayoutStore();
const students = ref([])
const apollonyars = ref([])
const terms = ref([])
const courses = ref([])
const calls = ref([])
const medals = ref([])

onMounted(async () => {
  layoutStore.setPageTitle('داشبورد');
  try {
    const [studentsRes, apollonyarsRes, termsRes, coursesRes, callsRes, medalsRes] = await Promise.all([
      api.getProfiles(),
      api.getApollonyars(),
      api.getTerms(),
      api.getCourses(),
      api.getCalls(),
      api.getMedals()
    ])
    students.value = studentsRes.data
    apollonyars.value = apollonyarsRes.data
    terms.value = termsRes.data
    courses.value = coursesRes.data
    calls.value = callsRes.data
    medals.value = medalsRes.data
  } catch (error) {
    console.error("Failed to fetch dashboard data:", error)
  }
});

// --- ۱. محاسبه داده‌های کارت‌های اطلاعات سریع ---
const statCards = computed(() => [
  { id: 1, title: "تماس‌های در انتظار", value: calls.value.filter(c => c.callStatus === 'برای انجام').length, icon: 'fa-solid fa-phone-volume' },
  { id: 2, title: "کل هنرجویان", value: students.value.length, icon: 'fa-solid fa-users' },
  { id: 3, title: "شاخص سوم", value: 'N/A', icon: 'fa-solid fa-chart-pie' },
  { id: 4, title: "شاخص چهارم", value: 'N/A', icon: 'fa-solid fa-chart-line' },
  { id: 5, title: "شاخص پنجم", value: 'N/A', icon: 'fa-solid fa-gauge-high' },
]);

// Transform students data for dashboard
const studentsWithDetails = computed(() => {
  return students.value.map(profile => ({
    ...profile,
    id: profile.user?.id || profile.id,
    name: `${profile.user?.first_name || ''} ${profile.user?.last_name || ''}`.trim() || profile.name,
    phone: profile.user?.phone_number || profile.phone,
    course: profile.term?.course?.name || '-',
    term: profile.term?.name || '-',
    apollonyar: profile.apollonyar?.first_name || '-',
    group: profile.group?.name || '-',
    apollonyarId: profile.apollonyar?.id,
    termId: profile.term?.id,
    status: profile.status || 'آزاد',
    studentType: profile.student_type || 'عادی',
    accessStatus: profile.access_status || 'فعال',
  }))
})

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
  
  const uniqueCombinations = studentsWithDetails.value.reduce((acc, student) => {
    if (student.apollonyarId && student.termId) {
      const key = `${student.apollonyarId}-${student.termId}`;
      if (!acc[key]) acc[key] = { apollonyarId: student.apollonyarId, termId: student.termId };
    }
    return acc;
  }, {});

  return Object.values(uniqueCombinations).map(combo => {
    const relevantStudents = studentsWithDetails.value.filter(s => s.apollonyarId === combo.apollonyarId && s.termId === combo.termId);
    const studentsAtStart = relevantStudents.length;
    if (studentsAtStart === 0) return null;

    const apollonyarInfo = apollonyars.value.find(a => a.id === combo.apollonyarId);
    const termInfo = terms.value.find(t => t.id === combo.termId);
    const courseInfo = courses.value.find(c => c.id === termInfo?.courseId);

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
      toDoCalls: calls.value.filter(c => c.apollonyarId === combo.apollonyarId && c.termId === combo.termId && c.callStatus === 'برای انجام').length,
      burntCalls: calls.value.filter(c => c.apollonyarId === combo.apollonyarId && c.termId === combo.termId && c.callStatus === 'سوخته').length,
      studentsAtStart,
      currentActiveStudents: { count: currentActiveStudents, percent: calculatePercentage(currentActiveStudents, studentsAtStart) },
      inactiveInstallment: { count: inactiveInstallment, percent: calculatePercentage(inactiveInstallment, studentsAtStart) },
      inactiveAssignment: { count: inactiveAssignment, percent: calculatePercentage(inactiveAssignment, studentsAtStart) },
      droppedOut: { count: droppedOut, percent: calculatePercentage(droppedOut, studentsAtStart) },
      changedTerm: { count: changedTerm, percent: calculatePercentage(changedTerm, studentsAtStart) },
    };
    medals.value.forEach(medal => {
      const count = relevantStudents.filter(s => s.earnedMedalIds?.includes(medal.id)).length;
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
  const medalColumns = medals.value.map(medal => ({ key: `medal_${medal.id}`, label: `دارای مدال ${medal.name}` }));
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