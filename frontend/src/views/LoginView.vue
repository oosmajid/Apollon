<script setup>
import { ref, onUnmounted } from 'vue' // onUnmounted را اضافه می‌کنیم
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const loginMode = ref('otp')
const step = ref(1)
const phoneNumber = ref('')
const password = ref('')
const otp = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

async function getOtp() {
    errorMessage.value = ''
    if (phoneNumber.value.length < 11) {
        errorMessage.value = 'لطفاً شماره تلفن صحیح را وارد کنید.'
        return
    }
    isLoading.value = true
    try {
        const response = await api.requestOtp(phoneNumber.value)
        console.log('OTP request successful:', response.data.message); // نمایش پیام موفقیت در کنسول مرورگر
        step.value = 2
        startTimer() // Start the countdown timer after successful OTP request
    } catch (error) {
        console.error('OTP request failed:', error);
        console.error('Error response:', error.response?.data);
        console.error('Error status:', error.response?.status);
        console.error('Error message:', error.message);
        errorMessage.value = 'خطایی در ارسال کد رخ داد.'
    } finally {
        isLoading.value = false
    }
}

async function handleLogin() {
    isLoading.value = true
    errorMessage.value = ''
    try {
        let response;
        if (loginMode.value === 'otp') {
            response = await api.verifyOtp(phoneNumber.value, otp.value)
        } else { // loginMode === 'password'
            response = await api.loginWithPassword({ 
                phone_number: phoneNumber.value, 
                password: password.value 
            })
        }

        // ذخیره توکن‌ها در localStorage
        localStorage.setItem('accessToken', response.data.access);
        localStorage.setItem('refreshToken', response.data.refresh);
        
        // انتقال کاربر به صفحه اصلی
        router.push({ name: 'all-students' })

    } catch (error) {
        errorMessage.value = 'اطلاعات وارد شده صحیح نیست. لطفاً مجدداً تلاش کنید.'
        console.error('Login failed:', error.response?.data || error.message);
    } finally {
        isLoading.value = false
    }
}

// --- جدید: منطق تایمر برای ارسال مجدد کد ---
const countdown = ref(30)
const timerId = ref(null)

function startTimer() {
  // اگر تایمر قبلی فعال بود، آن را پاک کن
  if (timerId.value) clearInterval(timerId.value)

  countdown.value = 30
  timerId.value = setInterval(() => {
    countdown.value--
    if (countdown.value === 0) {
      clearInterval(timerId.value)
    }
  }, 1000)
}

async function resendOtp() {
  console.log('Resending OTP to:', phoneNumber.value)
  errorMessage.value = ''
  otp.value = ''
  isLoading.value = true
  
  try {
    await api.requestOtp(phoneNumber.value)
    startTimer() // تایمر را مجددا شروع کن
  } catch (error) {
    console.error('Resend OTP failed:', error);
    errorMessage.value = 'خطایی در ارسال مجدد کد رخ داد.'
  } finally {
    isLoading.value = false
  }
}

// پاک کردن تایمر هنگام خروج از کامپوننت برای جلوگیری از نشت حافظه
onUnmounted(() => {
  if (timerId.value) clearInterval(timerId.value)
})
// --- پایان منطق تایمر ---


function editPhoneNumber() {
  step.value = 1
  otp.value = ''
  errorMessage.value = ''
  if (timerId.value) clearInterval(timerId.value) // توقف تایمر
}

