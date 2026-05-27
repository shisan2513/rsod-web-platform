<template>
  <div class="shell">
    <header class="topbar">
      <div class="topbar-left">
        <div class="logo-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <circle cx="12" cy="12" r="3"/>
            <line x1="12" y1="2" x2="12" y2="6"/>
            <line x1="12" y1="18" x2="12" y2="22"/>
            <line x1="2" y1="12" x2="6" y2="12"/>
            <line x1="18" y1="12" x2="22" y2="12"/>
          </svg>
        </div>
        <span class="logo-text">遥感目标检测平台</span>
      </div>
      <div class="topbar-right">
        <span class="status-badge" :class="{ ok: connectOk }">
          <span class="status-dot"></span>
          {{ connectOk ? '服务已连接' : '未连接' }}
        </span>
      </div>
    </header>

    <main class="main">
      <div class="hero">
        <h1 class="hero-title">AI 遥感图像分析</h1>
        <p class="hero-desc">上传遥感图像，YOLO11 模型自动识别飞机、船舶、建筑等目标，实时返回检测结果与置信度。</p>
      </div>

      <div class="card upload-card">
        <div class="card-body">
          <div
            class="dropzone"
            :class="{ dragover: isDragover, filled: selectedFile }"
            @dragover.prevent="isDragover = true"
            @dragleave="isDragover = false"
            @drop.prevent="onDrop"
            @click="triggerInput"
          >
            <template v-if="!selectedFile">
              <div class="dz-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
              </div>
              <div class="dz-text">
                <span class="dz-link">点击上传</span> 或拖放图片到此处
              </div>
              <div class="dz-hint">JPG / PNG，单张不超过 5MB</div>
            </template>
            <template v-else>
              <div class="preview-wrap">
                <img :src="previewUrl" class="preview-img" />
                <button class="preview-remove" @click.stop="clearFile">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </template>
          </div>
          <input ref="fileInput" type="file" accept="image/jpeg,image/png" hidden @change="onFileInput" />
        </div>

        <div class="card-foot">
          <button
            class="btn-detect"
            :disabled="!selectedFile || loading"
            @click="handleInference"
          >
            <svg v-if="loading" class="spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            {{ loading ? '正在检测…' : '开始检测' }}
          </button>
          <p class="card-foot-hint" v-if="!selectedFile">请先选择一张遥感图像</p>
          <p class="card-foot-hint" v-else-if="!loading">准备就绪，点击按钮开始 AI 识别</p>
        </div>
      </div>

      <div v-if="errorMsg" class="toast">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
        {{ errorMsg }}
      </div>

      <div v-if="resultImageUrl" class="card result-card">
        <div class="result-head">
          <div>
            <h2 class="result-title">检测结果</h2>
            <p class="result-sub">共识别 <strong>{{ detections.length }}</strong> 个目标</p>
          </div>
        </div>
        <div class="result-img-wrap">
          <img :src="resultImageUrl" class="result-img" />
        </div>
        <div class="result-tags" v-if="detections.length">
          <span
            v-for="item in detections"
            :key="item.class + item.confidence"
            class="tag-chip"
            :style="{ '--chip-color': colorMap[item.class] || 'var(--accent)' }"
          >
            <span class="chip-dot"></span>
            {{ labelMap[item.class] || item.class }}
            <span class="chip-pct">{{ (item.confidence * 100).toFixed(0) }}%</span>
          </span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { ElMessage } from "element-plus";

const connectOk = ref(false);
const selectedFile = ref(null);
const previewUrl = ref("");
const loading = ref(false);
const resultImageUrl = ref("");
const detections = ref([]);
const errorMsg = ref("");
const isDragover = ref(false);
const fileInput = ref(null);

const colorMap = {
  airplane: "#ef4444", oil_tank: "#f59e0b", playground: "#10b981",
  building: "#3b82f6", ship: "#8b5cf6", pest: "#ec4899",
  person: "#06b6d4", car: "#84cc16", bus: "#f97316", truck: "#6366f1",
};
const labelMap = {
  airplane: "飞机", oil_tank: "油罐", playground: "操场", building: "建筑",
  ship: "船舶", pest: "虫害", person: "行人", car: "汽车", bus: "公交", truck: "卡车",
};

onMounted(() => { testConnect(); });

const testConnect = async () => {
  try {
    const res = await fetch("/api/test/connect");
    const data = await res.json();
    connectOk.value = data.code === 200;
  } catch { connectOk.value = false; }
};

const triggerInput = () => { if (!selectedFile.value) fileInput.value?.click(); };

const onFileInput = (e) => { const f = e.target.files?.[0]; if (f) loadFile(f); };
const onDrop = (e) => { isDragover.value = false; const f = e.dataTransfer?.files?.[0]; if (f) loadFile(f); };

const loadFile = (file) => {
  errorMsg.value = "";
  if (!["image/jpeg", "image/png"].includes(file.type)) { errorMsg.value = "仅支持 JPG / PNG 格式"; return; }
  if (file.size > 5 * 1024 * 1024) { errorMsg.value = "图片大小不能超过 5MB"; return; }
  selectedFile.value = file;
  previewUrl.value = URL.createObjectURL(file);
  resultImageUrl.value = "";
  detections.value = [];
};

const clearFile = () => { selectedFile.value = null; previewUrl.value = ""; };

