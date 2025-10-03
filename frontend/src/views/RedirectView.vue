<template>
  <div class="redirect-page">
    <div class="redirect-box">
      <i class="fa-solid fa-spinner fa-spin"></i>
      <h1>در حال انتقال به درگاه پرداخت</h1>
      <p>لطفاً کمی صبر کنید...</p>
    </div>
  </div>
</template>

<style scoped>
.redirect-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--background-color);
  direction: rtl;
}
.redirect-box {
  text-align: center;
  color: var(--text-secondary);
}
.redirect-box i {
  font-size: 3rem;
  color: var(--primary-color);
  margin-bottom: 25px;
}
.redirect-box h1 {
  font-size: 1.8rem;
  color: var(--text-primary);
  margin-bottom: 10px;
}
</style>
