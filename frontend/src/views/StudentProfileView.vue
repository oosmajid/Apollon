<script setup>
import { ref, computed, watchEffect, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLayoutStore } from '@/stores/layout.js'
import api from '@/services/api'
import MedalsGrid from '@/components/MedalsGrid.vue'
import BaseModal from '@/components/BaseModal.vue'
import BaseTable from '@/components/BaseTable.vue'
import HeartRating from '@/components/HeartRating.vue'
import AssignmentSubmission from '@/components/AssignmentSubmission.vue'
import DetailedProgressBar from '@/components/DetailedProgressBar.vue'
import dayjs from 'dayjs'
import jalali from 'dayjs-jalali'

dayjs.extend(jalali)
dayjs.locale('fa')

const layoutStore = useLayoutStore()
const route = useRoute()
const router = useRouter()

const studentId = parseInt(route.params.id)
const student = ref(null)
const studentAssignments = ref([])
const studentCalls = ref([])
const studentNotes = ref([])
const studentPaymentHistory = ref([])
const studentActionLogs = ref([])
const availableCourses = ref([])
const availableTerms = ref([])
const allTerms = ref([])
const termsInSameCourse = ref([])
const allApollonyars = ref([])
const callTopics = ref([])


// متغیر برای نگهداری ترم انتخاب‌شده فعلی
const selectedTermId = ref(null)
// متغیرهای مودال تایید حذف دوره
const isDeleteCourseModalOpen = ref(false)
const courseToRemove = ref(null)

// --- منطق مدیریت دوره‌ها ---
const isAddCourseModalOpen = ref(false)
const newEnrollment = ref({ courseId: '', termId: '' })


onMounted(async () => {
    // به محض باز شدن صفحه، تمام داده‌های مورد نیاز را از APIها فراخوانی می‌کنیم
    try {
        const profileRes = await api.getProfileDetails(studentId);
        student.value = profileRes.data;
        layoutStore.setPageTitle(`پروفایل: ${student.value.name}`);

        const [assignmentsRes, callsRes, notesRes, paymentsRes, coursesRes, termsRes, apollonyarsRes] = await Promise.all([
            api.getProfileAssignments(studentId),
            api.getProfileCalls(studentId),
            api.getProfileNotes(studentId),
            api.getProfilePayments(studentId),
            api.getCourses(),
            api.getTerms(),
            api.getApollonyars()
        ]);
        
        studentAssignments.value = assignmentsRes.data;
        studentCalls.value = callsRes.data;
        studentNotes.value = notesRes.data;
        studentPaymentHistory.value = paymentsRes.data;
        
        // Populate the ref arrays
        const allCourses = coursesRes.data;
        const allTermsData = termsRes.data;
        const allApollonyarsData = apollonyarsRes.data;
        
        // Store all terms for later use
        allTerms.value = allTermsData;
        
        // Calculate available courses (courses not enrolled in)
        const enrolledCourseIds = student.value.enrolledCourses.map((ec) => ec.courseId);
        availableCourses.value = allCourses.filter((c) => !enrolledCourseIds.includes(c.id));
        
        // Set all apollonyars
        allApollonyars.value = allApollonyarsData;
        
        // Calculate terms in same course
        if (student.value.courseId) {
            termsInSameCourse.value = allTermsData.filter((term) => term.courseId === student.value.courseId);
        }
        
        // Calculate call topics - will be updated when course changes
        callTopics.value = ['تماس انصراف', 'تماس پیگیری قسط', 'سایر'];
        
        // Load action logs
        await loadActionLogs();

    } catch (error) {
        console.error("Failed to load student profile data:", error);
        // اگر پروفایل پیدا نشد، کاربر را به صفحه دیگری منتقل کنید
    }
});

// These are now refs defined above

async function loadActionLogs() {
    try {
        const response = await api.getLogs();
        studentActionLogs.value = response.data;
    } catch (error) {
        console.error("Failed to load action logs:", error);
        studentActionLogs.value = [];
    }
}

function openAddCourseModal() {
  newEnrollment.value = { courseId: '', termId: '' }
  availableTerms.value = []
  isAddCourseModalOpen.value = true
}

// Function to update available terms when course is selected
function updateAvailableTerms() {
  if (!newEnrollment.value.courseId) {
    availableTerms.value = []
    return
  }
  // Get terms from allTerms ref that was loaded from API
  availableTerms.value = allTerms.value.filter((t) => t.courseId === newEnrollment.value.courseId)
}

async function handleAddCourse() {
  if (newEnrollment.value.courseId && newEnrollment.value.termId) {
    try {
      await api.addCourseToStudent(studentId, {
        courseId: newEnrollment.value.courseId,
        termId: newEnrollment.value.termId
      });
      
      // آپدیت کردن اطلاعات هنرجو
      const profileRes = await api.getProfileDetails(studentId);
      student.value = profileRes.data;
      
      isAddCourseModalOpen.value = false;
    } catch (error) {
      console.error("Failed to add course to student:", error);
      alert('خطا در افزودن دوره. لطفاً دوباره تلاش کنید.');
    }
  } else {
    alert('لطفاً هم دوره و هم ترم را انتخاب کنید.')
  }
}

function selectCourse(enrolledCourse) {
  selectedTermId.value = enrolledCourse.termId
}

function openDeleteCourseModal(enrolledCourse) {
  courseToRemove.value = enrolledCourse
  isDeleteCourseModalOpen.value = true
}

async function confirmRemoveCourse() {
  if (!courseToRemove.value) return

  try {
    await api.removeCourseFromStudent(studentId, courseToRemove.value.enrollmentId || courseToRemove.value.courseId);
    
    // آپدیت کردن اطلاعات هنرجو
    const profileRes = await api.getProfileDetails(studentId);
    student.value = profileRes.data;

    // اگر دوره حذف شده، دوره فعال بود، اولین دوره دیگر را فعال کن
    if (selectedTermId.value === courseToRemove.value.termId) {
      const remainingCourses = student.value.enrolledCourses.filter(
        (c) => c.courseId !== courseToRemove.value.courseId,
      )
      selectedTermId.value = remainingCourses.length > 0 ? remainingCourses[0].termId : null
    }

    isDeleteCourseModalOpen.value = false
    courseToRemove.value = null
  } catch (error) {
    console.error("Failed to remove course from student:", error);
    alert('خطا در حذف دوره. لطفاً دوباره تلاش کنید.');
  }
}

// --- منطق بخش پرداخت‌ها و ویرایش اقساط ---
const isEditInstallmentsModalOpen = ref(false)
const editableInstallments = ref([])
const validationError = ref('')
// >> جدید: متغیر برای نگهداری مبلغ کل قابل ویرایش
const editableTotalCourseFee = ref(0)

const totalPaid = computed(() => {
  return studentPaymentHistory.value
    .filter((i) => i.paymentStatus === 'پرداخت شده')
    .reduce((sum, i) => sum + (Number(String(i.amount).replace(/,/g, '')) || 0), 0)
})

function getReceiptUrl(transactionId) {
  if (!transactionId) return '#'
  // This should be handled by the backend - for now return a placeholder
  return `#transaction-${transactionId}`
}

const totalInstallmentsAmount = computed(() => {
  if (!editableInstallments.value) return 0
  return editableInstallments.value.reduce((sum, i) => {
    // فقط اقساطی که عودت نشده‌اند را جمع بزن
    if (i.paymentStatus !== 'عودت شده') {
      return sum + (Number(i.amount) || 0)
    }
    return sum
  }, 0)
})

