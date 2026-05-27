<template>
  <div class="detection-page">
    <!-- Ambient glow behind hero area -->
    <div class="hero-glow"></div>

    <!-- Function cards — visually subordinated -->
    <div class="function-tabs">
      <div
        v-for="tab in functionTabs"
        :key="tab.key"
        class="function-tab"
        :class="{ active: activeTab === tab.key }"
        :data-key="tab.key"
        @click="handleTabClick(tab.key)"
      >
        <input
          type="file"
          :accept="tab.accept"
          :multiple="tab.multiple"
          class="file-input"
          @change="handleFileChange($event, tab.key)"
          @click.stop
          ref="fileInputs"
        />
        <el-icon :size="17"><component :is="tab.icon" /></el-icon>
        <span class="tab-text">{{ tab.name }}</span>
      </div>
    </div>

    <!-- Camera detection -->
    <div v-if="activeTab === 'camera'" class="camera-section">
      <CameraDetection />
    </div>

    <!-- Batch detection strip -->
    <div v-if="batchFiles.length > 0 && activeTab !== 'camera'" class="batch-strip">
      <div v-if="batchProgress.total > 0" class="batch-progress">
        <span class="batch-progress-text">检测中 {{ batchResults.length }} / {{ batchProgress.total }}</span>
        <div class="batch-progress-bar"><div class="batch-progress-fill" :style="{ width: (batchResults.length / batchProgress.total * 100) + '%' }"></div></div>
      </div>
      <div class="batch-list">
        <div
          v-for="(item, index) in batchFiles"
          :key="index"
          class="batch-thumb"
          :class="{ active: batchActiveIndex === index, done: batchResults[index] }"
          @click="batchResults[index] && selectBatchResult(index)"
        >
          <img :src="item.url" class="batch-thumb-img" />
          <span class="batch-thumb-name">{{ item.name.length > 14 ? item.name.slice(0, 12) + '…' : item.name }}</span>
          <span v-if="batchResults[index]" class="batch-thumb-n">{{ batchResults[index].result.total_objects }}</span>
          <span v-else class="batch-thumb-wait">...</span>
        </div>
      </div>
    </div>

    <!-- Main content — detection area dominates -->
    <div v-if="activeTab !== 'camera'" class="main-content">
      <!-- Left: Hero detection area -->
      <div class="hero-panel">
        <div class="hero-header">
          <span class="hero-title">Detection View</span>
          <div class="hero-status" v-if="isDetecting">
            <span class="pulse-dot"></span>
            <span class="pulse-text">Analyzing...</span>
          </div>
          <span v-else-if="detectionResult" class="hero-badge">{{ detectionResult.total_objects }} objects</span>
        </div>

        <div class="hero-images" :class="compareMode">
          <!-- Source image -->
          <div class="hero-image-card" :class="{ active: originalImage }">
            <template v-if="originalImage">
              <img :src="originalImage" class="hero-img" />
            </template>
            <template v-else>
              <div class="hero-placeholder" @click="handlePlaceholderClick">
                <el-icon class="hero-placeholder-icon"><Plus /></el-icon>
                <span>Drop image here</span>
              </div>
            </template>
            <span class="hero-img-label">Source</span>
          </div>

          <!-- Result image — the focal point -->
          <div class="hero-image-card result" :class="{ active: resultImage }">
            <template v-if="resultImage">
              <img :src="resultImage" class="hero-img" />
              <!-- Scanning line overlay -->
              <div class="scan-line" :class="{ scanning: isDetecting }"></div>
              <!-- HUD corner markers -->
              <div class="hud-corners">
                <span class="hud-corner tl"></span>
                <span class="hud-corner tr"></span>
                <span class="hud-corner bl"></span>
                <span class="hud-corner br"></span>
              </div>
            </template>
            <template v-else>
              <div class="hero-placeholder result-placeholder">
                <el-icon class="hero-placeholder-icon"><Picture /></el-icon>
                <span>Waiting for input</span>
                <span class="hero-placeholder-hint">Select an image to begin analysis</span>
              </div>
            </template>
            <span class="hero-img-label">
              Result
              <span v-if="detectionResult" class="hero-img-badge">{{ detectionResult.total_objects }}</span>
            </span>
          </div>
        </div>

        <!-- View toggle -->
        <div class="hero-toolbar">
          <button :class="{ active: compareMode === 'side' }" class="hero-tool-btn" @click="compareMode = 'side'">
            <el-icon :size="13"><Menu /></el-icon>
          </button>
          <button :class="{ active: compareMode === 'grid' }" class="hero-tool-btn" @click="compareMode = 'grid'">
            <el-icon :size="13"><Grid /></el-icon>
          </button>
        </div>
      </div>

      <!-- Right: AI Co-pilot panel -->
      <div class="copilot-panel">
        <!-- System metrics -->
        <div class="metrics-row">
          <div class="metric-item">
            <span class="metric-label">GPU</span>
            <div class="metric-bar-wrap">
              <div class="metric-bar" :class="{ active: isDetecting }" style="width: 34%"></div>
            </div>
            <span class="metric-value">34<span class="metric-unit">%</span></span>
          </div>
          <div class="metric-item">
            <span class="metric-label">FPS</span>
            <div class="metric-bar-wrap">
              <div class="metric-bar" style="width: 72%"></div>
            </div>
            <span class="metric-value">36<span class="metric-unit">fps</span></span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Latency</span>
            <div class="metric-bar-wrap">
              <div class="metric-bar low" style="width: 28%"></div>
            </div>
            <span class="metric-value">28<span class="metric-unit">ms</span></span>
          </div>
        </div>

        <!-- Model info -->
        <div class="copilot-card model-card">
          <div class="copilot-card-hd">
            <el-icon :size="13"><component :is="Cpu" /></el-icon>
            <span>Model</span>
          </div>
          <div class="model-info-grid">
            <div class="model-kv">
              <span class="model-k">Architecture</span>
              <span class="model-v">{{ modelStore.currentModel }}</span>
            </div>
            <div class="model-kv">
              <span class="model-k">Input</span>
              <span class="model-v">640 × 640</span>
            </div>
            <div class="model-kv">
              <span class="model-k">Version</span>
              <span class="model-v">v1.0.0</span>
            </div>
          </div>
        </div>

        <!-- Detection results -->
        <div class="copilot-card results-card">
          <div class="copilot-card-hd">
            <el-icon :size="13"><List /></el-icon>
            <span>Detections</span>
            <span v-if="detectionResult" class="results-n">{{ detectionResult.total_objects }}</span>
          </div>
          <div v-if="!detectionResult || detectionResult.total_objects === 0" class="copilot-empty">
            <span>No detections yet</span>
          </div>
          <div v-else class="detection-list">
            <div v-for="(box, index) in detectionResult.boxes" :key="index" class="detection-row">
              <span class="det-idx">{{ String(index + 1).padStart(2, '0') }}</span>
              <span class="det-name">{{ box.class_name }}</span>
              <div class="det-bar-bg">
                <div class="det-bar-fill" :style="{ width: (box.confidence * 100) + '%' }"></div>
              </div>
              <span class="det-pct">{{ (box.confidence * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>

        <!-- AI diagnosis -->
        <div class="copilot-card diag-card">
          <div class="copilot-card-hd">
            <el-icon :size="13"><ChatDotRound /></el-icon>
            <span>Diagnosis</span>
          </div>
          <div class="diag-body">
            <p v-if="!detectionResult">Awaiting detection results for analysis.</p>
            <p v-else>
              {{ detectionResult.total_objects }} objects detected in {{ detectionResult.detection_time }}s
              using {{ detectionResult.model_name }}.
            </p>
          </div>
        </div>

        <!-- Actions -->
        <div class="copilot-actions">
          <button class="act-btn secondary" @click="handleRedetect">
            <el-icon :size="14"><Refresh /></el-icon>
            Re-run
          </button>
          <button class="act-btn primary">
            <el-icon :size="14"><component :is="Document" /></el-icon>
            Full Report
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, ElLoading } from "element-plus";
import {
  Picture, Plus, Folder, Monitor, Grid, List, VideoCamera,
  CircleCheck, ChatDotRound, Refresh, Menu, Cpu, Document,
} from "@element-plus/icons-vue";
import { detectSingleImage, detectBatchImages, getDetectionDetail } from "../api/detection";
import { useModelStore } from "../stores/model";
import CameraDetection from "../components/CameraDetection.vue";

const modelStore = useModelStore();
const route = useRoute();

const activeTab = ref("single");
const batchFiles = ref([]);
const batchResults = ref([]);
const batchProgress = ref({ current: 0, total: 0 });
const batchActiveIndex = ref(-1);
const compareMode = ref("side");
const originalImage = ref("");
const resultImage = ref("");
const detectionResult = ref(null);
const isDetecting = ref(false);

const functionTabs = [
  { key: "single", name: "Single", icon: Picture, accept: "image/*", multiple: false },
  { key: "batch", name: "Batch", icon: Plus, accept: "image/*", multiple: true },
  { key: "folder", name: "Folder", icon: Folder, accept: "image/*", multiple: true },
  { key: "camera", name: "Camera", icon: VideoCamera, accept: "", multiple: false, noInput: true },
  { key: "video", name: "Video", icon: Monitor, accept: "video/*", multiple: false },
];

const fileInputs = ref([]);

const handleTabClick = (key) => {
  activeTab.value = key;
  const tab = functionTabs.find(t => t.key === key);
  if (tab?.noInput) return;
  const input = document.querySelector(`.function-tab[data-key="${key}"] .file-input`);
  if (input) input.click();
};

const handleFileChange = async (event, tabKey) => {
  event.stopPropagation();
  event.preventDefault();
  const files = event.target.files;
  if (!files || files.length === 0) return;

  if (tabKey === "single") {
    await performSingleDetection(files[0]);
  } else if (tabKey === "batch" || tabKey === "folder") {
    batchFiles.value = Array.from(files).map(f => ({
      name: f.name,
      url: URL.createObjectURL(f),
      file: f,
    }));
    batchResults.value = [];
    batchActiveIndex.value = -1;
    detectionResult.value = null;
    originalImage.value = "";
    resultImage.value = "";
    await performBatchDetection();
  }
  setTimeout(() => { event.target.value = ''; }, 0);
};

const performSingleDetection = async (file) => {
  const loading = ElLoading.service({
    lock: true,
    text: "Analyzing...",
    background: "oklch(0.12 0.003 185 / 0.75)",
  });

  try {
    isDetecting.value = true;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("model_name", modelStore.currentModel);

    originalImage.value = URL.createObjectURL(file);

    const response = await detectSingleImage(formData);
    if (response.code === 200 && response.data) {
      detectionResult.value = response.data;
      resultImage.value = response.data.result_image_url;
      ElMessage.success("Detection complete");
    } else {
      ElMessage.error(response.message || "Detection failed");
    }
  } catch (error) {
    console.error("Detection error:", error);
    ElMessage.error("Detection failed, please retry");
  } finally {
    isDetecting.value = false;
    loading.close();
  }
};

const performBatchDetection = async () => {
  if (batchFiles.value.length === 0) return;
  isDetecting.value = true;
  batchProgress.value = { current: 0, total: batchFiles.value.length };
  const formData = new FormData();
  for (const f of batchFiles.value) {
    formData.append("files", f.file);
  }
  formData.append("model_name", modelStore.currentModel);

  try {
    const response = await detectBatchImages(formData);
    if (response.code === 200 && response.data) {
      batchResults.value = response.data;
      ElMessage.success(`批量检测完成 ${response.success}/${response.total}`);
      if (batchResults.value.length > 0) {
        selectBatchResult(0);
      }
    }
  } catch {
    // 错误提示已在 request 拦截器中处理
  } finally {
    isDetecting.value = false;
    batchProgress.value = { current: 0, total: 0 };
  }
};

const selectBatchResult = (index) => {
  batchActiveIndex.value = index;
  const item = batchResults.value[index];
  if (item && item.result) {
    detectionResult.value = item.result;
    originalImage.value = item.result.image_url;
    resultImage.value = item.result.result_image_url;
  }
};

const handlePlaceholderClick = () => {
  const input = document.querySelector('.function-tab[data-key="single"] .file-input');
  if (input) input.click();
};

const handleRedetect = () => {
  const input = document.querySelector('.function-tab[data-key="single"] .file-input');
  if (input) input.click();
};

onMounted(() => { loadRecord(); });
watch(() => route.query.record, () => { loadRecord(); });

async function loadRecord() {
  const recordId = route.query.record;
  if (!recordId) return;
  try {
    const res = await getDetectionDetail(recordId);
    if (res.code === 200 && res.data) {
      detectionResult.value = res.data;
      originalImage.value = res.data.image_url;
      resultImage.value = res.data.result_image_url;
    }
  } catch {
    // 错误提示已在 request 拦截器中处理
  }
}
</script>

<style scoped>
/* ============================================
   Detection Page — AI Workstation
   Hero: image comparison area
   Support: function tabs + copilot panel
   ============================================ */

.detection-page {
  width: 100%;
  max-width: 1320px;
  position: relative;
}

/* ---- Ambient glow behind hero ---- */
.hero-glow {
  position: absolute;
  top: 40%;
  left: 35%;
  width: 600px;
  height: 440px;
  transform: translate(-50%, -50%);
  background: radial-gradient(ellipse, oklch(0.52 0.10 178 / 0.055) 0%, transparent 65%);
  pointer-events: none;
  animation: hero-glow-pulse 6s ease-in-out infinite;
}

@keyframes hero-glow-pulse {
  0%, 100% { opacity: 0.6; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1.08); }
}

/* ---- Function tabs — compact, low-contrast ---- */
.function-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.function-tab {
  position: relative;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 16px;
  background: var(--bg-glass);
  border-radius: var(--radius-sm);
  cursor: pointer;
  border: 1px solid var(--border-subtle);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.function-tab:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
  border-color: var(--border-card);
}

.function-tab.active {
  color: var(--accent);
  background: var(--accent-soft);
  border-color: oklch(0.56 0.10 178 / 0.20);
}

.file-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  z-index: 5;
}

