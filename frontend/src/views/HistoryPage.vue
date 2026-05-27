<template>
  <div class="history-page">
    <div class="page-header">
      <h1 class="page-title">历史记录</h1>
      <p class="page-subtitle">查看和管理所有检测记录</p>
    </div>

    <div class="search-bar">
      <el-input v-model="searchQuery" placeholder="搜索检测记录..." size="default" class="search-input">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filterStatus" placeholder="状态筛选" size="default" class="filter-select">
        <el-option label="全部" value="" />
        <el-option label="检测完成" value="completed" />
        <el-option label="检测中" value="processing" />
        <el-option label="失败" value="failed" />
      </el-select>
      <el-select v-model="filterType" placeholder="类型筛选" size="default" class="filter-select">
        <el-option label="全部" value="" />
        <el-option label="单图检测" value="single" />
        <el-option label="批量检测" value="batch" />
        <el-option label="文件夹" value="folder" />
        <el-option label="视频检测" value="video" />
      </el-select>
    </div>

    <div class="history-list">
      <div v-for="record in historyRecords" :key="record.id" class="history-card" @click="viewRecord(record)">
        <div class="record-preview">
          <img :src="record.image_url" :alt="record.model_name" class="preview-image" />
          <div class="status-badge completed">
            <span class="status-dot"></span>
            完成
          </div>
        </div>
        <div class="record-info">
          <div class="record-header">
            <span class="record-filename">{{ record.id.slice(0, 8) }}...{{ record.model_name }}</span>
            <span class="record-type">{{ getTypeText(record.type) }}</span>
          </div>
          <div class="record-meta">
            <span class="meta-item"><el-icon :size="13"><Clock /></el-icon>{{ formatTime(record.created_at) }}</span>
            <span class="meta-item"><el-icon :size="13"><Picture /></el-icon>{{ record.model_name }}</span>
            <span class="meta-item"><el-icon :size="13"><Aim /></el-icon>{{ record.total_objects }} 目标</span>
          </div>
        </div>
        <div class="record-actions" @click.stop>
          <el-button size="small" text @click="viewRecord(record)"><el-icon :size="14"><Monitor/></el-icon>查看</el-button>
          <el-button size="small" text @click="downloadRecord(record)"><el-icon :size="14"><Download/></el-icon>下载</el-button>
          <el-button size="small" text type="danger" @click="deleteRecord(record)"><el-icon :size="14"><Delete/></el-icon>删除</el-button>
        </div>
      </div>
    </div>

    <div v-if="!loading && historyRecords.length === 0" class="empty-state">
      <el-icon :size="56" class="empty-icon"><Search /></el-icon>
      <p class="empty-text">暂无检测记录</p>
      <el-button type="primary" @click="goToDetection">开始检测</el-button>
    </div>

    <div class="pagination-wrapper">
      <el-pagination
        v-if="totalRecords > 0"
        :total="totalRecords"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
        layout="prev, pager, next"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import {
  Search, Clock, Picture, Aim, Monitor, Download, Delete,
} from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { getDetectionHistory } from "../api/detection";

const router = useRouter();
const searchQuery = ref("");
const filterStatus = ref("");
const filterType = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const totalRecords = ref(0);
const loading = ref(false);

const historyRecords = ref([]);

async function fetchHistory() {
  loading.value = true;
  try {
    const params = { page: currentPage.value, page_size: pageSize.value };
    if (filterStatus.value) params.status = filterStatus.value;
    if (filterType.value) params.type = filterType.value;
    if (searchQuery.value) params.search = searchQuery.value;
    const res = await getDetectionHistory(params);
    historyRecords.value = res.data;
    totalRecords.value = res.total;
  } catch {
    // 错误提示已在 request 拦截器中处理
  } finally {
    loading.value = false;
  }
}

onMounted(() => { fetchHistory(); });
watch([currentPage, filterStatus, filterType], () => { fetchHistory(); });

let searchTimer;
watch(searchQuery, () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => { currentPage.value = 1; fetchHistory(); }, 400);
});

function getStatusText(status) {
  const texts = { completed: "完成", processing: "检测中", failed: "失败", pending: "等待中" };
  return texts[status] || status;
}
function getTypeText(type) {
  const texts = { single: "单图", batch: "批量", folder: "文件夹", video: "视频" };
  return texts[type] || "单图";
}
function formatTime(dateStr) {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleString("zh-CN");
}

