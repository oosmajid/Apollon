<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '@/stores/dataStore' // جدید: برای دسترسی به دوره‌ها و ترم‌ها

const dataStore = useDataStore() // جدید

const formData = ref({
  rulesAgreement: null,
  firstName: '',
  lastName: '',
  email: '', // جدید
  gender: null,
  phone: '',
  profilePicture: null,
  courseId: null, // جدید
  termId: null, // نامش از term تغییر کرد
  registrationTime: null,
  occupation: '',
  skillLevel: '', // نامش از photoshopLevel تغییر کرد
  learningReason: '',
  birthYear: '',
  birthMonth: '',
  birthDay: '',
  province: '',
  city: '',
  address: '',
  postalCode: '',
  registrationType: 'نقدی(یکجا)',
  acquaintanceDuration: '',
  acquaintanceSource: '',
  paymentAmount: '',
  paymentDate: '',
  paymentTime: '',
  paymentReceipts: [],
})

const showForm = ref(false)
const uploadedFiles = ref([])

// جدید: computed property برای فیلتر کردن ترم‌ها بر اساس دوره انتخابی
const availableTerms = computed(() => {
  if (!formData.value.courseId) {
    return []
  }
  return dataStore.terms.filter((term) => term.courseId === formData.value.courseId)
})

// جدید: ریست کردن ترم با تغییر دوره
function handleCourseChange() {
  formData.value.termId = null
}

function handleRulesSelection(agreed) {
  if (agreed) {
    showForm.value = true
  } else {
    alert('برای ثبت‌نام، لازم است با قوانین موافقت نمایید.')
    showForm.value = false
  }
}

function onFileChange(event) {
  const files = event.target.files
  uploadedFiles.value = Array.from(files)
  formData.value.paymentReceipts = uploadedFiles.value
}

function triggerFileInput(inputId) {
  document.getElementById(inputId).click()
}

function handleSubmit() {
  console.log('Form Submitted:', formData.value)
  alert('ثبت‌نام شما با موفقیت انجام شد. اطلاعات در کنسول مرورگر قابل مشاهده است.')
}
</script>