.tab-text { white-space: nowrap; }

/* ---- Batch strip ---- */
.batch-strip {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  padding: 14px 16px;
  margin-bottom: 16px;
}

.batch-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.batch-progress-text {
  font-size: 11px;
  color: var(--accent);
  font-weight: 540;
  white-space: nowrap;
}

.batch-progress-bar {
  flex: 1;
  height: 3px;
  background: oklch(0.90 0.002 180);
  border-radius: 3px;
  overflow: hidden;
}

.batch-progress-fill {
  height: 100%;
  background: var(--accent-gradient);
  border-radius: 3px;
  transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.batch-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.batch-list::-webkit-scrollbar { height: 4px; }
.batch-list::-webkit-scrollbar-thumb { background: oklch(0.85 0.002 180); border-radius: 4px; }

.batch-thumb {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  cursor: pointer;
  padding: 6px;
  border-radius: var(--radius-sm);
  border: 2px solid transparent;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  opacity: 0.5;
}

.batch-thumb.done { opacity: 1; }
.batch-thumb.active { border-color: var(--accent); background: var(--accent-soft); }
.batch-thumb.done:hover { background: var(--bg-hover); border-color: var(--border-card); }

.batch-thumb-img {
  width: 72px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
}

.batch-thumb-name {
  font-size: 10px;
  color: var(--text-secondary);
  max-width: 76px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.batch-thumb-n {
  font-size: 10px;
  font-weight: 620;
  color: var(--accent);
  background: var(--accent-soft);
  padding: 1px 6px;
  border-radius: var(--radius-full);
}

.batch-thumb-wait {
  font-size: 10px;
  color: var(--text-muted);
  animation: pulse-breath 1.4s ease-in-out infinite;
}

/* ---- Main content ---- */
.main-content {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

/* ============================================
   HERO PANEL — the visual focal point
   ============================================ */

.hero-panel {
  flex: 1;
  min-width: 0;
  position: relative;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 20px;
  border: 1px solid var(--border-card);
  box-shadow: var(--shadow-md), var(--shadow-hero);
}

.hero-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.hero-title {
  font-size: 12px;
  font-weight: 620;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* AI analyzing pulse */
.hero-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse-breath 1.4s ease-in-out infinite;
}

@keyframes pulse-breath {
  0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 4px var(--accent); }
  50% { opacity: 0.3; transform: scale(1.6); box-shadow: 0 0 12px var(--accent); }
}

.pulse-text {
  font-size: 11px;
  font-weight: 500;
  color: var(--accent);
  letter-spacing: 0.03em;
}

.hero-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  background: oklch(0.48 0.10 158 / 0.12);
  color: var(--success);
  letter-spacing: 0.02em;
}

/* ---- Hero images ---- */
.hero-images {
  display: flex;
  gap: 12px;
  height: 420px;
}

.hero-images.grid {
  flex-direction: column;
}

.hero-image-card {
  flex: 1;
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: oklch(0.95 0.002 180);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-subtle);
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.hero-image-card:hover {
  border-color: oklch(0.56 0.08 178 / 0.25);
}

.hero-image-card.result {
  background: oklch(0.93 0.003 185);
  border-color: oklch(0.56 0.08 178 / 0.15);
  box-shadow: inset 0 0 60px oklch(0.50 0.08 180 / 0.04);
}

.hero-image-card.result.active {
  border-color: oklch(0.52 0.10 178 / 0.22);
}

.hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ---- Scanning line ---- */
.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, oklch(0.55 0.12 178 / 0.7), transparent);
  top: -2px;
  opacity: 0;
  pointer-events: none;
  box-shadow: 0 0 12px oklch(0.52 0.12 178 / 0.5);
}

