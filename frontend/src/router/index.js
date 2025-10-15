import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import { useAuthStore } from '../stores/auth.js'

// کامپوننت‌های صفحات
import AllStudentsView from '../views/AllStudentsView.vue'
import MyCallsView from '../views/MyCallsView.vue'
import AssignmentsView from '../views/AssignmentsView.vue'
import StudentProfileView from '../views/StudentProfileView.vue'
import AdminView from '../views/AdminView.vue'
import TransactionsView from '../views/TransactionsView.vue'
import InstallmentTrackingView from '../views/InstallmentTrackingView.vue'
import DashboardView from '../views/DashboardView.vue'
import StudentSelfProfileView from '../views/StudentSelfProfileView.vue'
import LoginView from '../views/LoginView.vue'
import RegistrationView from '../views/RegistrationView.vue'
import LandingView from '../views/LandingView.vue'
import RedirectView from '../views/RedirectView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegistrationView,
      meta: { requiresGuest: true }
    },
    {
      path: '/course/photoshop', // می‌توانید این آدرس را به دلخواه تغییر دهید
      name: 'course-landing',
      component: LandingView,
    },
    {
      path: '/redirecting',
      name: 'redirecting',
      component: RedirectView,
    },
    {
      path: '/my-profile/:id',
      name: 'student-self-profile',
      component: StudentSelfProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'all-students',
          component: AllStudentsView,
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: DashboardView,
        },
        {
          path: 'my-calls',
          name: 'my-calls',
          component: MyCallsView,
        },
        {
          path: 'assignments',
          name: 'assignments',
          component: AssignmentsView,
        },
        {
          path: 'student/:id',
          name: 'student-profile',
          component: StudentProfileView,
        },
        {
          path: 'installments',
          name: 'installments',
          component: InstallmentTrackingView,
        },
        {
          path: 'transactions',
          name: 'transactions',
          component: TransactionsView,
        },
        {
          path: 'admin',
          name: 'admin',
          component: AdminView,
        },
      ],
    },
  ],
})

// Route guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if user is authenticated
  const isAuthenticated = authStore.checkAuth()
  
  // If route requires authentication and user is not authenticated
  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log('Access denied: Authentication required for', to.path)
    next({ name: 'login' })
    return
  }
  
  // If route requires guest (like login page) and user is authenticated
  if (to.meta.requiresGuest && isAuthenticated) {
    console.log('Redirecting authenticated user away from guest page')
    next({ name: 'all-students' })
    return
  }
  
  next()
})

export default router