function handleStatusChange(installment, newStatus) {
  if (installment.paymentStatus === newStatus) {
    // اگر کاربر روی چک‌باکس فعال کلیک کرد، آن را غیرفعال کن
    installment.paymentStatus = 'درآینده'
  } else {
    installment.paymentStatus = newStatus
  }
}

function openEditInstallmentsModal() {
  // کپی عمیق از اقساط برای ویرایش
  editableTotalCourseFee.value = student.value.totalCourseFee || 0

  editableInstallments.value = JSON.parse(
    JSON.stringify(studentPaymentHistory.value),
  ).map((i) => {
    // ۱. تبدیل اعداد فارسی در تاریخ به انگلیسی
    const persianMap = {
      '۰': '0',
      '۱': '1',
      '۲': '2',
      '۳': '3',
      '۴': '4',
      '۵': '5',
      '۶': '6',
      '۷': '7',
      '۸': '8',
      '۹': '9',
    }
    const normalizedDate = i.dueDate
      ? String(i.dueDate).replace(/[۰-۹]/g, (d) => persianMap[d])
      : ''

    // ۲. تبدیل تاریخ شمسی به میلادی برای نمایش در date picker
    if (normalizedDate) {
      const parsedDate = dayjs(normalizedDate, 'YYYY/MM/DD', 'fa')
      // <<< این خطوط مشکل را حل می‌کنند >>>
      // با تعیین locale به 'en'، از باگ پلاگین جلالی جلوگیری می‌کنیم
      i.dueDate = parsedDate.isValid() ? parsedDate.locale('en').format('YYYY-MM-DD') : ''
    } else {
      i.dueDate = ''
    }

    // ۳. تبدیل مبلغ از رشته با کاما به عدد خالص
    i.amount = Number(String(i.amount).replace(/,/g, '')) || 0

    return i
  })

  validationError.value = ''
  isEditInstallmentsModalOpen.value = true
}

function addInstallment() {
  const newInstallment = {
    id: `new_${Date.now()}`,
    studentId: studentId,
    dueDate: dayjs().locale('en').format('YYYY-MM-DD'),
    amount: 0,
    paymentStatus: 'درآینده',
    transactionId: null,
  }
  editableInstallments.value = [...editableInstallments.value, newInstallment]
}

function removeInstallment(index) {
  editableInstallments.value.splice(index, 1)
}

// src/views/StudentProfileView.vue

// src/views/StudentProfileView.vue

async function saveInstallments() {
  const totalCourseFee = editableTotalCourseFee.value
  if (totalInstallmentsAmount.value !== totalCourseFee) {
    validationError.value = `مجموع مبلغ اقساط (${totalInstallmentsAmount.value.toLocaleString('fa-IR')}) باید با کل مبلغ قابل پرداخت (${totalCourseFee.toLocaleString('fa-IR')}) برابر باشد.`
    return
  }

  try {
    // تبدیل تاریخ میلادی به شمسی قبل از ذخیره
    const finalInstallments = editableInstallments.value.map((i) => {
      if (i.dueDate && i.dueDate.includes('-')) {
        // <<< این خط مشکل را به طور کامل حل می‌کند >>>
        // ابتدا تاریخ را به تقویم جلالی تبدیل کرده و سپس فرمت می‌کنیم
        i.dueDate = dayjs(i.dueDate).calendar('jalali').format('YYYY/MM/DD')
      }
      return i
    })

    await api.updateStudentInstallments(studentId, {
      installments: finalInstallments,
      totalCourseFee: editableTotalCourseFee.value
    });

    // آپدیت کردن اطلاعات هنرجو و اقساط
    const [profileRes, paymentsRes] = await Promise.all([
      api.getProfileDetails(studentId),
      api.getProfilePayments(studentId)
    ]);
    
    student.value = profileRes.data;
    studentPaymentHistory.value = paymentsRes.data;
    
    isEditInstallmentsModalOpen.value = false;
  } catch (error) {
    console.error("Failed to update installments:", error);
    alert('خطا در به‌روزرسانی اقساط. لطفاً دوباره تلاش کنید.');
  }
}
// --- پایان منطق جدید ---

// --- Medals Modal ---
const isMedalModalOpen = ref(false)
const selectedMedal = ref(null)
const isAwardingMedal = ref(true)
function handleMedalClick(medal) {
  selectedMedal.value = medal
  isAwardingMedal.value = !student.value.earnedMedalIds.includes(medal.id)
  isMedalModalOpen.value = true
}
async function submitMedalAction() {
  try {
    if (isAwardingMedal.value) {
      await api.addMedalToStudent(studentId, { medalId: selectedMedal.value.id });
    } else {
      await api.removeMedalFromStudent(studentId, selectedMedal.value.id);
    }
    
    // آپدیت کردن اطلاعات هنرجو
    const profileRes = await api.getProfileDetails(studentId);
    student.value = profileRes.data;
    
    isMedalModalOpen.value = false
    selectedMedal.value = null
  } catch (error) {
    console.error("Failed to update student medal:", error);
    alert('خطا در به‌روزرسانی مدال. لطفاً دوباره تلاش کنید.');
  }
}

// --- Change Term Modal ---
const isChangeTermModalOpen = ref(false)
const previousTermChangesCount = ref(0)
// termsInSameCourse is now a ref defined above
function openChangeTermModal() {
  previousTermChangesCount.value = student.value.actionLogs.filter(
    (log) => log.action === 'تغییر ترم',
  ).length
  isChangeTermModalOpen.value = true
}
async function submitChangeTerm() {
  try {
    // این باید از فرم مودال گرفته شود
    const newTermId = document.getElementById('term-select')?.value;
    if (newTermId) {
      await api.changeStudentTerm(studentId, { 
        termId: newTermId,
        reason: document.getElementById('change-term-notes')?.value || ''
      });
      
      // آپدیت کردن اطلاعات هنرجو
      const profileRes = await api.getProfileDetails(studentId);
      student.value = profileRes.data;
    }
    
    isChangeTermModalOpen.value = false;
  } catch (error) {
    console.error("Failed to change student term:", error);
    alert('خطا در تغییر ترم. لطفاً دوباره تلاش کنید.');
  }
}

// --- Edit Apollonyar Modal ---
const isEditApollonyarModalOpen = ref(false)
// allApollonyars is now a ref defined above
function openEditApollonyarModal() {
  isEditApollonyarModalOpen.value = true
}
async function submitApollonyarChange() {
  try {
    const newApollonyarId = document.getElementById('apollonyar-select')?.value;
    if (newApollonyarId) {
      await api.changeStudentApollonyar(studentId, { 
        apollonyarId: newApollonyarId,
        reason: document.getElementById('apollonyar-notes')?.value || ''
      });
      
      // آپدیت کردن اطلاعات هنرجو
      const profileRes = await api.getProfileDetails(studentId);
      student.value = profileRes.data;
    }
    
    isEditApollonyarModalOpen.value = false;
  } catch (error) {
    console.error("Failed to change student apollonyar:", error);
    alert('خطا در تغییر آپولون‌یار. لطفاً دوباره تلاش کنید.');
  }
}

// --- Edit Student Type Modal ---
const isEditTypeModalOpen = ref(false)
const selectedType = ref('')
function openEditTypeModal() {
  selectedType.value = student.value.studentType
  isEditTypeModalOpen.value = true
}
async function submitTypeChange() {
  try {
    await api.changeStudentType(studentId, { 
      studentType: selectedType.value,
      reason: document.getElementById('type-notes')?.value || ''
    });
    
    // آپدیت کردن اطلاعات هنرجو
    const profileRes = await api.getProfileDetails(studentId);
    student.value = profileRes.data;
    
    isEditTypeModalOpen.value = false;
  } catch (error) {
    console.error("Failed to change student type:", error);
    alert('خطا در تغییر نوع هنرجو. لطفاً دوباره تلاش کنید.');
  }
}

