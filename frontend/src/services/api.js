// src/services/api.js

import axios from 'axios';

// ساخت یک نمونه از axios با تنظیمات پیش‌فرض
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/', // آدرس پایه بک‌اند شما
    headers: {
        'Content-Type': 'application/json',
    },
});

// اضافه کردن Interceptor برای ارسال خودکار توکن
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// اکسپورت کردن توابع برای استفاده در کامپوننت‌ها
export default {
    loginWithPassword(credentials) {
        return apiClient.post('/auth/login/', credentials);
    },
    requestOtp(phone) {
        return apiClient.post('/auth/otp/request/', { phone_number: phone });
    },
    verifyOtp(phone, code) {
        return apiClient.post('/auth/otp/verify/', { phone_number: phone, code: code });
    },
    // --- توابع دریافت داده‌های اصلی ---
    getProfiles() {
        return apiClient.get('/profiles/');
    },
    getCourses() {
        return apiClient.get('/courses/');
    },
    getTerms() {
        return apiClient.get('/terms/');
    },
    getApollonyars() {
        return apiClient.get('/apollonyars/');
    },
    getGroups() {
        return apiClient.get('/groups/');
    },
    getMedals() {
        return apiClient.get('/medal-defs/');
    },
    getDiscounts() {
        return apiClient.get('/discount-codes/');
    },
    // ... بقیه توابع API را در آینده اینجا اضافه می‌کنیم ...
};