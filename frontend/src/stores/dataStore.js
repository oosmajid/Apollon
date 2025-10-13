// src/stores/dataStore.js

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/services/api' // سرویس API را import می‌کنیم

export const useDataStore = defineStore('data', () => {
    // داده‌ها را با آرایه‌های خالی مقداردهی اولیه می‌کنیم
    const students = ref([])
    const apollonyars = ref([])
    const terms = ref([])
    const courses = ref([])
    const groups = ref([])
    const medals = ref([])
    const discounts = ref([])

    // یک action برای دریافت تمام داده‌های اولیه
    async function fetchInitialData() {
        try {
            // درخواست‌ها را به صورت موازی ارسال می‌کنیم تا سریع‌تر انجام شوند
            const [
                profilesRes,
                coursesRes,
                termsRes,
                apollonyarsRes,
                groupsRes,
                medalsRes,
                discountsRes,
            ] = await Promise.all([
                api.getProfiles(),
                api.getCourses(),
                api.getTerms(),
                api.getApollonyars(),
                api.getGroups(),
                api.getMedals(),
                api.getDiscounts(),
            ]);

            // داده‌های دریافت شده را در state ذخیره می‌کنیم
            students.value = profilesRes.data; // توجه: ما پروفایل‌ها را در students ذخیره می‌کنیم
            courses.value = coursesRes.data;
            terms.value = termsRes.data;
            apollonyars.value = apollonyarsRes.data;
            groups.value = groupsRes.data;
            medals.value = medalsRes.data;
            discounts.value = discountsRes.data;

            console.log("Initial data loaded successfully!");
        } catch (error) {
            console.error("Failed to fetch initial data:", error);
            // اینجا می‌توانید منطق مدیریت خطا را اضافه کنید (مثلاً نمایش پیام به کاربر)
        }
    }

    // Computed properties شما (مانند studentsWithDetails) همچنان کار خواهند کرد
    // اما حالا با داده‌های زنده از بک‌اند
    const studentsWithDetails = computed(() => {
        // این بخش ممکن است نیاز به کمی تغییر داشته باشد تا با ساختار API هماهنگ شود
        // برای مثال، به جای student.course، باید از student.term.course استفاده کنید
        return students.value.map(profile => ({
            ...profile,
            // تبدیل ساختار API به ساختار مورد انتظار فرانت‌اند
            id: profile.user.id,
            name: `${profile.user.first_name} ${profile.user.last_name}`,
            phone: profile.user.phone_number,
            course: profile.term?.course?.name || '-',
            term: profile.term?.name || '-',
            apollonyar: profile.apollonyar?.first_name || '-',
            // ... بقیه فیلدها ...
        }));
    });

    return {
        students,
        apollonyars,
        terms,
        courses,
        groups,
        medals,
        discounts,
        fetchInitialData, // اکشن جدید را اکسپورت می‌کنیم
        studentsWithDetails,
    }
})