const handleInference = async () => {
  if (!selectedFile.value) return;
  loading.value = true;
  errorMsg.value = "";
  const fd = new FormData();
  fd.append("file", selectedFile.value);
  try {
    const res = await axios.post("/api/inference/single", fd, { headers: { "Content-Type": "multipart/form-data" } });
    if (res.data.code === 200) {
      resultImageUrl.value = res.data.data.image_url;
      detections.value = res.data.data.detections;
    } else { errorMsg.value = res.data.message || "推理失败"; }
  } catch (err) { errorMsg.value = `请求失败: ${err.message}`; }
  finally { loading.value = false; }
};
</script>

<style scoped>
.shell { min-height: 100vh; display: flex; flex-direction: column; }

/* ---- topbar ---- */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  height: 56px; padding: 0 28px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  position: sticky; top: 0; z-index: 20;
}
.topbar-left { display: flex; align-items: center; gap: 10px; }
.logo-icon {
  width: 34px; height: 34px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-sm);
  background: var(--accent-soft);
  color: var(--accent);
}
.logo-text { font-size: 15px; font-weight: 600; color: var(--text-primary); letter-spacing: 0.01em; }
.topbar-right { display: flex; align-items: center; }

.status-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border-radius: 20px;
  font-size: 12px; color: var(--text-muted);
  background: var(--bg-wash); border: 1px solid var(--border-subtle);
}
.status-badge.ok { color: var(--success); background: oklch(0.95 0.04 155); border-color: oklch(0.85 0.08 155); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--text-muted); }
.status-badge.ok .status-dot { background: var(--success); }

/* ---- main ---- */
.main {
  flex: 1; max-width: 840px; width: 100%; margin: 0 auto;
  padding: 48px 24px 80px; display: flex; flex-direction: column; gap: 20px;
}

/* ---- hero ---- */
.hero { text-align: center; margin-bottom: 8px; }
.hero-title { font-size: 28px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.01em; }
.hero-desc { margin-top: 8px; font-size: 14px; color: var(--text-secondary); max-width: 520px; margin-left: auto; margin-right: auto; line-height: 1.7; }

/* ---- card ---- */
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}
.upload-card { overflow: hidden; }

/* ---- dropzone ---- */
.dropzone {
  padding: 48px 24px; text-align: center;
  cursor: pointer; transition: background 0.15s, border-color 0.15s;
  border: 2px dashed var(--border-strong); border-radius: var(--radius-md); margin: 20px;
}
.dropzone:hover, .dropzone.dragover {
  background: var(--accent-soft); border-color: var(--accent);
}
.dropzone.filled { padding: 16px; border-style: solid; border-color: var(--border-subtle); cursor: default; }

.dz-icon { color: var(--text-muted); margin-bottom: 14px; }
.dz-text { font-size: 15px; color: var(--text-secondary); }
.dz-link { color: var(--accent); font-weight: 600; }
.dz-hint { margin-top: 6px; font-size: 12px; color: var(--text-muted); }

.preview-wrap { position: relative; display: inline-block; max-height: 360px; }
.preview-img { max-width: 100%; max-height: 360px; border-radius: var(--radius-sm); display: block; }
.preview-remove {
  position: absolute; top: 8px; right: 8px;
  width: 30px; height: 30px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  border: none; background: oklch(0.2 0.01 260 / 0.7); color: #fff; cursor: pointer;
  transition: background 0.15s;
}
.preview-remove:hover { background: oklch(0.2 0.01 260 / 0.9); }

/* ---- card foot ---- */
.card-foot {
  padding: 16px 24px 20px;
  border-top: 1px solid var(--border-subtle);
  display: flex; flex-direction: column; align-items: center; gap: 10px;
}
.card-foot-hint { font-size: 12px; color: var(--text-muted); }

.btn-detect {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 12px 36px; border: none; border-radius: var(--radius-md);
  background: var(--accent); color: #fff;
  font-size: 15px; font-weight: 600; cursor: pointer;
  transition: background 0.15s, transform 0.1s, box-shadow 0.15s;
  box-shadow: 0 2px 8px oklch(0.52 0.16 262 / 0.3);
}
.btn-detect:hover:not(:disabled) {
  background: var(--accent-hover);
  box-shadow: 0 4px 14px oklch(0.52 0.16 262 / 0.4);
  transform: translateY(-1px);
}
.btn-detect:active:not(:disabled) { transform: translateY(0); }
.btn-detect:disabled { opacity: 0.45; cursor: not-allowed; box-shadow: none; }

/* ---- toast ---- */
.toast {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 18px; border-radius: var(--radius-md);
  background: oklch(0.95 0.04 22); color: oklch(0.45 0.15 22);
  font-size: 13px;
}

/* ---- result card ---- */
.result-card { overflow: hidden; }
.result-head { padding: 20px 24px 0; }
.result-title { font-size: 16px; font-weight: 600; }
.result-sub { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }
.result-sub strong { color: var(--text-primary); }
.result-img-wrap { padding: 16px 24px; }
.result-img { width: 100%; border-radius: var(--radius-sm); display: block; border: 1px solid var(--border-subtle); }

.result-tags {
  display: flex; flex-wrap: wrap; gap: 8px;
  padding: 0 24px 20px;
}

.tag-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 12px; border-radius: 20px;
  font-size: 13px; color: var(--text-primary);
  background: var(--bg-wash); border: 1px solid var(--border-subtle);
}
.chip-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--chip-color); flex-shrink: 0; }
.chip-pct { color: var(--text-muted); font-size: 12px; }

@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; }
</style>
