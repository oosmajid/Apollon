import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

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
    },
    {
      path: '/register',
      name: 'register',
      component: RegistrationView,
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
    },
    {
      path: '/',
      component: MainLayout,
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

export default router