.scan-line.scanning {
  animation: scan-down 2.2s ease-in-out infinite;
  opacity: 1;
}

@keyframes scan-down {
  0% { top: -2px; opacity: 0; }
  15% { opacity: 1; }
  85% { opacity: 1; }
  100% { top: calc(100% + 2px); opacity: 0; }
}

/* ---- HUD corner markers ---- */
.hud-corners {
  position: absolute;
  inset: 10px;
  pointer-events: none;
  opacity: 0.35;
}

.hud-corner {
  position: absolute;
  width: 16px;
  height: 16px;
  border-color: oklch(0.55 0.12 178 / 0.6);
}

.hud-corner.tl { top: 0; left: 0; border-top: 1px solid; border-left: 1px solid; }
.hud-corner.tr { top: 0; right: 0; border-top: 1px solid; border-right: 1px solid; }
.hud-corner.bl { bottom: 0; left: 0; border-bottom: 1px solid; border-left: 1px solid; }
.hud-corner.br { bottom: 0; right: 0; border-bottom: 1px solid; border-right: 1px solid; }

/* ---- Placeholder ---- */
.hero-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 24px;
}

.hero-placeholder-icon {
  font-size: 32px;
  color: oklch(0.56 0.03 178 / 0.3);
}

.hero-placeholder span {
  font-size: 12px;
  color: var(--text-muted);
}