const viewRecord = (record) => {
  router.push(`/detection?record=${record.id}`);
};
const downloadRecord = (record) => {
  if (record.result_image_url) {
    window.open(record.result_image_url, "_blank");
  }
};
const deleteRecord = (record) => {
  ElMessage.info("删除功能开发中");
};
const goToDetection = () => router.push("/detection");
const handlePageChange = (page) => {
  currentPage.value = page;
  fetchHistory();
};
</script>

<style scoped lang="scss">
.history-page { width: 100%; max-width: 1100px; position: relative; }

.history-page::before {
  content: "";
  position: absolute;
  top: -80px;
  left: -60px;
  width: 360px;
  height: 360px;
  background: radial-gradient(ellipse, oklch(0.52 0.08 178 / 0.04) 0%, transparent 70%);
  pointer-events: none;
  z-index: -1;
  animation: ambient-drift 24s ease-in-out infinite;
}

@keyframes ambient-drift {
  0%, 100% { transform: translate(0, 0); }
  33% { transform: translate(30px, -15px); }
  66% { transform: translate(-15px, 10px); }
}

.page-header { margin-bottom: 28px; }
.page-title { font-size: 26px; font-weight: 620; color: var(--text-primary); margin-bottom: 6px; letter-spacing: -0.02em; }
.page-subtitle { font-size: 13px; color: var(--text-muted); }
.search-bar { display: flex; gap: 12px; margin-bottom: 24px; align-items: center; }
.search-input { flex: 1; max-width: 280px; }
.filter-select { width: 130px; }
.history-list { display: flex; flex-direction: column; gap: 10px; }
.history-card {
  background: var(--bg-surface); border-radius: var(--radius-md); padding: 18px 22px;
  border: 1px solid var(--border-subtle); box-shadow: var(--shadow-xs);
  display: flex; align-items: center; gap: 18px; cursor: pointer;
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.35s cubic-bezier(0.16, 1, 0.3, 1),
              border-color 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}
.history-card:hover {
  background: var(--bg-raised); box-shadow: var(--shadow-md); transform: translateY(-2px);
  border-color: var(--border-card);
}
.record-preview { position: relative; width: 112px; height: 76px; border-radius: var(--radius-xs); overflow: hidden; flex-shrink: 0; background: oklch(0.96 0.002 168); border: 1px solid var(--border-subtle); }
.preview-image { width: 100%; height: 100%; object-fit: cover; }
.status-badge {
  position: absolute; bottom: 5px; left: 5px; padding: 2px 9px; border-radius: var(--radius-full);
  font-size: 10px; font-weight: 500; display: flex; align-items: center; gap: 4px;
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
}
.status-badge.completed { background: oklch(0.90 0.06 155 / 0.85); color: oklch(0.35 0.10 155); }
.status-badge.processing { background: oklch(0.90 0.05 175 / 0.85); color: oklch(0.35 0.07 175); }
.status-badge.failed { background: oklch(0.92 0.06 20 / 0.85); color: oklch(0.40 0.14 22); }
.status-dot { width: 4px; height: 4px; border-radius: 50%; background: currentColor; }
.record-info { flex: 1; min-width: 0; }
.record-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.record-filename { font-size: 13px; font-weight: 600; color: var(--text-primary); letter-spacing: -0.01em; }
.record-type { padding: 2px 8px; background: var(--accent-muted); border-radius: var(--radius-xs); font-size: 10px; color: var(--accent); font-weight: 540; }
.record-meta { display: flex; gap: 16px; margin-bottom: 6px; }
.meta-item { display: flex; align-items: center; gap: 4px; font-size: 11px; color: var(--text-muted); }
.record-tags { display: flex; flex-wrap: wrap; gap: 5px; }
.detected-tag { padding: 1px 7px; background: var(--accent-muted); color: var(--accent); border-radius: var(--radius-xs); font-size: 10px; font-weight: 520; }
.record-actions { display: flex; gap: 2px; flex-shrink: 0; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 0; }
.empty-icon { color: var(--text-muted); opacity: 0.4; margin-bottom: 16px; }
.empty-text { font-size: 14px; color: var(--text-secondary); margin-bottom: 24px; }
.pagination-wrapper { display: flex; justify-content: center; margin-top: var(--space-xl); }
</style>