// --- Edit Student Status Modal ---
const isEditStatusModalOpen = ref(false)
const selectedStatus = ref('')
function openEditStatusModal() {
  selectedStatus.value = student.value.status
  isEditStatusModalOpen.value = true
}
async function submitStatusChange() {
  try {
    await api.changeStudentStatus(studentId, { 
      status: selectedStatus.value,
      reason: document.getElementById('status-notes')?.value || ''
    });
    
    // آپدیت کردن اطلاعات هنرجو
    const profileRes = await api.getProfileDetails(studentId);
    student.value = profileRes.data;
    
    isEditStatusModalOpen.value = false;
  } catch (error) {
    console.error("Failed to change student status:", error);
    alert('خطا در تغییر وضعیت هنرجو. لطفاً دوباره تلاش کنید.');
  }
}

// --- Edit Profile Modal ---
const isEditProfileModalOpen = ref(false)
const editableProfile = ref(null) // ref جدید برای داده‌های قابل ویرایش

function openEditProfileModal() {
  // یک کپی از اطلاعات فعلی هنرجو ایجاد می‌کنیم تا تغییرات مستقیما اعمال نشود
  editableProfile.value = JSON.parse(JSON.stringify(student.value))
  isEditProfileModalOpen.value = true
}

async function submitProfileEdit() {
  try {
    await api.updateStudentProfile(studentId, editableProfile.value);
    
    // آپدیت کردن اطلاعات هنرجو
    const profileRes = await api.getProfileDetails(studentId);
    student.value = profileRes.data;
    
    isEditProfileModalOpen.value = false;
  } catch (error) {
    console.error("Failed to update student profile:", error);
    alert('خطا در به‌روزرسانی پروفایل. لطفاً دوباره تلاش کنید.');
  }
}

// --- Edit Assignment Due Date Modal ---
const isEditDueDateModalOpen = ref(false)
const selectedAssignmentForDueDate = ref(null)
const newDueDate = ref('')
function openEditDueDateModal(assignment) {
  selectedAssignmentForDueDate.value = assignment
  if (assignment && assignment.dueDate) {
    try {
      const persianMap = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
      }
      const normalizedDate = String(assignment.dueDate).replace(/[۰-۹]/g, (d) => persianMap[d])
      const parsedDate = dayjs(normalizedDate, 'YYYY/MM/DD', 'fa')
      if (parsedDate.isValid()) {
        newDueDate.value = parsedDate.format('YYYY-MM-DD')
      } else {
        newDueDate.value = ''
      }
    } catch (e) {
      console.error('Error parsing date: ', e)
      newDueDate.value = ''
    }
  } else {
    newDueDate.value = ''
  }
  isEditDueDateModalOpen.value = true
}
async function submitDueDateChange() {
  try {
    await api.updateAssignmentDueDate(selectedAssignmentForDueDate.value.id, { 
      dueDate: newDueDate.value,
      reason: document.getElementById('due-date-notes')?.value || ''
    });
    
    // آپدیت کردن تکالیف
    const assignmentsRes = await api.getProfileAssignments(studentId);
    studentAssignments.value = assignmentsRes.data;
    
    isEditDueDateModalOpen.value = false;
  } catch (error) {
    console.error("Failed to update assignment due date:", error);
    alert('خطا در به‌روزرسانی مهلت تکلیف. لطفاً دوباره تلاش کنید.');
  }
}

// --- Log Call Modal ---
const showLogCallModal = ref(false)
const newCallData = ref({ topic: '', description: '', isUnanswered: false })
// callTopics is now a ref defined above
function openLogCallModal() {
  newCallData.value = { topic: callTopics.value[0] || '', description: '', isUnanswered: false }
  showLogCallModal.value = true
}
async function submitLogCall() {
  try {
    await api.logCallForProfile(studentId, newCallData.value);
    
    // آپدیت کردن تماس‌ها
    const callsRes = await api.getProfileCalls(studentId);
    studentCalls.value = callsRes.data;
    
    showLogCallModal.value = false;
  } catch (error) {
    console.error("Failed to log call:", error);
    alert('خطا در ثبت تماس. لطفاً دوباره تلاش کنید.');
  }
}

// --- Details Modal for Calls & Logs ---
const isDetailsModalOpen = ref(false)
const detailsModalContent = ref({ title: '', description: '' })
function openDetailsModal(title, description) {
  detailsModalContent.value = {
    title,
    description: description || 'توضیحاتی برای این مورد ثبت نشده است.',
  }
  isDetailsModalOpen.value = true
}

// --- Delete Note Modal ---
const isDeleteNoteModalOpen = ref(false)
const noteToDelete = ref(null)
function openDeleteNoteModal(note) {
  noteToDelete.value = note
  isDeleteNoteModalOpen.value = true
}
async function confirmDeleteNote() {
  if (noteToDelete.value) {
    try {
      await api.removeNoteFromStudent(studentId, noteToDelete.value.id);
      
      // آپدیت کردن یادداشت‌ها
      const notesRes = await api.getProfileNotes(studentId);
      studentNotes.value = notesRes.data;
      
      isDeleteNoteModalOpen.value = false;
      noteToDelete.value = null;
    } catch (error) {
      console.error("Failed to delete note:", error);
      alert('خطا در حذف یادداشت. لطفاً دوباره تلاش کنید.');
    }
  }
}

// --- Add Note Modal ---
const isAddNoteModalOpen = ref(false)
const newNoteText = ref('')
function openAddNoteModal() {
  newNoteText.value = ''
  isAddNoteModalOpen.value = true
}
async function submitNewNote() {
  try {
    await api.addNoteToStudent(studentId, { 
      text: newNoteText.value
    });
    
    // آپدیت کردن یادداشت‌ها
    const notesRes = await api.getProfileNotes(studentId);
    studentNotes.value = notesRes.data;
    
    isAddNoteModalOpen.value = false;
  } catch (error) {
    console.error("Failed to add note:", error);
    alert('خطا در افزودن یادداشت. لطفاً دوباره تلاش کنید.');
  }
}

// --- Other computed properties and functions ---
const course = computed(() => {
  if (!student.value || !selectedTermId.value) return null
  const selectedEnrollment = student.value.enrolledCourses.find(
    (e) => e.termId === selectedTermId.value,
  )
  if (!selectedEnrollment) return null
  // This should be loaded from API - for now return null
  return null
})
watchEffect(() => {
  if (student.value) {
    layoutStore.setPageTitle(`پروفایل: ${student.value.name}`)
    // انتخاب اولین دوره به عنوان پیش‌فرض
    if (student.value.enrolledCourses && student.value.enrolledCourses.length > 0) {
      if (!selectedTermId.value) {
        selectedTermId.value = student.value.enrolledCourses[0].termId
      }
    }
  }
})
function goBack() {
  router.back()
}
const isModalOpen = ref(false)
const selectedAssignment = ref(null)
function openEvaluationModal(assignment) {
  const assignmentCopy = JSON.parse(JSON.stringify(assignment))
  if (assignmentCopy.submissions) {
    assignmentCopy.submissions.sort((a, b) => b.date.localeCompare(a.date))
  }
  selectedAssignment.value = assignmentCopy
  isModalOpen.value = true
}
function submitEvaluation() {
  isModalOpen.value = false
}
const progressPercent = computed(() => {
  if (!student.value || !student.value.totalWatchTime) return 0
  return (student.value.watchTime / student.value.totalWatchTime) * 100
})
const assignmentColumns = [
  { key: 'actions', label: '', sortable: false, filterable: false },
  { key: 'title', label: 'عنوان تکلیف' },
  { key: 'dueDate', label: 'مهلت ارسال' },
  { key: 'submissionDate', label: 'تاریخ ارسال' },
  { key: 'submissionCount', label: 'نسخه‌های ارسالی' },
  { key: 'status', label: 'وضعیت بررسی' },
  { key: 'grade', label: 'نمره', width: '100px' },
]
const callColumns = [
  { key: 'actions', label: '' },
  { key: 'topic', label: 'موضوع تماس' },
  { key: 'callDate', label: 'تاریخ تماس' }, // ستون جدید
  { key: 'daysRemaining', label: 'روزهای مانده' }, // ستون جدید
  { key: 'callStatus', label: 'وضعیت تماس' },
  { key: 'apollonyar', label: 'آپولون‌یار' },
]
const logColumns = [
  { key: 'actions', label: '' },
  { key: 'action', label: 'اقدام' },
  { key: 'timestamp_formatted', label: 'تاریخ و ساعت' },
  { key: 'issuer_name', label: 'توسط' },
  { key: 'description', label: 'توضیحات' },
]
const noteColumns = [
  { key: 'actions', label: '', width: '60px' },
  { key: 'date', label: 'تاریخ' },
  { key: 'note', label: 'یادداشت' },
  { key: 'author', label: 'نویسنده' },
]
</script>

