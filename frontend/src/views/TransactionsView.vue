<script setup>
import { ref, onMounted } from 'vue';
import { useDataStore } from '@/stores/dataStore.js';
import BaseTable from '@/components/BaseTable.vue';
import BaseModal from '@/components/BaseModal.vue';
import { useLayoutStore } from '@/stores/layout.js';

const dataStore = useDataStore();
const layoutStore = useLayoutStore();
onMounted(() => {
  layoutStore.setPageTitle('تراکنش‌ها');
});

const isModalOpen = ref(false);
const selectedTransaction = ref(null);
const newNote = ref('');

function openTransactionModal(transaction) {
  selectedTransaction.value = JSON.parse(JSON.stringify(transaction));
  newNote.value = '';
  isModalOpen.value = true;
}

function handleTransactionStatus(status) {
  dataStore.updateTransactionStatus(selectedTransaction.value.id, status);
  isModalOpen.value = false;
}

function submitNewNote() {
    if (newNote.value.trim()) {
        dataStore.addTransactionNote(selectedTransaction.value.id, newNote.value.trim());
        const updatedTransaction = dataStore.transactions.find(t => t.id === selectedTransaction.value.id);
        selectedTransaction.value = JSON.parse(JSON.stringify(updatedTransaction));
        newNote.value = '';
    }
}

const tableColumns = [
  { key: 'actions', label: '', sortable: false, filterable: false },
  { key: 'type', label: '', sortable: true, filterable: true, width: '60px' },
  { key: 'amount', label: 'مبلغ (تومان)', sortable: true, filterable: false },
  { key: 'dateTime', label: 'تاریخ و ساعت', sortable: true, filterable: false },
  { key: 'trackingNumber', label: 'شماره پیگیری', sortable: false, filterable: true },
  { key: 'paymentMethod', label: 'نوع', sortable: true, filterable: true },
  { key: 'status', label: 'تأیید تراکنش', sortable: true, filterable: true },
];
</script>

<template>
  <div class="view-container">
    <BaseTable :columns="tableColumns" :data="dataStore.transactions" :rows-per-page="15">
      <template #cell-type="{ item }">
        <span class="type-cell-icon-only">
          <i
            :title="item.type"
            :class="{
              'fa-solid': true,
              'fa-circle-plus': item.type === 'واریز', 'icon-deposit': item.type === 'واریز',
              'fa-circle-minus': item.type === 'برداشت', 'icon-withdrawal': item.type === 'برداشت'
            }"
          ></i>
        </span>
      </template>
      
      <template #cell-status="{ item }">
        <span class="status-badge" :class="item.status.replace(' ', '_')">{{ item.status }}</span>
      </template>

      <template #cell-actions="{ item }">
        <button @click="openTransactionModal(item)" class="btn-sm btn-icon-only" title="مشاهده جزئیات">
          <i class="fa-solid fa-eye"></i>
        </button>
      </template>
    </BaseTable>
  </div>

  <BaseModal :show="isModalOpen" @close="isModalOpen = false" size="lg">
    <template #header>
      <h2>جزئیات تراکنش</h2>
    </template>
    
    <div class="modal-scroll-container">
      <div v-if="selectedTransaction" class="modal-grid">
        <div class="transaction-details">
          <div class="detail-item amount-header">
            <i :class="selectedTransaction.type === 'واریز' ? 'fa-solid fa-circle-plus icon-deposit' : 'fa-solid fa-circle-minus icon-withdrawal'"></i>
            <h3>{{ selectedTransaction.amount }} تومان</h3>
          </div>
          <div class="detail-item"><span>تاریخ و ساعت:</span><span>{{ selectedTransaction.dateTime }}</span></div>
          <div class="detail-item"><span>شماره پیگیری:</span><span>{{ selectedTransaction.trackingNumber }}</span></div>
          <div class="detail-item"><span>نوع تراکنش:</span><span>{{ selectedTransaction.paymentMethod }}</span></div>
          
          <div v-if="selectedTransaction.receiptImageUrl" class="receipt-section">
            <h5>رسید تراکنش:</h5>
            <a :href="selectedTransaction.receiptImageUrl" target="_blank" class="receipt-thumbnail">
              <img :src="selectedTransaction.receiptImageUrl" alt="عکس رسید">
            </a>
          </div>
        </div>

        <div class="notes-section">
          <h5>یادداشت‌ها و تاریخچه</h5>
          <div class="add-note-form">
            <textarea v-model="newNote" rows="3" placeholder="یادداشت جدید خود را اینجا بنویسید..."></textarea>
            <button @click="submitNewNote" class="btn-sm"><i class="fa-solid fa-plus"></i> ثبت یادداشت</button>
          </div>
          <ul class="notes-list">
            <li v-for="(note, index) in selectedTransaction.notes" :key="index">
              <p class="note-text">{{ note.text }}</p>
              <small class="note-meta">توسط: {{ note.author }} - {{ note.date }}</small>
            </li>
          </ul>
        </div>
      </div>
    </div>
      
    <div v-if="selectedTransaction" class="modal-actions">
      <button @click="handleTransactionStatus('تأیید')" class="btn btn-success">تأیید تراکنش</button>
      <button @click="handleTransactionStatus('در انتظار')" class="btn btn-warning">بررسی مجدد</button>
      <button @click="handleTransactionStatus('رد')" class="btn btn-danger">رد تراکنش</button>
    </div>
  </BaseModal>
