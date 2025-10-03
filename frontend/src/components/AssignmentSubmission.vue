<script setup>
import StarRating from './StarRating.vue'

defineProps({
  submission: Object,
  templateFiles: Array,
  isReadOnly: { type: Boolean, default: false }, // پراپ جدید
})

const findSubmittedFileForTemplate = (templateId, submittedFiles) => {
  return submittedFiles.find((file) => file.templateId === templateId)
}
</script>

<template>
  <div class="submission-wrapper">
    <div class="submission-header">
      <h4>نسخه ارسالی در تاریخ: {{ submission.date }}</h4>
    </div>

    <div class="content-grid">
      <div class="grid-column">
        <h5>فایل‌های الگو</h5>
        <div class="files-container">
          <div v-for="template in templateFiles" :key="template.id" class="file-row">
            <a :href="template.url" target="_blank" class="file-preview">
              <img :src="template.url" :alt="template.name" />
            </a>
          </div>
        </div>
      </div>

      <div class="grid-column">
        <h5>فایل‌های ارسالی هنرجو</h5>
        <div class="files-container">
          <div v-for="template in templateFiles" :key="template.id" class="file-row">
            <template v-if="findSubmittedFileForTemplate(template.id, submission.submittedFiles)">
              <a
                :href="findSubmittedFileForTemplate(template.id, submission.submittedFiles).url"
                target="_blank"
                class="file-preview"
              >
                <img
                  :src="findSubmittedFileForTemplate(template.id, submission.submittedFiles).url"
                  :alt="findSubmittedFileForTemplate(template.id, submission.submittedFiles).name"
                />
              </a>
            </template>
            <div v-else class="no-submission">
              <span>-</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="submission-footer">
      <div class="evaluation-section">
        <div class="form-group">
          <label :for="`feedback-${submission.version}`">یادداشت و توضیحات آپولون‌یار</label>
          <textarea
            :id="`feedback-${submission.version}`"
            v-model="submission.feedback"
            rows="3"
            placeholder="توضیحی ثبت نشده است..."
            :disabled="isReadOnly"
          ></textarea>
        </div>
        <div class="rating-group">
          <label>امتیاز</label>
          <StarRating v-model="submission.grade" :is-read-only="isReadOnly" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* --- کادر اصلی و زیبای هر نسخه --- */
.submission-wrapper {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 20px;
  margin-bottom: 20px;
  background-color: var(--background-color);
}
.submission-wrapper:last-child {
  margin-bottom: 0;
}

/* --- هدر --- */
.submission-header {
  text-align: center;
  padding-bottom: 15px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}
.submission-header h4 {
  font-weight: 500;
  margin: 0;
}
/* --- فوتر و بخش ارزیابی (تغییرات اصلی) --- */
.submission-footer {
  padding-top: 15px;
  margin-top: 20px;
  border-top: 1px solid var(--border-color);
}
.evaluation-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}
.form-group {
  flex-grow: 1;
}
.form-group label,
.rating-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--surface-color);
  font-family: 'Vazirmatn', sans-serif;
  resize: vertical;
}
/* استایل برای حالت غیرفعال */
.form-group textarea:disabled {
  background-color: var(--background-color);
  opacity: 0.8;
  cursor: not-allowed;
}
.rating-group {
  display: flex;
  flex-direction: column;
  align-items: center;
}
/* --- چیدمان دو ستونی محتوا --- */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  align-items: flex-start;
}
.grid-column h5 {
  text-align: center;
  margin-bottom: 15px;
  color: var(--text-secondary);
  font-weight: 400;
}
.files-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.file-row {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 120px;
}

/* --- استایل نمایش فایل‌ها --- */
.file-preview,
.no-submission {
  width: 120px;
  height: 120px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background-color: var(--surface-color);
}
.file-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.no-submission {
  color: var(--text-secondary);
  font-size: 1.5rem;
}
</style>
