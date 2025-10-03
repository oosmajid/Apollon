<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const course = {
  name: 'دوره جامع آپولون فتوشاپ',
  originalPrice: 5000000,
  description:
    'از صفر تا صد فتوشاپ را بیاموزید و به یک متخصص تبدیل شوید. این دوره برای ورود به بازار کار طراحی شده است.',
}

const discountCode = ref('')
const appliedDiscount = ref(0)
const phoneNumber = ref('')
const discountErrorMessage = ref('') // متغیر جدید فقط برای خطای تخفیف
const phoneErrorMessage = ref('') // متغیر جدید فقط برای خطای تلفن
const successMessage = ref('')

const finalPrice = computed(() => {
  return course.originalPrice - appliedDiscount.value
})

const isPhoneNumberValid = computed(() => {
  return phoneNumber.value.length === 11 && phoneNumber.value.startsWith('09')
})

function applyDiscount() {
  discountErrorMessage.value = '' // پاک کردن خطای قبلی تخفیف
  successMessage.value = ''
  if (discountCode.value.toUpperCase() === 'RAYAN50') {
    appliedDiscount.value = course.originalPrice * 0.5
    successMessage.value = 'کد تخفیف ۵۰٪ با موفقیت اعمال شد!'
  } else {
    appliedDiscount.value = 0
    discountErrorMessage.value = 'کد تخفیف وارد شده معتبر نیست.' // فقط متغیر خطای تخفیف پر می‌شود
  }
}

function proceedToPayment() {
  phoneErrorMessage.value = '' // پاک کردن خطای قبلی تلفن
  if (!isPhoneNumberValid.value) {
    phoneErrorMessage.value = 'لطفاً شماره تلفن صحیح را وارد کنید.' // فقط متغیر خطای تلفن پر می‌شود
    return
  }
  console.log('Redirecting to payment gateway for:', {
    phone: phoneNumber.value,
    finalPrice: finalPrice.value,
  })
  router.push({ name: 'redirecting' })
}
</script>

<template>
  <div class="landing-page">
    <header class="banner">
      <div class="banner-content">
        <h1>{{ course.name }}</h1>
        <p>{{ course.description }}</p>
        <a href="#payment-section" class="btn btn-cta">ثبت‌نام و شروع یادگیری</a>
      </div>
    </header>

    <main id="payment-section" class="main-content">
      <div class="payment-card">
        <h2 class="card-title">ثبت‌نام در دوره</h2>

        <div class="price-section">
          <div class="price-item">
            <span>مبلغ اصلی دوره</span>
            <span class="original-price"
              >{{ course.originalPrice.toLocaleString('fa-IR') }} تومان</span
            >
          </div>
          <div v-if="appliedDiscount > 0" class="price-item discount">
            <span>تخفیف</span>
            <span>{{ appliedDiscount.toLocaleString('fa-IR') }}- تومان</span>
          </div>
          <div class="price-item final-price">
            <span>مبلغ نهایی قابل پرداخت</span>
            <span>{{ finalPrice.toLocaleString('fa-IR') }} تومان</span>
          </div>
        </div>

        <div class="discount-section">
          <label for="discount">کد تخفیف دارید؟</label>
          <div class="input-group">
            <input type="text" id="discount" v-model="discountCode" placeholder="کد تخفیف" />
            <button @click="applyDiscount" class="btn btn-apply">اعمال</button>
          </div>
          <p v-if="successMessage" class="feedback-message success">{{ successMessage }}</p>
          <p v-if="discountErrorMessage" class="feedback-message error">
            {{ discountErrorMessage }}
          </p>
        </div>

        <div class="phone-section">
          <label for="phone">شماره تلفن همراه</label>
          <input
            type="tel"
            id="phone"
            v-model="phoneNumber"
            placeholder="برای تکمیل ثبت‌نام شماره خود را وارد کنید"
          />
          <p v-if="phoneErrorMessage" class="feedback-message error">{{ phoneErrorMessage }}</p>
        </div>

        <button @click="proceedToPayment" class="btn btn-submit" :disabled="!isPhoneNumberValid">
          پرداخت و ثبت‌نام نهایی
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.landing-page {
  background-color: var(--background-color);
  direction: rtl;
  font-family: 'Vazirmatn', sans-serif;
}
.banner {
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('https://picsum.photos/1600/800');
  background-size: cover;
  background-position: center;
  color: #fff;
  text-align: center;
  padding: 120px 20px;
}
.banner-content h1 {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 20px;
}
.banner-content p {
  font-size: 1.2rem;
  max-width: 600px;
  margin: 0 auto 30px;
  line-height: 1.7;
}
.btn-cta {
  background-color: var(--primary-color);
  color: #fff;
  padding: 15px 30px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  font-size: 1.1rem;
  transition: background-color 0.3s;
}
.btn-cta:hover {
  background-color: var(--primary-hover);
}
.main-content {
  padding: 60px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}
.payment-card {
  background-color: var(--surface-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-color) 0px 10px 30px -5px;
  width: 100%;
  max-width: 500px;
  padding: 30px;
}
.card-title {
  text-align: center;
  font-size: 1.8rem;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}
.price-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}
.price-item {
  display: flex;
  justify-content: space-between;
  font-size: 1rem;
  color: var(--text-secondary);
}
.price-item .original-price {
  text-decoration: line-through;
}
.price-item.discount {
  color: var(--success-text);
}
.price-item.final-price {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-top: 10px;
}
.discount-section,
.phone-section {
  margin-bottom: 30px;
}
.discount-section label,
.phone-section label {
  display: block;
  font-weight: 500;
  margin-bottom: 10px;
}
.input-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.input-group input {
  flex-grow: 1;
  height: 42px;
}
.btn-apply {
  height: 42px;
  padding: 0 20px;
  white-space: nowrap;
}
input[type='text'],
input[type='tel'] {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-family: 'Vazirmatn', sans-serif;
  font-size: 1rem;
}
.feedback-message {
  font-size: 0.9rem;
  margin-top: 10px;
  padding: 10px;
  border-radius: 6px;
}
.feedback-message.success {
  background-color: var(--success-bg);
  color: var(--success-text);
}
.feedback-message.error {
  background-color: #fee2e2;
  color: #b91c1c;
}
.btn-submit {
  width: 100%;
  padding: 15px;
  font-size: 1.1rem;
  font-weight: 700;
}
.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