<template>
  <div class="registration-page">
    <div class="form-container">
      <header class="form-header">
        <img src="https://picsum.photos/80/80" alt="Rayan Academy Logo" class="logo" />
        <h1>فرم ثبت نام دوره</h1>
        <p>آکادمی هنری رایان - شماره ثبت ۲۲۴۹۸</p>
      </header>

      <div class="card intro-card">
        <p>
          قبل از ثبت‌نام در هریک از دوره های آکادمی رایان لازم است متن کامل قوانین و تعهدات متقابل
          دوره و هنرجویان را مطالعه نموده باشید، جهت مطالعه
          <a href="#" target="_blank">روی اینجا کلیک کنید</a>.
        </p>
        <small>زمان مورد نیاز: ۱۰ دقیقه</small>

        <div class="form-section rules-section">
          <label class="form-label">لطفا یک گزینه را انتخاب نمایید:</label>
          <div class="radio-group">
            <label>
              <input type="radio" name="rules" @change="handleRulesSelection(true)" />
              <span
                >متن کامل قوانین و تعهدات آپولون را خواندم و با آگاهی، قصد شرکت در دوره را
                دارم.</span
              >
            </label>
            <label>
              <input type="radio" name="rules" @change="handleRulesSelection(false)" />
              <span>قصد شرکت در دوره آپولون را ندارم.</span>
            </label>
          </div>
        </div>
      </div>

      <form v-if="showForm" @submit.prevent="handleSubmit">
        <div class="card">
          <h2 class="section-title">اطلاعات فردی</h2>
          <div class="grid-2">
            <div class="form-group">
              <label for="firstName" class="form-label">نام (به فارسی)</label>
              <input type="text" id="firstName" v-model="formData.firstName" required />
            </div>
            <div class="form-group">
              <label for="lastName" class="form-label">نام خانوادگی (به فارسی)</label>
              <input type="text" id="lastName" v-model="formData.lastName" required />
            </div>
          </div>
          <div class="form-group">
            <label for="email" class="form-label">ایمیل</label>
            <input type="email" id="email" v-model="formData.email" required />
          </div>
          <div class="form-group">
            <label class="form-label">... هستم!</label>
            <div class="radio-group horizontal">
              <label
                ><input type="radio" v-model="formData.gender" value="خانم" /><span
                  >خانم</span
                ></label
              >
              <label
                ><input type="radio" v-model="formData.gender" value="آقا" /><span>آقا</span></label
              >
            </div>
          </div>
          <div class="form-group">
            <label for="phone" class="form-label">شماره همراه در دسترس خودت</label>
            <p class="description">
              در ثبت شماره دقت کنید و شماره تماس اصلی خودتان را وارد کنید، تمامی امور مربوط به دوره
              شما از طریق این شماره قابل پیگیری خواهد بود. لطفا شماره همراه خود را بصورت یک عدد ۱۱
              رقمی با صفر ابتدای آن وارد کنید.
            </p>
            <input type="tel" id="phone" v-model="formData.phone" required />
          </div>
          <div class="form-group">
            <label class="form-label">یک عکس از خودتون اینجا بارگذاری کنید</label>
            <p class="description">جهت تکمیل پرونده شما در مدرسه رایان</p>
            <div class="file-uploader" @click="triggerFileInput('profilePicture')">
              <i class="fa-solid fa-camera"></i>
              <span>انتخاب عکس پروفایل</span>
            </div>
            <input type="file" id="profilePicture" hidden />
          </div>
        </div>

        <div class="card">
          <h2 class="section-title">اطلاعات دوره</h2>
          <div class="grid-2">
            <div class="form-group">
              <label for="course" class="form-label">قصد شرکت در کدام دوره را دارید؟</label>
              <select id="course" v-model="formData.courseId" @change="handleCourseChange" required>
                <option :value="null" disabled>ابتدا دوره را انتخاب کنید...</option>
                <option v-for="course in dataStore.courses" :key="course.id" :value="course.id">
                  {{ course.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="term" class="form-label">کدام یک از ترم‌های زیر؟</label>
              <select id="term" v-model="formData.termId" :disabled="!formData.courseId" required>
                <option :value="null" disabled>ابتدا دوره را انتخاب کنید...</option>
                <option v-for="term in availableTerms" :key="term.id" :value="term.id">
                  {{ term.name }} (شروع از {{ term.startDate }})
                </option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label"
              >زمان ثبت نام شما برای همین دوره هست یا دوره‌های قبل ثبت نام کردین و الان قصد شروع
              دوره‌تون رو دارین؟</label
            >
            <div class="radio-group">
              <label
                ><input type="radio" v-model="formData.registrationTime" value="current" /><span
                  >برای همین دوره ثبت نام کردم</span
                ></label
              >
              <label
                ><input type="radio" v-model="formData.registrationTime" value="previous" /><span
                  >در زمان دوره‌های قبل ثبت نام کردم ولی اولین بار است که وارد دوره میشوم</span
                ></label
              >
            </div>
          </div>
          <div class="form-group">
            <label for="occupation" class="form-label"
              >کمی درمورد شغل یا رشته تحصیلی فعلی خود بگویید</label
            >
            <p class="description">این سوال جهت آشنایی بهتر و نزدیکتر ما با شماست</p>
            <textarea id="occupation" v-model="formData.occupation" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label for="skillLevel" class="form-label"
              >سطح مهارت خود در حوزه دوره را چطور ارزیابی میکنید؟</label
            >
            <p class="description">
              اگر قبلا تجربه مرتبطی داشته‌اید، اینجا توضیحاتی درموردش بنویسید
            </p>
            <textarea id="skillLevel" v-model="formData.skillLevel" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label for="learningReason" class="form-label"
              >دلیل اصلی شما برای یادگیری این مهارت چیست؟</label
            >
            <textarea id="learningReason" v-model="formData.learningReason" rows="3"></textarea>
          </div>
        </div>

        <div class="card">
          <h2 class="section-title">اطلاعات تکمیلی</h2>
          <div class="grid-3">
            <div class="form-group">
              <label for="birthYear" class="form-label">سال تولد</label>
              <input
                type="text"
                id="birthYear"
                v-model="formData.birthYear"
                placeholder="مثال: 82"
              />
            </div>
            <div class="form-group">
              <label for="birthMonth" class="form-label">ماه تولد</label>
              <input
                type="text"
                id="birthMonth"
                v-model="formData.birthMonth"
                placeholder="مثال: فروردین"
              />
            </div>
            <div class="form-group">
              <label for="birthDay" class="form-label">روز تولد</label>
              <input type="text" id="birthDay" v-model="formData.birthDay" placeholder="مثال: 14" />
            </div>
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label for="province" class="form-label">استان محل سکونت</label>
              <input
                type="text"
                id="province"
                v-model="formData.province"
                placeholder="مثال: تهران"
              />
            </div>
            <div class="form-group">
              <label for="city" class="form-label">شهر/روستای محل سکونت</label>
              <input type="text" id="city" v-model="formData.city" placeholder="مثال: تهران" />
            </div>
          </div>
          <div class="form-group">
            <label for="address" class="form-label">آدرس کامل پستی محل سکونت</label>
            <p class="description">
              حتما با دقت این سوال را تکمیل نمایید چرا که پس از ثبت فرم امکان تغییر آدرس وجود ندارد.
            </p>
            <textarea id="address" v-model="formData.address" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label for="postalCode" class="form-label">کد پستی محل سکونت</label>
            <p class="description">اگر ساکن ایران نیستید، «زیپ کد» محل سکونتتان را وارد کنید.</p>
            <input type="text" id="postalCode" v-model="formData.postalCode" />
          </div>
        </div>

        <div class="card">
          <h2 class="section-title">اطلاعات ثبت نام</h2>
          <div class="form-group">
            <label class="form-label">نوع ثبت نام شما</label>
            <select v-model="formData.registrationType">
              <option>نقدی(یکجا)</option>
              <option>قسطی</option>
              <option>سایر</option>
            </select>
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">چه مدت هست که با ما آشنا شدی؟</label>
              <select v-model="formData.acquaintanceDuration">
                <option>کم تر از یک ماه</option>
                <option>بین یک ماه تا سه ماه</option>
                <option>بیشتر از سه ماه</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">اولین بار از چه طریقی با رایان آشنا شدی؟</label>
              <select v-model="formData.acquaintanceSource">
                <option>معرفی دوستان</option>
                <option>صفحه‌ی اینستاگرام</option>
                <option>کانال تلگرام</option>
                <option>کانال ایتا</option>
                <option>کانال بله</option>
                <option>یوتیوب</option>
                <option>تبلیغات آنلاین</option>
                <option>معرفی توسط مدرسه، دانشگاه یا محل کارتان</option>
                <option>سایر</option>
              </select>
            </div>
          </div>
        </div>

        <div class="card">
          <h2 class="section-title">اطلاعات پرداخت شما</h2>
          <div class="form-group">
            <label for="paymentAmount" class="form-label">مبلغ پرداخت شما</label>
            <p class="description">
              لطفا صرفا مبلغ پرداختی که تا کنون انجام دادید را با یک عدد به تومان وارد کنید. مثال:
              3300000
            </p>
            <input type="number" id="paymentAmount" v-model="formData.paymentAmount" />
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label for="paymentDate" class="form-label">تاریخ انجام پرداخت</label>
              <input
                type="date"
                id="paymentDate"
                v-model="formData.paymentDate"
                class="native-date-picker"
              />
            </div>
            <div class="form-group">
              <label for="paymentTime" class="form-label">ساعت انجام پرداخت</label>
              <input
                type="time"
                id="paymentTime"
                v-model="formData.paymentTime"
                class="native-date-picker"
              />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">آپلود عکس رسید</label>
            <p class="description">
              درصورتی که چند تراکنش پرداختی داشته اید عكس فيش همه‌ي آنها را بارگذاري نماييد
            </p>
            <div class="file-uploader" @click="triggerFileInput('paymentReceipts')">
              <i class="fa-solid fa-cloud-arrow-up"></i>
              <span>{{
                uploadedFiles.length > 0
                  ? `${uploadedFiles.length} فایل انتخاب شد`
                  : 'برای آپلود کلیک کنید یا فایل‌ها را بکشید'
              }}</span>
            </div>
            <input type="file" id="paymentReceipts" @change="onFileChange" multiple hidden />
            <div v-if="uploadedFiles.length > 0" class="files-list">
              <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
                {{ file.name }}
              </div>
            </div>
          </div>
        </div>

        <button type="submit" class="btn btn-submit">ثبت نهایی اطلاعات</button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.registration-page {
  background-color: var(--background-color);
  padding: 40px 20px;
  direction: rtl;
  min-height: 100vh;
}
.form-container {
  max-width: 800px;
  margin: 0 auto;
}
.form-header {
  text-align: center;
  margin-bottom: 30px;
}
.logo {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 15px;
}
.form-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}
.form-header p {
  color: var(--text-secondary);
  font-size: 1rem;
}
.card {
  background-color: var(--surface-color);
  border-radius: var(--border-radius);
  padding: 30px;
  margin-bottom: 25px;
  box-shadow: var(--shadow-color) 0px 7px 29px 0px;
}
.intro-card {
  text-align: center;
}
.intro-card p {
  line-height: 1.8;
  color: var(--text-secondary);
  margin-bottom: 15px;
}
.intro-card a {
  color: var(--primary-color);
  font-weight: 500;
  text-decoration: none;
}
.intro-card small {
  color: var(--text-secondary);
  opacity: 0.8;
}
.rules-section {
  border-top: 1px solid var(--border-color);
  margin-top: 25px;
  padding-top: 25px;
}
.section-title {
  font-size: 1.5rem;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}
.form-group {
  margin-bottom: 25px;
}
.form-label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-primary);
}
.description {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 10px;
}
input[type='text'],
input[type='email'],
input[type='tel'],
input[type='number'],
input[type='date'],
input[type='time'],
textarea,
select {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
  font-family: 'Vazirmatn', sans-serif;
  font-size: 1rem;
  transition:
    border-color 0.3s,
    box-shadow 0.3s;
}
input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(106, 90, 205, 0.1);
}
select:disabled {
  background-color: #e9ecef;
  opacity: 0.7;
  cursor: not-allowed;
}
textarea {
  resize: vertical;
}
.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
.radio-group label {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  cursor: pointer;
}
.radio-group input[type='radio'] {
  width: 1.2em;
  height: 1.2em;
  margin-left: 10px;
}
.radio-group.horizontal {
  display: flex;
  gap: 25px;
}
.file-uploader {
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius);
  padding: 25px;
  text-align: center;
  cursor: pointer;
  transition:
    border-color 0.3s,
    background-color 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 15px;
  background-color: var(--background-color);
}
.file-uploader:hover {
  border-color: var(--primary-color);
}
.file-uploader i {
  font-size: 2.5rem;
  color: var(--primary-color);
}
.file-uploader span {
  font-weight: 500;
  color: var(--text-secondary);
}
.files-list {
  margin-top: 15px;
}
.file-item {
  background-color: var(--background-color);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  margin-bottom: 5px;
}
.btn-submit {
  width: 100%;
  padding: 15px;
  font-size: 1.1rem;
  font-weight: 700;
  background-color: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
}
.btn-submit:hover {
  background-color: var(--primary-hover);
}
</style>