<template>
  <div>
    <header class="page-header">
      <button @click="goBack" class="back-link">
        <i class="fa-solid fa-arrow-right"></i> بازگشت به صفحه قبلی
      </button>
    </header>
    <div v-if="student" class="profile-grid">
      <aside class="profile-sidebar">
        <div class="profile-card card">
          <div class="profile-image">
            <img src="https://picsum.photos/120/120" alt="عکس هنرجو" />
          </div>
          <div class="profile-name-header">
            <h2 class="profile-name">{{ student.name }}</h2>
            <button @click="openEditProfileModal" class="btn-icon">
              <i class="fa-solid fa-pen"></i>
            </button>
          </div>
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
          <div class="sidebar-actions">
            <button @click="openLogCallModal" class="btn">
              <i class="fa-solid fa-phone"></i> ثبت تماس
            </button>
          </div>
        </div>
        <div class="payments-card card">
          <div class="payments-header">
            <h4>پرداخت‌ها</h4>
            <button @click="openEditInstallmentsModal" class="btn-sm btn-outline">
              ویرایش اقساط
            </button>
          </div>
          <ul v-if="studentPaymentHistory.length" class="payment-list">
            <li v-for="payment in studentPaymentHistory" :key="payment.id" class="payment-item">
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
      <main class="profile-main">
        <div class="card">
          <div class="card-header">
            <h4>دوره‌های هنرجو</h4>
            <button @click="openAddCourseModal" class="btn-sm">
              <i class="fa-solid fa-plus"></i> افزودن دوره
            </button>
          </div>

          <ul v-if="student.enrolledCourses.length" class="courses-list">
            <li
              v-for="enrolledCourse in student.enrolledCourses"
              :key="enrolledCourse.courseId"
              class="course-item"
              :class="{ active: enrolledCourse.termId === selectedTermId }"
              @click="selectCourse(enrolledCourse)"
            >
              <div class="course-info">
                <span class="course-name">{{ enrolledCourse.courseName }}</span>
                <small class="term-name">{{ enrolledCourse.termName }}</small>
              </div>
              <div class="course-actions">
                <button
                  @click.stop="openDeleteCourseModal(enrolledCourse)"
                  class="btn-sm btn-icon-only btn-danger"
                  title="حذف دوره"
                >
                  <i class="fa-solid fa-trash-can"></i>
                </button>
              </div>
            </li>
          </ul>
          <p v-else class="no-data">هنرجو در هیچ دوره‌ای ثبت‌نام نشده است.</p>
        </div>
        <div class="stats-grid-container">
          <div class="stat-card card">
            <div class="card-title">
              <h4>نوع</h4>
              <button @click="openEditTypeModal" class="btn-icon">
                <i class="fa-solid fa-pen"></i>
              </button>
            </div>
            <p>
              <span class="status-bubble type">{{ student.studentType }}</span>
            </p>
          </div>
          <div class="stat-card card">
            <div class="card-title">
              <h4>وضعیت</h4>
              <button @click="openEditStatusModal" class="btn-icon">
                <i class="fa-solid fa-pen"></i>
              </button>
            </div>
            <p>
              <span class="status-bubble" :class="`status-${student.status}`">{{
                student.enrollmentStatus
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
            <div class="card-title">
              <h4>ترم</h4>
              <button @click="openChangeTermModal" class="btn-icon">
                <i class="fa-solid fa-pen"></i>
              </button>
            </div>
            <p>{{ student.term }}</p>
            <small class="term-dates">
              <i class="fa-solid fa-calendar-alt"></i>
              <span>{{ student.termStartDate }} تا {{ student.termEndDate }}</span>
            </small>
          </div>
          <div class="stat-card card">
            <div class="card-title">
              <h4>آپولون‌یار</h4>
              <button @click="openEditApollonyarModal" class="btn-icon">
                <i class="fa-solid fa-pen"></i>
              </button>
            </div>
            <p>{{ student.apollonyar }}</p>
            <small class="term-dates">
              <i class="fa-brands fa-telegram"></i>
              <span dir="ltr">{{ student.apollonyarTelegramId }}</span>
            </small>
          </div>
          <div class="stat-card card">
            <div class="card-title"><h4>جان</h4></div>
            <div class="icon-value-wrapper">
              <HeartRating :count="student.hearts" />
            </div>
          </div>
          <div class="stat-card card">
            <div class="card-title"><h4>امتیاز</h4></div>
            <div class="icon-value-wrapper">
              <p>{{ student.score }} <i class="fa-solid fa-star score-icon"></i></p>
            </div>
          </div>
        </div>
        <MedalsGrid
          :earned-medal-ids="student.earnedMedalIds"
          @medal-click="handleMedalClick"
        />
        <div class="progress-section card">
          <div class="progress-header">
            <h4>پیشرفت دوره</h4>
            <span class="total-progress-text">
              {{ student.watchTime }} از {{ student.totalWatchTime }} ساعت ({{
                Math.round(progressPercent)
              }}٪)
            </span>
          </div>
          <DetailedProgressBar
            v-if="course"
            :chapters="course.chapters"
            :progress-data="student.chapterProgress"
          />
        </div>
        <div class="card">
          <div class="card-header"><h4>تکالیف</h4></div>
          <BaseTable
            :columns="assignmentColumns"
            :data="studentAssignments"
            :rows-per-page="10"
            :row-class-fn="(item) => ({ 'overdue-row': item.isOverdue })"
          >
            <template #cell-actions="{ item }">
              <button
                @click="openEvaluationModal(item)"
                class="btn-sm btn-icon-only"
                :disabled="!item.submissionDate"
              >
                <i class="fa-solid fa-eye"></i>
              </button>
            </template>
            <template #cell-dueDate="{ item }">
              <div class="due-date-cell">
                <span>{{ item.dueDate }}</span>
                <button
                  type="button"
                  title="ویرایش مهلت"
                  @click.stop="openEditDueDateModal(item)"
                  class="btn-icon"
                >
                  <i class="fa-solid fa-pen"></i>
                </button>
              </div>
            </template>
            <template #cell-submissionDate="{ item }">
              <span v-if="item.submissionDate">{{ item.submissionDate }}</span>
              <span v-else class="status-badge not-submitted">ارسال نشده</span>
            </template>
            <template #cell-status="{ item }">
              <span
                v-if="item.status"
                class="status-badge"
                :class="item.status.includes('بررسی') ? 'checked' : 'not-checked'"
              >
                {{ item.status }}
              </span>
              <span v-else>-</span>
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
        <div class="card">
          <div class="card-header">
            <h4>تماس‌ها</h4>
            <button @click="openLogCallModal" class="btn-sm">
              <i class="fa-solid fa-phone"></i> ثبت تماس جدید
            </button>
          </div>
          <BaseTable :columns="callColumns" :data="studentCalls" :rows-per-page="10">
            <template #cell-actions="{ item }">
              <button
                @click="openDetailsModal('تماس: ' + item.topic, item.description)"
                class="btn-sm btn-icon-only"
                title="مشاهده توضیحات"
              >
                <i class="fa-solid fa-info-circle"></i>
              </button>
            </template>
            <template #cell-daysRemaining="{ item }">
              <span
                v-if="item.daysRemaining !== null"
                :class="item.daysRemaining < 0 ? 'days-past' : 'days-future'"
              >
                {{
                  item.daysRemaining < 0
                    ? `${Math.abs(item.daysRemaining)} روز گذشته`
                    : `${item.daysRemaining} روز مانده`
                }}
              </span>
              <span v-else>-</span>
            </template>
            <template #cell-callStatus="{ item }">
              <span class="status-badge" :class="`call-status-${item.callStatus}`">
                {{ item.callStatus }}
              </span>
            </template>
          </BaseTable>
        </div>
        <div class="card">
          <div class="card-header"><h4>لاگ اقدامات</h4></div>
          <BaseTable :columns="logColumns" :data="studentActionLogs" :rows-per-page="5">
            <template #cell-actions="{ item }">
              <button
                @click="openDetailsModal('اقدام: ' + item.action, item.description)"
                class="btn-sm btn-icon-only"
                title="مشاهده توضیحات"
              >
                <i class="fa-solid fa-eye"></i>
              </button>
            </template>
          </BaseTable>
        </div>
        <div class="card">
          <div class="card-header">
            <h4>یادداشت‌ها</h4>
            <button @click="openAddNoteModal" class="btn-sm">
              <i class="fa-solid fa-plus"></i> افزودن یادداشت
            </button>
          </div>
          <BaseTable :columns="noteColumns" :data="studentNotes" :rows-per-page="5">
            <template #cell-actions="{ item }">
              <button
                @click="openDeleteNoteModal(item)"
                class="btn-sm btn-icon-only btn-danger"
                title="حذف یادداشت"
              >
                <i class="fa-solid fa-trash-can"></i>
              </button>
            </template>
          </BaseTable>
          <BaseModal :show="isAddCourseModalOpen" @close="isAddCourseModalOpen = false">
            <template #header><h2>افزودن هنرجو به دوره جدید</h2></template>
            <form @submit.prevent="handleAddCourse" class="modal-form">
              <div class="form-group">
                <label for="course-select-modal">دوره را انتخاب کنید</label>
                <select id="course-select-modal" v-model="newEnrollment.courseId" @change="updateAvailableTerms" required>
                  <option disabled value="">یک دوره انتخاب کنید...</option>
                  <option v-for="course in availableCourses" :key="course.id" :value="course.id">
                    {{ course.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label for="term-select-modal">ترم مربوطه را انتخاب کنید</label>
                <select
                  id="term-select-modal"
                  v-model="newEnrollment.termId"
                  :disabled="!newEnrollment.courseId"
                  required
                >
                  <option disabled value="">یک ترم انتخاب کنید...</option>
                  <option v-for="term in availableTerms" :key="term.id" :value="term.id">
                    {{ term.name }}
                  </option>
                </select>
              </div>
              <div class="modal-actions">
                <button @click="isAddCourseModalOpen = false" type="button" class="btn-outline">
                  انصراف
                </button>
                <button type="submit" class="btn">افزودن</button>
              </div>
            </form>
          </BaseModal>
          <BaseModal :show="isDeleteCourseModalOpen" @close="isDeleteCourseModalOpen = false">
            <template #header><h2>تأیید حذف دوره</h2></template>
            <p v-if="courseToRemove">
              آیا از حذف دوره «{{ courseToRemove.courseName }}» برای این هنرجو اطمینان دارید؟
            </p>
            <div class="modal-actions">
              <button @click="isDeleteCourseModalOpen = false" class="btn-outline">انصراف</button>
              <button @click="confirmRemoveCourse" class="btn btn-danger">بله، حذف کن</button>
            </div>
          </BaseModal>
        </div>
      </main>
    </div>

    <div v-else><h2>هنرجو یافت نشد!</h2></div>

    <BaseModal :show="isMedalModalOpen" @close="isMedalModalOpen = false">
      <template #header>
        <h2 v-if="selectedMedal">{{ isAwardingMedal ? 'اعطای مدال' : 'حذف مدال' }}</h2>
      </template>
      <div v-if="selectedMedal" class="medal-modal-content">
        <i :class="selectedMedal.icon" class="modal-medal-icon"></i>
        <h3>{{ selectedMedal.name }}</h3>
        <p class="medal-description">{{ selectedMedal.description }}</p>
        <div class="form-group">
          <label>توضیحات (اختیاری)</label>
          <textarea rows="4" placeholder="دلیل خود را برای این اقدام بنویسید..."></textarea>
        </div>
        <button @click="submitMedalAction" class="btn" :class="{ 'btn-danger': !isAwardingMedal }">
          {{ isAwardingMedal ? 'ثبت' : 'حذف مدال' }}
        </button>
      </div>
    </BaseModal>
    <BaseModal :show="isModalOpen" @close="isModalOpen = false" size="lg">
      <template #header>
        <h2>ارزیابی تکلیف: {{ student.name }} - {{ selectedAssignment?.title }}</h2>
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
    <BaseModal :show="showLogCallModal" @close="showLogCallModal = false">
      <template #header><h2>ثبت تماس</h2></template>
      <form @submit.prevent="submitLogCall" class="modal-form">
        <div class="form-group">
          <label for="call-topic">عنوان تماس</label>
          <select id="call-topic" v-model="newCallData.topic">
            <option v-for="topic in callTopics" :key="topic" :value="topic">{{ topic }}</option>
          </select>
        </div>
        <div class="form-group">
          <label for="call-description">توضیحات</label>
          <textarea id="call-description" v-model="newCallData.description" rows="4"></textarea>
        </div>
        <div class="form-group-checkbox">
          <input type="checkbox" id="call-unanswered" v-model="newCallData.isUnanswered" />
          <label for="call-unanswered">تماس بی‌پاسخ بود</label>
        </div>
        <button type="submit" class="btn">ثبت</button>
      </form>
    </BaseModal>
    <BaseModal :show="isDetailsModalOpen" @close="isDetailsModalOpen = false">
      <template #header>
        <h2>{{ detailsModalContent.title }}</h2>
      </template>
      <p class="details-modal-description">{{ detailsModalContent.description }}</p>
    </BaseModal>
    <BaseModal :show="isDeleteNoteModalOpen" @close="isDeleteNoteModalOpen = false">
      <template #header>
        <h2>تأیید حذف یادداشت</h2>
      </template>
      <p>آیا از حذف این یادداشت اطمینان دارید؟ این عمل قابل بازگشت نیست.</p>
      <div class="modal-actions">
        <button @click="isDeleteNoteModalOpen = false" class="btn-outline">انصراف</button>
        <button @click="confirmDeleteNote" class="btn btn-danger">حذف</button>
      </div>
    </BaseModal>
    <BaseModal :show="isAddNoteModalOpen" @close="isAddNoteModalOpen = false">
      <template #header>
        <h2>افزودن یادداشت</h2>
      </template>
      <form @submit.prevent="submitNewNote" class="modal-form">
        <div class="form-group">
          <label for="new-note-text">متن یادداشت</label>
          <textarea id="new-note-text" v-model="newNoteText" rows="4" required></textarea>
        </div>
        <button type="submit" class="btn">ثبت</button>
      </form>
    </BaseModal>
    <BaseModal :show="isChangeTermModalOpen" @close="isChangeTermModalOpen = false">
      <template #header><h2>تغییر ترم</h2></template>
      <div v-if="student">
        <div class="modal-info-box">
          <div class="info-item">
            <span>ترم فعلی:</span> <strong>{{ student.term }}</strong>
          </div>
          <div class="info-item">
            <span>تغییرات قبلی:</span> <strong>{{ previousTermChangesCount }} بار</strong>
          </div>
        </div>
        <form @submit.prevent="submitChangeTerm" class="modal-form">
          <div class="form-group">
            <label for="term-select">ترم جدید</label>
            <select id="term-select" :value="student.termId">
              <option v-for="term in termsInSameCourse" :key="term.id" :value="term.id">
                {{ term.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="change-term-notes">توضیحات</label
            ><textarea
              id="change-term-notes"
              rows="4"
              placeholder="دلیل تغییر ترم را بنویسید..."
            ></textarea>
          </div>
          <button type="submit" class="btn">ثبت</button>
        </form>
      </div>
    </BaseModal>
    <BaseModal :show="isEditApollonyarModalOpen" @close="isEditApollonyarModalOpen = false">
      <template #header><h2>ویرایش آپولون‌یار</h2></template>
      <div v-if="student">
        <div class="modal-info-box">
          <div class="info-item">
            <span>آپولون‌یار فعلی:</span> <strong>{{ student.apollonyar }}</strong>
          </div>
        </div>
        <form @submit.prevent="submitApollonyarChange" class="modal-form">
          <div class="form-group">
            <label for="apollonyar-select">آپولون‌یار جدید</label>
            <select id="apollonyar-select" :value="student.apollonyarId">
              <option v-for="ap in allApollonyars" :key="ap.id" :value="ap.id">
                {{ ap.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="apollonyar-notes">توضیحات</label
            ><textarea id="apollonyar-notes" rows="4"></textarea>
          </div>
          <button type="submit" class="btn">ثبت</button>
        </form>
      </div>
    </BaseModal>
    <BaseModal :show="isEditTypeModalOpen" @close="isEditTypeModalOpen = false">
      <template #header><h2>ویرایش نوع</h2></template>
      <div v-if="student">
        <div class="modal-info-box">
          <div class="info-item">
            <span>نوع فعلی:</span> <strong>{{ student.studentType }}</strong>
          </div>
        </div>
        <form @submit.prevent="submitTypeChange" class="modal-form">
          <div class="form-group">
            <label>نوع جدید</label>
            <div class="toggle-switch-2">
              <button
                type="button"
                :class="{ active: selectedType === 'ترمی' }"
                @click="selectedType = 'ترمی'"
              >
                ترمی
              </button>
              <button
                type="button"
                :class="{ active: selectedType === 'خودخوان' }"
                @click="selectedType = 'خودخوان'"
              >
                خودخوان
              </button>
            </div>
          </div>
          <div class="form-group">
            <label for="type-notes">توضیحات</label><textarea id="type-notes" rows="4"></textarea>
          </div>
          <button type="submit" class="btn">ثبت</button>
        </form>
      </div>
    </BaseModal>
    <BaseModal :show="isEditStatusModalOpen" @close="isEditStatusModalOpen = false">
      <template #header><h2>ویرایش وضعیت</h2></template>
      <div v-if="student">
        <div class="modal-info-box">
          <div class="info-item">
            <span>وضعیت فعلی:</span> <strong>{{ student.enrollmentStatus }}</strong>
          </div>
        </div>
        <form @submit.prevent="submitStatusChange" class="modal-form">
          <div class="form-group">
            <label>وضعیت جدید</label>
            <div class="toggle-switch-3">
              <button
                type="button"
                :class="{ active: selectedStatus === 'آزاد' }"
                @click="selectedStatus = 'آزاد'"
              >
                آزاد
              </button>
              <button
                type="button"
                :class="{ active: selectedStatus === 'مسدود' }"
                @click="selectedStatus = 'مسدود'"
              >
                مسدود
              </button>
              <button
                type="button"
                :class="{ active: selectedStatus === 'انصراف' }"
                @click="selectedStatus = 'انصراف'"
              >
                انصراف
              </button>
            </div>
          </div>
          <div class="form-group">
            <label for="status-notes">توضیحات</label
            ><textarea id="status-notes" rows="4"></textarea>
          </div>
          <button type="submit" class="btn">ثبت</button>
        </form>
      </div>
    </BaseModal>
    <BaseModal :show="isEditProfileModalOpen" @close="isEditProfileModalOpen = false">
      <template #header><h2>ویرایش مشخصات هنرجو</h2></template>
      <form
        v-if="editableProfile"
        @submit.prevent="submitProfileEdit"
        class="modal-form profile-edit-form"
      >
        <div class="form-group profile-image-editor">
          <img src="https://picsum.photos/120/120" alt="عکس هنرجو" />
          <label for="profile-image-upload" class="edit-photo-btn">
            <i class="fa-solid fa-camera"></i>
            <input type="file" id="profile-image-upload" hidden />
          </label>
        </div>
        <div class="form-group">
          <label for="profile-name">نام و نام خانوادگی</label>
          <input type="text" id="profile-name" v-model="editableProfile.name" />
        </div>
        <div class="form-group">
          <label for="profile-phone">شماره تلفن</label>
          <input type="tel" id="profile-phone" v-model="editableProfile.phone" />
        </div>
        <div class="form-group">
          <label for="profile-birth-year">سال تولد</label>
          <input type="number" id="profile-birth-year" v-model="editableProfile.birthYear" />
        </div>
        <div class="form-group">
          <label for="profile-city">شهر</label>
          <input type="text" id="profile-city" v-model="editableProfile.city" />
        </div>
        <button type="submit" class="btn">ثبت تغییرات</button>
      </form>
    </BaseModal>
    <BaseModal :show="isEditDueDateModalOpen" @close="isEditDueDateModalOpen = false">
      <template #header><h2>ویرایش مهلت ارسال تکلیف</h2></template>
      <div v-if="selectedAssignmentForDueDate">
        <div class="modal-info-box">
          <div class="info-item">
            <span>تکلیف:</span>
            <strong>{{ selectedAssignmentForDueDate.title }}</strong>
          </div>
          <div class="info-item">
            <span>مهلت فعلی:</span>
            <strong>{{ selectedAssignmentForDueDate.dueDate }}</strong>
          </div>
        </div>
        <form @submit.prevent="submitDueDateChange" class="modal-form">
          <div class="form-group">
            <label for="new-due-date">مهلت جدید</label>
            <input type="date" id="new-due-date" v-model="newDueDate" class="native-date-picker" />
          </div>
          <div class="form-group">
            <label for="due-date-notes">توضیحات</label>
            <textarea
              id="due-date-notes"
              rows="4"
              placeholder="دلیل تغییر مهلت را بنویسید..."
            ></textarea>
          </div>
          <button type="submit" class="btn">ثبت</button>
        </form>
      </div>
    </BaseModal>
    <BaseModal
      :show="isEditInstallmentsModalOpen"
      @close="isEditInstallmentsModalOpen = false"
      size="lg"
    >
      <template #header
        ><h2>ویرایش اقساط: {{ student.name }}</h2></template
      >
      <div class="installments-modal">
        <div class="summary-bar">
          <div class="total-fee-editor">
            کل مبلغ قابل پرداخت:
            <input type="number" v-model="editableTotalCourseFee" class="total-fee-input" />
            <span>تومان</span>
          </div>
          <div>
            پرداخت شده:
            <strong class="success-text">{{ totalPaid.toLocaleString('fa-IR') }} تومان</strong>
          </div>
          <div>
            مجموع اقساط:
            <strong :class="{ 'error-text': totalInstallmentsAmount !== editableTotalCourseFee }"
              >{{ totalInstallmentsAmount.toLocaleString('fa-IR') }} تومان</strong
            >
          </div>
        </div>

        <p v-if="validationError" class="error-message">{{ validationError }}</p>

        <div class="installments-list-header">
          <span>تاریخ سررسید</span>
          <span>مبلغ</span>
          <span>وضعیت</span>
        </div>
        <div class="installments-list">
          <div
            v-for="(installment, index) in editableInstallments"
            :key="installment.id"
            class="installment-item"
            :class="{ locked: !!installment.transactionId }"
          >
            <div class="installment-row">
              <input
                type="date"
                v-model="installment.dueDate"
                :disabled="!!installment.transactionId"
                class="native-date-picker"
              />
              <input
                type="number"
                v-model="installment.amount"
                :disabled="!!installment.transactionId"
                placeholder="مبلغ (تومان)"
              />
              <div class="status-checkboxes">
                <label title="پرداخت شده">
                  <input
                    type="checkbox"
                    :checked="installment.paymentStatus === 'پرداخت شده'"
                    @change="handleStatusChange(installment, 'پرداخت شده')"
                    :disabled="!!installment.transactionId"
                  />
                  <i class="fa-solid fa-check"></i>
                  <span>پرداخت</span>
                </label>
                <label title="عودت شده">
                  <input
                    type="checkbox"
                    :checked="installment.paymentStatus === 'عودت شده'"
                    @change="handleStatusChange(installment, 'عودت شده')"
                    :disabled="!!installment.transactionId"
                  />
                  <i class="fa-solid fa-rotate-left"></i>
                  <span>عودت</span>
                </label>
              </div>
              <button
                @click="removeInstallment(index)"
                class="btn-icon-only-sm btn-danger"
                :disabled="!!installment.transactionId"
                title="حذف قسط"
              >
                <i class="fa-solid fa-trash-can"></i>
              </button>
            </div>

            <div
              v-if="
                installment.paymentStatus === 'پرداخت شده' ||
                installment.paymentStatus === 'عودت شده'
              "
              class="payment-details"
            >
              <input
                type="text"
                placeholder="شماره پیگیری"
                :disabled="!!installment.transactionId"
              />
              <input
                type="date"
                class="native-date-picker"
                :disabled="!!installment.transactionId"
              />
              <input
                type="time"
                class="native-date-picker"
                :disabled="!!installment.transactionId"
              />

              <template v-if="installment.transactionId">
                <a
                  :href="getReceiptUrl(installment.transactionId)"
                  target="_blank"
                  class="btn-sm btn-outline"
                  title="مشاهده رسید"
                >
                  <i class="fa-solid fa-eye"></i> رسید
                </a>
              </template>
              <template v-else>
                <label class="btn-sm btn-outline">
                  <i class="fa-solid fa-paperclip"></i> رسید
                  <input type="file" hidden />
                </label>
              </template>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="addInstallment" type="button" class="btn btn-outline">
            <i class="fa-solid fa-plus"></i> افزودن قسط جدید
          </button>
          <div class="spacer"></div>
          <button
            @click="isEditInstallmentsModalOpen = false"
            type="button"
            class="btn btn-outline"
          >
            انصراف
          </button>
          <button @click="saveInstallments" type="button" class="btn">ذخیره تغییرات</button>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<style scoped>
/* >> جدید: استایل برای فیلد ورودی مبلغ کل */
.total-fee-editor {
  display: flex;
  align-items: center;
  gap: 8px;
}
.total-fee-input {
  width: 140px;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background-color: var(--surface-color);
  text-align: center;
  font-weight: bold;
  font-size: 0.95rem;
}

/* استایل‌های مودال مدال */
.medal-modal-content {
  text-align: center;
}
.modal-medal-icon {
  font-size: 4rem;
  color: var(--star-color);
  margin-bottom: 15px;
}
.medal-modal-content h3 {
  font-size: 1.5rem;
  margin-bottom: 10px;
}
.medal-modal-content .form-group {
  text-align: right;
  margin-bottom: 20px;
}
.medal-description {
  background-color: var(--background-color);
  padding: 10px 15px;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.7;
  margin-bottom: 20px;
  text-align: justify;
}

/* استایل‌های کلی */
.card {
  background-color: var(--surface-color);
  border-radius: var(--border-radius);
  padding: 25px;
  box-shadow: var(--shadow-color) 0px 7px 29px 0px;
}
.page-header {
  margin-bottom: 25px;
}
.back-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}
.back-link i {
  margin-left: 8px;
}
.profile-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 30px;
}
.profile-main {
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
.profile-name-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}
.profile-name {
  margin-bottom: 0;
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
.sidebar-actions {
  margin-top: 25px;
  padding-top: 25px;
  border-top: 1px solid var(--border-color);
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
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  margin-bottom: 15px;
}
.stat-card .btn-icon {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 0.8rem;
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
.btn {
  border: none;
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
  font-size: 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: 'Vazirmatn', sans-serif;
}
.btn-icon {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 1rem;
}
.form-group {
  margin-bottom: 20px;
}
.form-group-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}
.form-group-checkbox label {
  cursor: pointer;
}
.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
}
.form-group select,
.form-group textarea,
.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
  font-family: 'Vazirmatn', sans-serif;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.btn-sm {
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.btn-icon-only {
  width: 32px;
  height: 32px;
  padding: 0;
  font-size: 1rem;
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
:deep(.overdue-row td) {
  background-color: #fff1f2 !important;
}
[data-theme='dark'] :deep(.overdue-row td) {
  background-color: #3f2226 !important;
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
.evaluation-footer {
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
  margin-top: 20px;
  text-align: center;
}
.btn-icon-only:disabled {
  background-color: var(--border-color);
  color: var(--text-secondary);
  cursor: not-allowed;
  opacity: 0.6;
}
.due-date-cell {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.due-date-cell .btn-icon {
  position: relative;
  z-index: 10;
}
.profile-name-header .btn-icon:hover,
.stat-card .btn-icon:hover,
.due-date-cell .btn-icon:hover {
  background-color: var(--primary-color);
  color: #fff;
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
.status-badge.call-status-موفق {
  background-color: var(--success-bg);
  color: var(--success-text);
}
.status-badge.call-status-بی‌پاسخ {
  background-color: #ffedd5;
  color: #9a3412;
}
.status-badge.call-status-در-آینده {
  background-color: #e5e7eb;
  color: #374151;
}
.status-badge.call-status-برای-انجام {
  background-color: #fef9c3;
  color: #854d0e;
}
.status-badge.call-status-سوخته {
  background-color: #fee2e2;
  color: #b91c1c;
}
.modal-info-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: var(--background-color);
  padding: 12px 15px;
  border-radius: 8px;
  margin-bottom: 25px;
  border: 1px solid var(--border-color);
}
.modal-info-box .info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-info-box span {
  font-size: 0.95rem;
  color: var(--text-secondary);
}
.toggle-switch-2,
.toggle-switch-3 {
  display: flex;
  background-color: var(--background-color);
  border-radius: 8px;
  padding: 4px;
  border: 1px solid var(--border-color);
}
.toggle-switch-2 button,
.toggle-switch-3 button {
  flex: 1;
  padding: 8px;
  border: none;
  background-color: transparent;
  cursor: pointer;
  border-radius: 6px;
  transition:
    background-color 0.2s,
    color 0.2s;
  font-family: 'Vazirmatn', sans-serif;
}
.toggle-switch-2 button.active,
.toggle-switch-3 button.active {
  background-color: var(--primary-color);
  color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  display: flex;
  align-items: center;
  justify-content: center;
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
.profile-edit-form .form-group {
  text-align: right;
}
.native-date-picker {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
  font-family: 'Vazirmatn', sans-serif;
  color: var(--text-primary);
  text-align: right;
}
.details-modal-description {
  line-height: 1.8;
  color: var(--text-secondary);
  white-space: pre-wrap;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}
.modal-actions .btn,
.modal-actions .btn-outline {
  width: auto;
  min-width: 100px;
}
.btn-danger {
  background-color: var(--danger-color);
  color: #fff;
}
.btn-danger:hover {
  background-color: #c13a3a;
}
.btn-icon-only.btn-danger {
  background-color: transparent;
  color: var(--danger-color);
}
.btn-icon-only.btn-danger:hover {
  background-color: var(--danger-color);
  color: #fff;
}
.btn-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.btn-outline:hover {
  background-color: var(--background-color);
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
.payment-status {
  display: flex;
  align-items: center;
  gap: 10px;
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
.summary-bar {
  display: flex;
  justify-content: space-around;
  align-items: center;
  background-color: var(--background-color);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 0.95rem;
  flex-wrap: wrap;
  gap: 15px;
}
.success-text {
  color: var(--success-text);
}
.error-text {
  color: var(--danger-color);
}
.error-message {
  color: var(--danger-color);
  background-color: #fee2e2;
  border-radius: 8px;
  padding: 10px 15px;
  font-size: 0.9rem;
  margin-bottom: 20px;
  text-align: center;
}
.installments-list {
  max-height: 40vh;
  overflow-y: auto;
  padding: 5px;
}
.installment-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto auto;
  gap: 15px;
  align-items: center;
  margin-bottom: 15px;
}
.installment-row.locked {
  opacity: 0.6;
}
.installment-row input {
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--surface-color);
}
.installment-row input:disabled {
  background-color: var(--background-color);
}
.status-tag {
  font-size: 0.8rem;
  color: var(--text-secondary);
  padding: 4px 10px;
  background: var(--background-color);
  border-radius: 6px;
  white-space: nowrap;
}
.btn-icon-only-sm {
  width: 36px;
  height: 36px;
  padding: 0;
  font-size: 0.9rem;
  border-radius: 8px;
  cursor: pointer;
}
.btn-icon-only-sm.btn-danger {
  background-color: #fee2e2;
  color: #b91c1c;
  border: none;
}
.btn-icon-only-sm.btn-danger:hover:not(:disabled) {
  background-color: var(--danger-color);
  color: #fff;
}
.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}
.modal-actions .spacer {
  flex-grow: 1;
}
.btn-outline {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.profile-sidebar {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* --- استایل‌های جدید برای مودال اقساط --- */
.installments-list-header {
  display: grid;
  grid-template-columns: 1fr 1fr 120px auto;
  gap: 15px;
  padding: 0 10px 8px 10px;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}
.installments-list-header span:nth-child(3) {
  text-align: center;
}

.installment-item {
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
  transition: background-color 0.2s;
}
.installment-item:hover {
  background-color: var(--background-color);
}
.installment-row {
  display: grid;
  grid-template-columns: 1fr 1fr 120px auto;
  gap: 15px;
  align-items: center;
}

.status-checkboxes {
  display: flex;
  justify-content: space-around;
  align-items: center;
}
.status-checkboxes label {
  cursor: pointer;
  position: relative;
  width: 36px;
  height: 36px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.status-checkboxes input[type='checkbox'] {
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
  visibility: hidden;
}
.status-checkboxes i {
  color: var(--text-secondary);
  font-size: 1.1rem;
  padding: 8px;
  border-radius: 50%;
  transition:
    background-color 0.2s,
    color 0.2s;
}
.status-checkboxes input:checked + i {
  color: #fff;
}
/* رنگ برای پرداخت شده */
.status-checkboxes label:first-child input:checked + i {
  background-color: var(--success-text);
}
/* رنگ برای عودت شده */
.status-checkboxes label:last-child input:checked + i {
  background-color: var(--danger-color);
}

.payment-details {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr auto;
  gap: 10px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--border-color);
}
.payment-details input {
  padding: 8px;
  font-size: 0.9rem;
  background-color: var(--background-color);
}
.payment-details .btn-sm {
  height: auto;
}
.payment-details .btn-sm:hover {
  height: auto;
  background-color: var(--border-color);
}
/* --- استایل‌های تکمیلی برای مودال اقساط --- */

/* استایل ردیف قفل شده (پرداخت شده) */
.installment-item.locked {
  background-color: var(--background-color);
}
.installment-item.locked .installment-row input,
.installment-item.locked .installment-row button,
.installment-item.locked .payment-details input {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none; /* غیرفعال کردن کلیک */
}
/* دکمه مشاهده رسید را فعال نگه می‌داریم */
.installment-item.locked .payment-details a.btn-sm {
  opacity: 1;
  cursor: pointer;
  pointer-events: auto;
}
.installment-item.locked input,
.installment-item.locked button {
  cursor: not-allowed !important;
}

/* استایل متن چک‌باکس‌ها */
.status-checkboxes label {
  flex-direction: column; /* چیدمان عمودی آیکون و متن */
  gap: 2px;
}
.status-checkboxes span {
  font-size: 9px;
  font-weight: 300;
  color: var(--text-secondary);
}
.status-checkboxes input:checked + i + span {
  color: var(--text-primary);
  font-weight: 500;
}

/* استایل دکمه رسید غیرفعال */
.payment-details .disabled-btn {
  background-color: var(--border-color);
  color: var(--text-secondary);
  border-color: var(--border-color);
}
.payment-details .disabled-btn:hover {
  background-color: var(--border-color);
  color: var(--text-secondary);
}
/* --- استایل‌های کارت مدیریت دوره‌ها --- */
.courses-management-card .courses-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 250px;
  overflow-y: auto;
  padding: 5px;
}
.courses-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--background-color);
  padding: 12px 15px;
  border-radius: 8px;
}
.course-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.course-name {
  font-weight: 500;
}
.term-name {
  font-size: 0.8rem;
  color: var(--text-secondary);
}
/* --- استایل‌های جدید کارت دوره‌ها --- */
.courses-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 250px;
  overflow-y: auto;
  padding: 5px;
}
.course-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--background-color);
  padding: 12px 15px;
  border-radius: 8px;
  border-right: 4px solid transparent;
  transition: all 0.2s ease-in-out;
}
.course-item.active {
  border-right-color: var(--primary-color);
  background-color: #e9e7f8;
}
[data-theme='dark'] .course-item.active {
  background-color: #2a2c4e;
}
.course-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.course-name {
  font-weight: 500;
}
.term-name {
  font-size: 0.8rem;
  color: var(--text-secondary);
}
.course-actions {
  display: flex;
  align-items: center;
}
.no-data {
  text-align: center;
  color: var(--text-secondary);
  padding: 20px 0;
}
/* --- استایل آیتم‌های قابل کلیک دوره --- */
.course-item {
  cursor: pointer;
}
.days-past {
  color: var(--danger-color);
  font-weight: 500;
}
.days-future {
  color: var(--success-text);
}
</style>
