<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import BaseTable from '@/components/BaseTable.vue'
import BaseModal from '@/components/BaseModal.vue'
import dayjs from 'dayjs'
import api from '@/services/api'

const discounts = ref([])

// Load discounts data on mount
onMounted(async () => {
  try {
    const response = await api.getDiscounts()
    discounts.value = response.data
  } catch (error) {
    console.error("Failed to fetch discounts:", error)
  }
})

// --- وضعیت مودال‌ها ---
const showDiscountModal = ref(false)
const showDeleteModal = ref(false)
const isEditMode = ref(false)
const isUsageLimitUnlimited = ref(false)
const isExpiryUnlimited = ref(false) // <-- جدید: برای تاریخ انقضا

// --- داده‌های کد تخفیف فعلی ---
const currentDiscount = ref(null)

// --- واچر برای کنترل وضعیت نامحدود ---
watch(isUsageLimitUnlimited, (newVal) => {
  if (newVal && currentDiscount.value) {
    currentDiscount.value.usageLimit = '' // پاک کردن مقدار در صورت انتخاب نامحدود
  }
})
watch(isExpiryUnlimited, (newVal) => {
  if (newVal && currentDiscount.value) {
    currentDiscount.value.expiresAt = '' // پاک کردن تاریخ در صورت انتخاب نامحدود
  }
})

const tableColumns = [
  { key: 'code', label: 'کد', sortable: true, filterable: true },
  { key: 'percentage', label: 'درصد تخفیف', sortable: true },
  { key: 'createdAt', label: 'تاریخ ساخت', sortable: true },
  { key: 'usageCount', label: 'تعداد استفاده', sortable: true },
  { key: 'usageLimit', label: 'سقف استفاده', sortable: true },
  { key: 'expiresAt', label: 'تاریخ انقضا', sortable: true },
  { key: 'status', label: 'وضعیت', sortable: true, filterable: true },
  { key: 'actions', label: '', sortable: false },
]

function openAddModal() {
  isEditMode.value = false
  isUsageLimitUnlimited.value = false
  isExpiryUnlimited.value = true // <-- جدید: پیش‌فرض تاریخ نامحدود است
  currentDiscount.value = {
    code: '',
    percentage: 10,
    usageLimit: 100,
    expiresAt: '',
  }
  showDiscountModal.value = true
}

function openEditModal(discount) {
  isEditMode.value = true
  currentDiscount.value = JSON.parse(JSON.stringify(discount))

  // تبدیل تاریخ انقضا برای date picker
  if (currentDiscount.value.expiresAt) {
    const parsedDate = dayjs(currentDiscount.value.expiresAt, 'YYYY/MM/DD', 'fa')
    currentDiscount.value.expiresAt = parsedDate.isValid()
      ? parsedDate.locale('en').format('YYYY-MM-DD')
      : ''
  }

  isUsageLimitUnlimited.value = currentDiscount.value.usageLimit === null
  isExpiryUnlimited.value = currentDiscount.value.expiresAt === null
  showDiscountModal.value = true
}

async function handleSubmit() {
  try {
    if (isUsageLimitUnlimited.value) {
      currentDiscount.value.usageLimit = null
    }
    if (isExpiryUnlimited.value) {
      currentDiscount.value.expiresAt = null
    }

    if (isEditMode.value) {
      await api.updateDiscount(currentDiscount.value.id, currentDiscount.value)
      console.log('Discount updated successfully')
    } else {
      await api.createDiscount(currentDiscount.value)
      console.log('Discount created successfully')
    }
    // Refresh discounts data
    const response = await api.getDiscounts()
    discounts.value = response.data
    showDiscountModal.value = false
  } catch (error) {
    console.error('Failed to save discount:', error)
    alert('خطا در ذخیره کد تخفیف. لطفاً دوباره تلاش کنید.')
  }
}

async function handleDelete() {
  try {
    await api.deleteDiscount(currentDiscount.value.id)
    console.log('Discount deleted successfully')
    // Refresh discounts data
    const response = await api.getDiscounts()
    discounts.value = response.data
    showDeleteModal.value = false
    showDiscountModal.value = false
  } catch (error) {
    console.error('Failed to delete discount:', error)
    alert('خطا در حذف کد تخفیف. لطفاً دوباره تلاش کنید.')
  }
}

const modalTitle = computed(() => (isEditMode.value ? 'ویرایش کد تخفیف' : 'افزودن کد تخفیف جدید'))
</script>

