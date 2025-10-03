<script setup>
defineProps({
  submission: Object
});
</script>

<template>
  <div class="submission-container">
    <h4>نسخه ارسالی در تاریخ: {{ submission.date }}</h4>
    <div class="files-section">
      <h5>فایل‌های الگو</h5>
      <div class="files-grid">
        <a v-for="(file, i) in submission.templateFiles" :key="`t-${i}`" :href="file.url" target="_blank" class="file-item">
          <img v-if="file.type === 'image'" :src="file.url" :alt="file.name">
          <span v-else><i class="fa-solid fa-file-arrow-down"></i> {{ file.name }}</span>
        </a>
      </div>
    </div>
    <div class="files-section">
      <h5>فایل‌های ارسالی هنرجو</h5>
      <div class="files-grid">
        <a v-for="(file, i) in submission.submittedFiles" :key="`s-${i}`" :href="file.url" target="_blank" class="file-item">
          <img v-if="file.type === 'image'" :src="file.url" :alt="file.name">
          <span v-else><i class="fa-solid fa-file-arrow-down"></i> {{ file.name }}</span>
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.submission-container { border: 1px solid var(--border-color); border-radius: 8px; padding: 15px; margin-bottom: 15px; }
h4 { margin-bottom: 15px; }
h5 { color: var(--text-secondary); margin-bottom: 10px; }
.files-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.file-item { display: block; width: 100px; height: 100px; border-radius: 8px; overflow: hidden; border: 1px solid var(--border-color); text-decoration: none; color: var(--text-primary); }
.file-item img { width: 100%; height: 100%; object-fit: cover; }
.file-item span { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; text-align: center; padding: 5px; background-color: var(--background-color); }
.file-item span i { font-size: 1.5rem; margin-bottom: 8px; }
</style>