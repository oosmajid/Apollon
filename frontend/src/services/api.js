// src/services/api.js

import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/',
    headers: {
        'Content-Type': 'application/json',
    },
});

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

export default {
    // --- Auth ---
    loginWithPassword(credentials) {
        return apiClient.post('/auth/login/', credentials);
    },
    requestOtp(phone) {
        return apiClient.post('/auth/otp/request/', { phone_number: phone });
    },
    verifyOtp(phone, code) {
        return apiClient.post('/auth/otp/verify/', { phone_number: phone, code: code });
    },

    // --- Admin Panel CRUD ---
    // Courses
    getCourses() { return apiClient.get('/courses/'); },
    createCourse(courseData) { return apiClient.post('/courses/', courseData); },
    updateCourse(courseId, courseData) { return apiClient.patch(`/courses/${courseId}/`, courseData); },
    deleteCourse(courseId) { return apiClient.delete(`/courses/${courseId}/`); },
    
    // Terms
    getTerms() { return apiClient.get('/terms/'); },
    createTerm(termData) { return apiClient.post('/terms/', termData); },
    updateTerm(termId, termData) { return apiClient.patch(`/terms/${termId}/`, termData); },
    deleteTerm(termId) { return apiClient.delete(`/terms/${termId}/`); },
    
    // Apollonyars
    getApollonyars() { return apiClient.get('/apollonyars/'); },
    createApollonyar(apollonyarData) { return apiClient.post('/apollonyars/', apollonyarData); },
    updateApollonyar(apollonyarId, apollonyarData) { return apiClient.patch(`/apollonyars/${apollonyarId}/`, apollonyarData); },
    deleteApollonyar(apollonyarId) { return apiClient.delete(`/apollonyars/${apollonyarId}/`); },
    
    // Groups
    getGroups() { return apiClient.get('/groups/'); },
    createGroup(groupData) { return apiClient.post('/groups/', groupData); },
    updateGroup(groupId, groupData) { return apiClient.patch(`/groups/${groupId}/`, groupData); },
    deleteGroup(groupId) { return apiClient.delete(`/groups/${groupId}/`); },
    
    // Medals
    getMedals() { return apiClient.get('/medal-defs/'); },
    createMedal(medalData) { return apiClient.post('/medal-defs/', medalData); },
    updateMedal(medalId, medalData) { return apiClient.patch(`/medal-defs/${medalId}/`, medalData); },
    deleteMedal(medalId) { return apiClient.delete(`/medal-defs/${medalId}/`); },
    
    // Discounts
    getDiscounts() { return apiClient.get('/discounts/'); },
    createDiscount(discountData) { return apiClient.post('/discounts/', discountData); },
    updateDiscount(discountId, discountData) { return apiClient.patch(`/discounts/${discountId}/`, discountData); },
    deleteDiscount(discountId) { return apiClient.delete(`/discounts/${discountId}/`); },

    // --- Profiles & Students ---
    getProfiles() {
        return apiClient.get('/profiles/');
    },
    createProfile(profileData) {
        return apiClient.post('/profiles/', profileData);
    },
    getProfileDetails(id) {
        return apiClient.get(`/profiles/${id}/`);
    },
    deleteProfile(id) {
        return apiClient.delete(`/profiles/${id}/`);
    },
    // API های اختصاصی هر پروفایل
    getProfileAssignments(profileId) {
        return apiClient.get(`/profiles/${profileId}/assignments/`);
    },
    getProfileCalls(profileId) {
        return apiClient.get(`/profiles/${profileId}/calls/`);
    },
    getProfileNotes(profileId) {
        return apiClient.get(`/profiles/${profileId}/notes/`);
    },

    // --- Interactions ---
    logCallForProfile(profileId, callData) {
        return apiClient.post(`/profiles/${profileId}/log_call/`, callData);
    },
    addNoteForProfile(profileId, noteData) {
        return apiClient.post(`/profiles/${profileId}/add_note/`, noteData);
    },
    getAssignments() {
        return apiClient.get('/assignments/');
    },
    submitAssignment(assignmentId, submissionData) {
        // این بخش به دلیل آپلود فایل کمی پیچیده‌تر است و بعدا تکمیل می‌شود
        return apiClient.post(`/assignments/${assignmentId}/submit/`, submissionData, {
             headers: { 'Content-Type': 'multipart/form-data' }
        });
    },
    gradeSubmission(submissionId, gradeData) {
        return apiClient.post(`/submissions/${submissionId}/grade/`, gradeData);
    },

    // --- Financial ---
    getTransactions() {
        return apiClient.get('/transactions/');
    },
    getInstallments() {
        return apiClient.get('/installments/');
    },
    verifyTransaction(transactionId, data) {
        return apiClient.patch(`/transactions/${transactionId}/`, data);
    },
    addTransactionNote(transactionId, noteData) {
        return apiClient.post(`/transactions/${transactionId}/notes/`, noteData);
    },

    // --- Student Profile Management ---
    updateStudentProfile(profileId, profileData) {
        return apiClient.patch(`/profiles/${profileId}/`, profileData);
    },
    addCourseToStudent(profileId, courseData) {
        return apiClient.post(`/profiles/${profileId}/enrollments/`, courseData);
    },
    removeCourseFromStudent(profileId, enrollmentId) {
        return apiClient.delete(`/profiles/${profileId}/enrollments/${enrollmentId}/`);
    },
    addMedalToStudent(profileId, medalData) {
        return apiClient.post(`/profiles/${profileId}/medals/`, medalData);
    },
    removeMedalFromStudent(profileId, medalId) {
        return apiClient.delete(`/profiles/${profileId}/medals/${medalId}/`);
    },
    addNoteToStudent(profileId, noteData) {
        return apiClient.post(`/profiles/${profileId}/notes/`, noteData);
    },
    removeNoteFromStudent(profileId, noteId) {
        return apiClient.delete(`/profiles/${profileId}/notes/${noteId}/`);
    },
    updateStudentInstallments(profileId, installmentsData) {
        return apiClient.patch(`/profiles/${profileId}/installments/`, installmentsData);
    },
    changeStudentTerm(profileId, termData) {
        return apiClient.patch(`/profiles/${profileId}/change_term/`, termData);
    },
    changeStudentApollonyar(profileId, apollonyarData) {
        return apiClient.patch(`/profiles/${profileId}/change_apollonyar/`, apollonyarData);
    },
    changeStudentType(profileId, typeData) {
        return apiClient.patch(`/profiles/${profileId}/change_type/`, typeData);
    },
    changeStudentStatus(profileId, statusData) {
        return apiClient.patch(`/profiles/${profileId}/change_status/`, statusData);
    },
    updateAssignmentDueDate(assignmentId, dueDateData) {
        return apiClient.patch(`/assignments/${assignmentId}/`, dueDateData);
    },

    // --- Additional API functions ---
    getCalls() {
        return apiClient.get('/calls/');
    },
    getProfilePayments(profileId) {
        return apiClient.get(`/profiles/${profileId}/payments/`);
    },
    
    // --- Student Self Profile API methods ---
    getStudentProfile(studentId) {
        return apiClient.get(`/profiles/${studentId}/`);
    },
    getStudentAssignments(studentId) {
        return apiClient.get(`/profiles/${studentId}/assignments/`);
    },
    getStudentPayments(studentId) {
        return apiClient.get(`/profiles/${studentId}/payments/`);
    },
    getStudentActionLogs(studentId) {
        return apiClient.get(`/profiles/${studentId}/action_logs/`);
    },
    getStudentMedals(studentId) {
        return apiClient.get(`/profiles/${studentId}/medals/`);
    },
    getStudentProgress(studentId) {
        return apiClient.get(`/profiles/${studentId}/progress/`);
    },
    submitStudentAssignment(assignmentId, submissionData) {
        return apiClient.post(`/assignments/${assignmentId}/submit/`, submissionData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },
};