</template>

<style scoped>
.view-container { padding-top: 20px; }
.type-cell-icon-only { font-size: 1.2rem; text-align: center; }
.icon-deposit { color: var(--success-text); }
.icon-withdrawal { color: var(--danger-color); }

.status-badge { padding: 4px 12px; border-radius: 8px; font-size: 11px; white-space: nowrap; }
.status-badge.تأیید { background-color: var(--success-bg); color: var(--success-text); }
.status-badge.رد { background-color: #fee2e2; color: #b91c1c; }
.status-badge.در_انتظار {
  background-color: #e0e7ff; 
  color: #3730a3;
  border-radius: 99px;
}

.modal-scroll-container {
  max-height: 65vh;
  overflow-y: auto;
  padding: 5px 15px 5px 5px;
  margin: 0 -15px 0 -5px;
}
.modal-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 25px;
}
.transaction-details .detail-item {
  display: flex; justify-content: space-between; padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}
.amount-header {
  justify-content: center; align-items: center; gap: 10px;
  font-size: 1.5rem; font-weight: 700; margin-bottom: 15px;
}
.receipt-section { margin-top: 20px; }
.receipt-thumbnail { display: block; width: 100%; border-radius: 8px; overflow: hidden; }
.receipt-thumbnail img { width: 100%; height: auto; object-fit: cover; display: block; }

.notes-section h5 { margin-bottom: 15px; }
.add-note-form { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
.add-note-form textarea { width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; background-color: var(--background-color); font-family: 'Vazirmatn', sans-serif;}
.notes-list {
  list-style: none; max-height: 300px; overflow-y: auto;
  padding-left: 10px; border-left: 2px solid var(--border-color);
}
.notes-list li {
  position: relative; padding: 10px 15px;
  background-color: var(--background-color);
  border-radius: 8px; margin-bottom: 10px;
  /* ۱. افزودن این خط برای جلوگیری از سرریز شدن آیتم لیست */
  overflow: hidden; 
}
.notes-list li::before {
  content: '✓'; position: absolute; left: -20px; top: 12px;
  background-color: var(--primary-color); color: white;
  width: 18px; height: 18px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-size: 12px;
}
/* ۲. اصلاح استایل‌ها برای شکستن صحیح کلمات و خطوط */
.note-text, .note-meta {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 0.9rem;
}
.note-text { margin-bottom: 8px; }
.note-meta { font-size: 0.75rem; color: var(--text-secondary); }

.modal-actions {
  display: flex; gap: 10px; margin-top: 25px;
  border-top: 1px solid var(--border-color); padding-top: 20px;
}
.btn-success { background-color: var(--success-text); }
.btn-danger { background-color: var(--danger-color); }
.btn-warning {
    background-color: var(--warning-text);
    color: #fff;
}
.btn-icon-only {
  width: 32px;
  height: 32px;
  padding: 0;
  font-size: 1rem;
}
</style>