.hero-placeholder-hint {
  font-size: 10px !important;
  opacity: 0.55;
}

.hero-placeholder.result-placeholder {
  cursor: default;
}

/* ---- Hero image label ---- */
.hero-img-label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 7px 14px;
  background: oklch(0.155 0.003 185 / 0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  color: oklch(0.92 0.002 178);
  font-size: 10px;
  font-weight: 520;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hero-img-badge {
  font-size: 10px;
  padding: 1px 7px;
  border-radius: var(--radius-full);
  background: oklch(0.55 0.12 178 / 0.4);
  color: #fff;
}

/* ---- Hero toolbar ---- */
.hero-toolbar {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 3px;
}

.hero-tool-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-xs);
  color: var(--text-muted);
  background: oklch(0.16 0.003 185 / 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid oklch(1 0 0 / 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}

.hero-tool-btn:hover {
  color: #fff;
  background: oklch(0.16 0.003 185 / 0.75);
}

.hero-tool-btn.active {
  color: #fff;
  background: var(--accent);
  border-color: var(--accent);
}

/* ============================================
   COPILOT PANEL — AI co-pilot, not a table
   ============================================ */

.copilot-panel {
  width: 296px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ---- Metrics row ---- */
.metrics-row {
  display: flex;
  gap: 8px;
}

.metric-item {
  flex: 1;
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-xs);
}

.metric-label {
  display: block;
  font-size: 9px;
  font-weight: 520;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 7px;
}

.metric-bar-wrap {
  height: 3px;
  background: oklch(0.90 0.002 180);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 5px;
}

.metric-bar {
  height: 100%;
  border-radius: 3px;
  background: var(--accent-gradient);
  transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.metric-bar.low { background: var(--success); }

.metric-value {
  font-size: 16px;
  font-weight: 640;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
}

.metric-unit {
  font-size: 10px;
  font-weight: 480;
  color: var(--text-muted);
  margin-left: 1px;
}

/* ---- Copilot cards ---- */
.copilot-card {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: 13px 16px;
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-xs);
}

.copilot-card-hd {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.copilot-card-hd .el-icon {
  color: var(--accent);
}

/* ---- Model info ---- */
.model-info-grid {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.model-kv {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-k {
  font-size: 11px;
  color: var(--text-muted);
}

.model-v {
  font-size: 11px;
  font-weight: 540;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

/* ---- Detection list ---- */
.results-n {
  margin-left: auto;
  font-size: 10px;
  font-weight: 620;
  color: var(--accent);
  background: var(--accent-soft);
  padding: 1px 7px;
  border-radius: var(--radius-full);
}

.copilot-empty {
  padding: 16px 0;
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  opacity: 0.6;
}

.detection-list {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.detection-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: oklch(0.955 0.002 180);
  border-radius: var(--radius-xs);
  transition: all 0.25s cube-bezier(0.16, 1, 0.3, 1);
}

.detection-row:hover {
  background: var(--accent-soft);
  transform: translateX(2px);
}

.det-idx {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
  width: 18px;
}

.det-name {
  font-size: 11px;
  font-weight: 520;
  color: var(--text-primary);
  flex: 1;
}

.det-bar-bg {
  width: 48px;
  height: 3px;
  background: oklch(0.90 0.002 180);
  border-radius: 3px;
  overflow: hidden;
}

.det-bar-fill {
  height: 100%;
  border-radius: 3px;
  background: var(--accent-gradient);
  transition: width 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}

.det-pct {
  font-size: 10px;
  font-weight: 540;
  color: var(--success);
  font-variant-numeric: tabular-nums;
  width: 36px;
  text-align: right;
}

/* ---- Diagnosis ---- */
.diag-body {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.diag-body p:first-child { color: var(--text-muted); }

/* ---- Actions ---- */
.copilot-actions {
  display: flex;
  gap: 8px;
}

.act-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 9px 14px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 520;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.act-btn.secondary {
  flex: 1;
  color: var(--text-secondary);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-xs);
}

.act-btn.secondary:hover {
  color: var(--text-primary);
  border-color: var(--border-card);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.act-btn.primary {
  flex: 2;
  color: #fff;
  background: var(--accent-gradient);
  border: none;
  box-shadow: var(--shadow-btn);
}

.act-btn.primary:hover {
  box-shadow: 0 4px 20px oklch(0.38 0.10 178 / 0.28);
  transform: translateY(-2px);
}

/* ---- Camera section ---- */
.camera-section {
  padding: 8px 0;
}
</style>