function toggleMode(mode) {
  loginMode.value = mode
  errorMessage.value = ''
  password.value = ''
  otp.value = ''
  step.value = 1
  if (timerId.value) clearInterval(timerId.value) // توقف تایمر
}
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <h2 class="title">ورود به پنل رایان</h2>
        <p class="subtitle">برای ادامه وارد شوید.</p>

        <form v-if="loginMode === 'otp'" @submit.prevent="step === 1 ? getOtp() : handleLogin()">
          <div v-if="step === 1">
            <div class="form-group">
              <label for="phone-otp">شماره تلفن همراه</label>
              <div class="input-wrapper">
                <i class="fa-solid fa-mobile-screen-button"></i>
                <input
                  type="tel"
                  id="phone-otp"
                  v-model="phoneNumber"
                  placeholder="09123456789"
                  required
                />
              </div>
            </div>
            <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
            <button type="submit" class="btn btn-full" :disabled="isLoading">
              <span v-if="!isLoading">دریافت کد ورود</span>
              <i v-else class="fa-solid fa-spinner fa-spin"></i>
            </button>
          </div>

          <div v-if="step === 2">
            <div class="form-group">
              <label>کد تایید ارسال شده به شماره زیر را وارد کنید:</label>
              <div class="phone-display">
                <span>{{ phoneNumber }}</span>
                <button type="button" @click="editPhoneNumber" class="edit-btn">ویرایش</button>
              </div>
            </div>
            <div class="form-group">
              <label for="otp">کد تایید</label>
              <div class="input-wrapper">
                <i class="fa-solid fa-key"></i>
                <input type="text" id="otp" v-model="otp" placeholder="کد ۴ رقمی" required />
              </div>
            </div>
            <div class="resend-wrapper">
              <span v-if="countdown > 0" class="countdown-timer">
                دریافت مجدد کد تا {{ countdown }} ثانیه دیگر
              </span>
              <button v-else type="button" @click="resendOtp" class="resend-btn">
                دریافت دوباره کد
              </button>
            </div>
            <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
            <button type="submit" class="btn btn-full" :disabled="isLoading">
              <span v-if="!isLoading">ورود</span>
              <i v-else class="fa-solid fa-spinner fa-spin"></i>
            </button>
          </div>
        </form>

        <form v-if="loginMode === 'password'" @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="phone-pass">شماره تلفن همراه</label>
            <div class="input-wrapper">
              <i class="fa-solid fa-mobile-screen-button"></i>
              <input
                type="tel"
                id="phone-pass"
                v-model="phoneNumber"
                placeholder="09123456789"
                required
              />
            </div>
          </div>
          <div class="form-group">
            <label for="password">رمز عبور</label>
            <div class="input-wrapper">
              <i class="fa-solid fa-lock"></i>
              <input
                type="password"
                id="password"
                v-model="password"
                placeholder="••••••••"
                required
              />
            </div>
          </div>
          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
          <button type="submit" class="btn btn-full" :disabled="isLoading">
            <span v-if="!isLoading">ورود</span>
            <i v-else class="fa-solid fa-spinner fa-spin"></i>
          </button>
        </form>

        <div class="separator"></div>

        <button v-if="loginMode === 'otp'" @click="toggleMode('password')" class="toggle-mode-btn">
          ورود با رمز عبور
        </button>
        <button v-if="loginMode === 'password'" @click="toggleMode('otp')" class="toggle-mode-btn">
          ورود با کد یکبار مصرف
        </button>
      </div>
      <footer class="login-footer">
        &copy; {{ new Date().getFullYear() }} آکادمی هنرهای دیجیتال رایان
      </footer>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--background-color);
  direction: rtl;
}

.login-container {
  width: 100%;
  max-width: 420px;
  padding: 20px;
}

.login-card {
  background-color: var(--surface-color);
  padding: 40px;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-color) 0px 10px 30px -5px;
  text-align: center;
}

.title {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
  text-align: right;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.input-wrapper {
  position: relative;
}

.input-wrapper i {
  position: absolute;
  top: 50%;
  right: 15px;
  transform: translateY(-50%);
  color: var(--text-secondary);
  opacity: 0.7;
}

.input-wrapper input {
  width: 100%;
  height: 48px;
  padding: 10px 45px 10px 15px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
  font-family: 'Vazirmatn', sans-serif;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.input-wrapper input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(106, 90, 205, 0.2);
}

.btn-full {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 500;
}

.error-message {
  color: var(--danger-color);
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 10px;
  font-size: 0.9rem;
  margin-bottom: 20px;
  text-align: center;
}
[data-theme='dark'] .error-message {
  background-color: #451b1b;
  border-color: #7f1d1d;
}

.separator {
  height: 1px;
  background-color: var(--border-color);
  margin: 30px 0;
}

.toggle-mode-btn {
  background: none;
  border: none;
  color: var(--primary-color);
  font-family: 'Vazirmatn', sans-serif;
  font-size: 0.9rem;
  cursor: pointer;
  font-weight: 500;
}

.phone-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--background-color);
  padding: 10px 15px;
  border-radius: 8px;
  font-weight: 500;
}

.edit-btn {
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 0.8rem;
  cursor: pointer;
}

/* استایل‌های جدید برای تایمر و دکمه ارسال مجدد */
.resend-wrapper {
  text-align: left;
  margin-bottom: 20px;
  height: 20px; /* برای جلوگیری از پرش صفحه */
}
.countdown-timer {
  font-size: 0.9rem;
  color: var(--text-secondary);
}
.resend-btn {
  background: none;
  border: none;
  color: var(--primary-color);
  font-family: 'Vazirmatn', sans-serif;
  font-size: 0.9rem;
  cursor: pointer;
  font-weight: 500;
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  color: var(--text-secondary);
  font-size: 0.8rem;
}
</style>
