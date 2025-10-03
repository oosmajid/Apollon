<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  isReadOnly: { type: Boolean, default: false }, // پراپ جدید
})
const emit = defineEmits(['update:modelValue'])

const hoverRating = ref(0)

function setRating(rating) {
  if (props.isReadOnly) return // اگر فقط خواندنی بود، خارج شو
  if (props.modelValue === rating) {
    emit('update:modelValue', 0)
  } else {
    emit('update:modelValue', rating)
  }
}

function handleMouseEnter(star) {
  if (props.isReadOnly) return
  hoverRating.value = star
}
</script>

<template>
  <div class="star-rating" :class="{ 'read-only': isReadOnly }" @mouseleave="hoverRating = 0">
    <i
      v-for="star in 3"
      :key="star"
      class="fa-solid fa-star"
      :class="{ active: (hoverRating || modelValue) >= star }"
      @mouseenter="handleMouseEnter(star)"
      @click="setRating(star)"
    ></i>
  </div>
</template>

<style scoped>
.star-rating i {
  font-size: 1.8rem;
  color: var(--border-color);
  cursor: pointer;
  transition: color 0.2s;
  margin: 0 2px;
}
.star-rating i.active {
  color: var(--star-color);
}
/* استایل جدید برای حالت فقط خواندنی */
.star-rating.read-only {
  cursor: default;
}
</style>