<template>
  <div>
    <div class="pane-header">
      <h2>مدیریت کدهای تخفیف</h2>
      <button @click="openAddModal" class="btn">
        <i class="fa-solid fa-plus"></i> افزودن کد تخفیف جدید
      </button>
    </div>

    <BaseTable :columns="tableColumns" :data="discounts" :rows-per-page="10">
      <template #cell-percentage="{ item }">{{ item.percentage }}٪</template>
      <template #cell-usageLimit="{ item }">{{ item.usageLimit ?? 'نامحدود' }}</template>
      <template #cell-expiresAt="{ item }">{{ item.expiresAt ?? 'ندارد' }}</template>
      <template #cell-status="{ item }">
        <span
          class="status-bubble"
          :class="item.status === 'فعال' ? 'status-active' : 'status-expired'"
        >
          {{ item.status }}
        </span>
      </template>
      <template #cell-actions="{ item }">
        <button @click="openEditModal(item)" class="btn-sm">
          <i class="fa-solid fa-cogs"></i> ویرایش
        </button>
      </template>
    </BaseTable>

    <BaseModal :show="showDiscountModal" @close="showDiscountModal = false">
      <template #header
        ><h2>{{ modalTitle }}</h2></template
      >
      <form v-if="currentDiscount" @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label for="code">کد تخفیف (به حروف انگلیسی)</label>
          <input
            type="text"
            id="code"
            v-model="currentDiscount.code"
            @input="currentDiscount.code = $event.target.value.toUpperCase()"
            required
          />
        </div>

        <div class="form-group">
          <label for="percentage">درصد تخفیف: {{ currentDiscount.percentage }}٪</label>
          <input
            type="range"
            id="percentage"
            v-model="currentDiscount.percentage"
            min="0"
            max="100"
            class="slider"
          />
        </div>

        <div class="form-group">
          <label for="usageLimit">سقف تعداد استفاده</label>
          <div class="input-with-checkbox">
            <input
              type="number"
              id="usageLimit"
              v-model="currentDiscount.usageLimit"
              :disabled="isUsageLimitUnlimited"
            />
            <label class="checkbox-label">
              <input type="checkbox" v-model="isUsageLimitUnlimited" />
              <span>نامحدود</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label for="expiresAt">تاریخ انقضا</label>
          <div class="input-with-checkbox">
            <input
              type="date"
              id="expiresAt"
              v-model="currentDiscount.expiresAt"
              class="native-date-picker"
              :disabled="isExpiryUnlimited"
            />
            <label class="checkbox-label">
              <input type="checkbox" v-model="isExpiryUnlimited" />
              <span>بدون تاریخ</span>
            </label>
          </div>
        </div>

        <div class="modal-actions">
          <button
            v-if="isEditMode"
            @click.prevent="showDeleteModal = true"
            type="button"
            class="btn btn-danger-outline"
          >
            حذف
          </button>
          <div class="spacer"></div>
          <button @click="showDiscountModal = false" type="button" class="btn-outline">
            انصراف
          </button>
          <button type="submit" class="btn">{{ isEditMode ? 'ذخیره' : 'ثبت' }}</button>
        </div>
      </form>
    </BaseModal>

    <BaseModal :show="showDeleteModal" @close="showDeleteModal = false">
      <template #header><h2>تأیید حذف کد تخفیف</h2></template>
      <p v-if="currentDiscount">آیا از حذف کد «{{ currentDiscount.code }}» اطمینان دارید؟</p>
      <div class="modal-actions">
        <button @click="showDeleteModal = false" class="btn-outline">انصراف</button>
        <button @click="handleDelete" class="btn btn-danger">بله، حذف کن</button>
      </div>
    </BaseModal>
  </div>
</template>

<style scoped>
.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.status-bubble {
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 11px;
}
.status-bubble.status-active {
  background-color: var(--success-bg);
  color: var(--success-text);
}
.status-bubble.status-expired {
  background-color: #e5e7eb;
  color: #374151;
}
.modal-form .form-group {
  margin-bottom: 20px;
}
.modal-form label {
  /* display: block; */
  margin-bottom: 8px;
  color: var(--text-secondary);
}
.modal-form input[type='text'],
.modal-form input[type='number'],
.modal-form input[type='date'] {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--background-color);
  font-family: 'Vazirmatn', sans-serif;
  height: 42px; /* ثابت کردن ارتفاع */
}
.modal-form input:disabled {
  opacity: 0.5;
  background-color: #e9ecef;
}
.modal-form .slider {
  width: 100%;
  cursor: pointer;
}

/* --- استایل‌های جدید و بهبودیافته --- */
.input-with-checkbox {
  /* relative container so the label can be positioned inside the input */
  position: relative;
}
.input-with-checkbox input[type='number'],
.input-with-checkbox input[type='date'] {
  width: 100%;
  /* make room on the right for the inline checkbox label */
  padding-right: 130px; /* increased to accommodate label + separator */
  box-sizing: border-box;
}
.checkbox-label {
  /* place the checkbox label over the input on the right side */
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  display: inline-flex;
  flex-direction: row; /* ensure items lay out in a row */
  align-items: center; /* keeps checkbox vertically centered */
  gap: 10px; /* space between checkbox and text */
  flex-wrap: nowrap; /* prevent text from wrapping to next line */
  background-color: transparent; /* visually inside the input */
  border: none;
  /* subtle vertical separator to isolate the label from the input */
  border-left: 1px solid rgba(55, 65, 81, 0.08);
  height: 36px; /* match input height visually */
  padding: 0 10px 0 12px; /* left padding after separator plus right padding */
  cursor: pointer;
  white-space: nowrap;
  box-sizing: border-box;
  border-top-left-radius: 6px;
  border-bottom-left-radius: 6px;
}
.checkbox-label input[type='checkbox'] {
  /* slightly larger for touch targets and centered */
  width: 18px;
  height: 18px;
  margin: 0;
  display: inline-block; /* keep on same row with the text */
  flex: 0 0 auto;
  vertical-align: middle;
}

.checkbox-label span {
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis; /* if the label is too long, truncate with ellipsis */
  max-width: 120px; /* slightly larger to avoid wrapping */
}
.native-date-picker {
  text-align: right;
  color: var(--text-primary);
}
.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 25px;
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}
.modal-actions .spacer {
  flex-grow: 1;
}
.modal-actions .btn,
.modal-actions .btn-outline,
.modal-actions .btn-danger-outline {
  width: auto;
  min-width: 100px;
}
.btn-outline {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.btn-outline:hover {
  background-color: var(--primary-color);
  border: 1px solid var(--border-color);
  color: #fff;
}
.btn-danger-outline {
  background: transparent;
  border: 1px solid var(--danger-color);
  color: var(--danger-color);
}
.btn-danger-outline:hover {
  background-color: var(--danger-color);
  color: #fff;
}
.btn-danger {
  background-color: var(--danger-color);
  color: #fff;
}
</style>
