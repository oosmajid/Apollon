<script setup>
import { ref } from 'vue';

const props = defineProps({
  chapters: {
    type: Array,
    default: () => []
  },
  progressData: {
    type: Array,
    default: () => []
  }
});

// ۱. متغیرهای جدید برای کنترل نمایش و محتوای tooltip
const isTooltipVisible = ref(false);
const tooltipContent = ref('');
const tooltipStyle = ref({});

const segmentColors = [
  '#6a5acd', '#4682b4', '#3cb371', '#ffa500', '#ff6347',
  '#ba55d3', '#db7093', '#00ced1', '#ffd700', '#20b2aa',
  '#8a2be2', '#00fa9a', '#ff4500', '#ff8c00', '#2e8b57'
];

const getChapterProgress = (chapterId) => {
  const progress = props.progressData.find(p => p.chapterId === chapterId);
  return progress ? progress.progressPercent : 0;
};

const getWatchedHours = (chapter, progressPercent) => {
  return (chapter.duration * (progressPercent / 100)).toFixed(1);
};

// ۲. توابع جدید برای مدیریت رویدادهای موس
function showTooltip(event, chapter) {
  const progressPercent = getChapterProgress(chapter.id);
  const watchedHours = getWatchedHours(chapter, progressPercent);
  tooltipContent.value = `${chapter.name}\nکل ساعات: ${chapter.duration}\nساعات مشاهده شده: ${watchedHours} (${progressPercent}%)`;
  
  const rect = event.target.getBoundingClientRect();
  tooltipStyle.value = {
    left: `${rect.left + rect.width / 2}px`,
    top: `${rect.top - 10}px`, // کمی فاصله از بالای نوار
  };

  isTooltipVisible.value = true;
}

function hideTooltip() {
  isTooltipVisible.value = false;
}
</script>

<template>
  <div class="progress-bar-container">
    <div class="detailed-progress-bar">
      <div
        v-for="(chapter, index) in chapters"
        :key="chapter.id"
        class="segment-wrapper"
        :style="{ flex: chapter.duration }"
        @mouseenter="showTooltip($event, chapter)"
        @mouseleave="hideTooltip"
      >
        <div
          class="segment-fill"
          :style="{ 
            width: getChapterProgress(chapter.id) + '%',
            backgroundColor: segmentColors[index % segmentColors.length] 
          }"
        ></div>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="tooltip-fade">
        <div v-if="isTooltipVisible" class="custom-tooltip" :style="tooltipStyle">
          <div class="tooltip-content">{{ tooltipContent }}</div>
          <div class="tooltip-arrow"></div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
/* کانتینر اصلی را relative می‌کنیم تا tooltip موقعیت خود را نسبت به آن تنظیم کند */
.progress-bar-container {
  position: relative;
  width: 100%;
}

.detailed-progress-bar {
  display: flex;
  width: 100%;
  height: 25px;
  background-color: var(--background-color);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.segment-wrapper {
  height: 100%;
  background-color: var(--background-color);
  border-left: 1px solid var(--border-color);
  transition: filter 0.2s ease-in-out;
  border-radius: 2px;
  cursor: pointer;
}
.segment-wrapper:first-child {
  border-left: none;
}
.segment-wrapper:hover {
    filter: brightness(1.1);
}

.segment-fill {
  height: 100%;
  transition: width 0.5s ease-in-out;
  border-radius: 2px;
}

/* ۴. استایل‌های کامل و نهایی برای tooltip جدید */
.custom-tooltip {
  position: fixed;
  transform: translate(-50%, -100%);
  background-color: #2c3e50;
  color: #fff;
  padding: 10px 15px;
  border-radius: 8px;
  font-size: 0.85rem;
  z-index: 1000;
  pointer-events: none;
  white-space: pre-line; 
  text-align: center;
  width: 220px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.tooltip-arrow {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0; 
  height: 0; 
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid #2c3e50;
}

[data-theme="dark"] .custom-tooltip {
    background-color: #ecf0f1;
    color: #2c3e50;
}
[data-theme="dark"] .tooltip-arrow {
    border-top-color: #ecf0f1;
}

/* انیمیشن محو شدن */
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.2s ease;
}
.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
}
</style>