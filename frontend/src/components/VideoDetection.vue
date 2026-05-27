<template>
  <div class="video-detection">
    <div class="video-layout">
      <!-- Left: Video area -->
      <div class="video-panel">
        <div class="video-viewport">
          <template v-if="!hasVideo">
            <div class="video-placeholder" @click="triggerFileInput">
              <el-icon :size="40"><VideoCamera /></el-icon>
              <span>点击上传视频文件</span>
              <span class="placeholder-hint">mp4, avi, mov</span>
              <input
                type="file"
                accept="video/*"
                class="video-file-input-hidden"
                @change="handleVideoUpload"
              />
            </div>
          </template>
          <template v-else>
            <video
              ref="videoRef"
              :src="videoUrl"
              class="video-player"
              :controls="!isDetecting"
              @loadedmetadata="onVideoLoaded"
              @timeupdate="onTimeUpdate"
              @ended="onVideoEnded"
            />
            <canvas ref="canvasRef" class="detection-canvas" :class="{ 'canvas-active': isDetecting }" />

            <div v-if="isDetecting" class="video-hud">
              <div class="hud-item">
                <span class="hud-label">帧数</span>
                <span class="hud-value">{{ currentFrameIndex }}</span>
              </div>
              <div class="hud-item">
                <span class="hud-label">目标</span>
                <span class="hud-value">{{ currentDetection?.total_objects || 0 }}</span>
              </div>
              <div class="hud-item">
                <span class="hud-label">耗时</span>
                <span class="hud-value">{{ (currentDetection?.detection_time * 1000).toFixed(0) || 0 }}ms</span>
              </div>
            </div>
          </template>
        </div>

        <div v-if="hasVideo" class="video-info-bar">
          <span>时长 {{ formatDuration(videoDuration) }}</span>
          <span>当前 {{ formatDuration(currentTime) }}</span>
        </div>
      </div>

      <!-- Right: Controls + Results -->
      <div class="side-panel">
        <div class="side-card">
          <div class="side-card-hd">检测设置</div>

          <div class="setting-item">
            <div class="setting-label">
              <span>置信度阈值</span>
              <span class="setting-val">{{ confidenceThreshold.toFixed(2) }}</span>
            </div>
            <el-slider v-model="confidenceThreshold" :min="0.05" :max="0.9" :step="0.05" :disabled="isDetecting" />
          </div>

          <div class="setting-item">
            <div class="setting-label">
              <span>检测帧率</span>
              <span class="setting-val">{{ detectionFPS }} fps</span>
            </div>
            <el-slider v-model="detectionFPS" :min="2" :max="12" :step="1" :disabled="isDetecting" />
          </div>

          <div class="detection-actions">
            <el-button
              v-if="!isDetecting"
              type="primary"
              :disabled="!hasVideo"
              @click="startRealtimeDetection"
            >
              <el-icon><VideoPlay /></el-icon>开始检测
            </el-button>
            <el-button v-else type="danger" @click="stopRealtimeDetection">
              <el-icon><VideoPause /></el-icon>停止检测
            </el-button>
            <el-button :disabled="isDetecting" @click="triggerFileInput">
              <el-icon><Upload /></el-icon>上传
            </el-button>
          </div>
        </div>

        <div class="side-card results-card">
          <div class="side-card-hd">
            <span>检测结果</span>
            <span v-if="currentDetection" class="results-badge">{{ currentDetection.total_objects || 0 }}</span>
          </div>
          <div v-if="!isDetecting && !currentDetection" class="results-empty">等待检测</div>
          <div v-else-if="currentDetection && currentDetection.boxes.length === 0" class="results-empty">未检测到目标</div>
          <div v-else-if="currentDetection" class="results-list">
            <div v-for="(box, i) in currentDetection.boxes" :key="i" class="result-tag">
              <span class="tag-dot" :style="{ background: getColor(box.class_name) }"></span>
              {{ box.chinese_name || box.class_name }}
              <span class="tag-pct">{{ (box.confidence * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount, nextTick } from "vue";
import { ElMessage } from "element-plus";
import { VideoCamera, VideoPlay, VideoPause, Upload } from "@element-plus/icons-vue";
import { detectRealtimeFrame } from "../api/detection";

const CLASS_COLORS = {
  Raw_Banana: "oklch(0.55 0.12 145)",
  Raw_Mango: "oklch(0.55 0.12 85)",
  Ripe_Banana: "oklch(0.60 0.15 85)",
  Ripe_Mango: "oklch(0.58 0.16 65)",
};

function getColor(className) {
  return CLASS_COLORS[className] || "oklch(0.52 0.10 178)";
}

const videoRef = ref(null);
const canvasRef = ref(null);
const hasVideo = ref(false);
const videoUrl = ref(null);
const videoDuration = ref(0);
const currentTime = ref(0);
const currentFrameIndex = ref(0);
const isDetecting = ref(false);
const currentDetection = ref(null);

const confidenceThreshold = ref(0.25);
const detectionFPS = ref(5);

let detectionTimer = null;
let animationFrameId = null;
let canvasContext = null;
let lastBoxes = [];
let lastVideoWidth = 0;
let lastVideoHeight = 0;
let isProcessingFrame = false;

function formatDuration(seconds) {
  if (!seconds || seconds <= 0) return "--:--";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
}

function triggerFileInput() {
  const input = document.querySelector(".video-file-input-hidden");
  if (input) input.click();
}

function handleVideoUpload(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  if (videoUrl.value) URL.revokeObjectURL(videoUrl.value);

  videoUrl.value = URL.createObjectURL(file);
  hasVideo.value = true;
  currentDetection.value = null;
  currentFrameIndex.value = 0;
  currentTime.value = 0;
  lastBoxes = [];

  event.target.value = "";
}

function onVideoLoaded() {
  const video = videoRef.value;
  if (video) {
    videoDuration.value = video.duration;
    nextTick(() => initCanvas());
  }
}

function onTimeUpdate() {
  const video = videoRef.value;
  if (video) currentTime.value = video.currentTime;
}

function onVideoEnded() {
  if (isDetecting.value) {
    stopRealtimeDetection();
    ElMessage.success("视频播放完成");
  }
}

function initCanvas() {
  const video = videoRef.value;
  const canvas = canvasRef.value;
  if (!video || !canvas) return;
  const dw = video.clientWidth || video.offsetWidth;
  const dh = video.clientHeight || video.offsetHeight;
  canvas.width = dw;
  canvas.height = dh;
  canvasContext = canvas.getContext("2d");
  clearCanvas();
}

function clearCanvas() {
  if (!canvasContext || !canvasRef.value) return;
  canvasContext.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
}

function drawBoxes(boxes, videoWidth, videoHeight, interpolate) {
  if (!canvasContext || !canvasRef.value || !videoRef.value) return;

  const canvas = canvasRef.value;
  const video = videoRef.value;
  const dw = video.clientWidth || video.offsetWidth;
  const dh = video.clientHeight || video.offsetHeight;

  if (canvas.width !== dw || canvas.height !== dh) {
    canvas.width = dw;
    canvas.height = dh;
  }

  const scaleX = dw / videoWidth;
  const scaleY = dh / videoHeight;

  canvasContext.clearRect(0, 0, dw, dh);

  let toDraw = boxes;
  let refW = videoWidth;
  let refH = videoHeight;
  if (interpolate && lastBoxes.length > 0) {
    toDraw = lastBoxes;
    refW = lastVideoWidth;
    refH = lastVideoHeight;
  }

  for (const box of toDraw) {
    const x1 = box.x1 * scaleX;
    const y1 = box.y1 * scaleY;
    const x2 = box.x2 * scaleX;
    const y2 = box.y2 * scaleY;
    const w = x2 - x1;
    const h = y2 - y1;
    const color = getColor(box.class_name);

    canvasContext.strokeStyle = color;
    canvasContext.lineWidth = 2;
    canvasContext.strokeRect(x1, y1, w, h);

    canvasContext.fillStyle = color;
    canvasContext.globalAlpha = 0.12;
    canvasContext.fillRect(x1, y1, w, h);
    canvasContext.globalAlpha = 1;

    const label = `${box.chinese_name || box.class_name} ${(box.confidence * 100).toFixed(0)}%`;
    canvasContext.font = "bold 11px 'Inter', system-ui, sans-serif";
    const tw = canvasContext.measureText(label).width + 8;
    const th = 18;
    const ly = y1 >= th ? y1 - th : y1 + h;

    canvasContext.fillStyle = color;
    canvasContext.fillRect(x1, ly, tw, th);
    canvasContext.fillStyle = "#fff";
    canvasContext.fillText(label, x1 + 4, ly + 13);
  }

  if (!interpolate) {
    lastBoxes = toDraw;
    lastVideoWidth = refW;
    lastVideoHeight = refH;
  }
}

function animateLoop() {
  if (!isDetecting.value) return;
  const video = videoRef.value;
  if (video && !video.paused && !video.ended && lastBoxes.length > 0) {
    drawBoxes([], lastVideoWidth, lastVideoHeight, true);
  }
  animationFrameId = requestAnimationFrame(animateLoop);
}

async function captureAndDetect() {
  const video = videoRef.value;
  if (!video || video.paused || video.ended || isProcessingFrame) return;

  isProcessingFrame = true;
  try {
    const tempCanvas = document.createElement("canvas");
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const ctx = tempCanvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    const blob = await new Promise(resolve => {
      tempCanvas.toBlob(b => resolve(b), "image/jpeg", 0.6);
    });
    if (!blob) { isProcessingFrame = false; return; }

    const formData = new FormData();
    formData.append("file", blob, "frame.jpg");
    formData.append("confidence_threshold", confidenceThreshold.value.toString());
    formData.append("iou_threshold", "0.7");

    const response = await detectRealtimeFrame(formData);
    if (response.success && response.data) {
      currentDetection.value = response.data;
      const boxes = response.data.boxes || [];
      drawBoxes(boxes, response.data.image_width, response.data.image_height);
      currentFrameIndex.value++;
    }
  } catch {
    // silently skip failed frames
  } finally {
    isProcessingFrame = false;
  }
}

async function startRealtimeDetection() {
  const video = videoRef.value;
  if (!video) { ElMessage.error("视频未加载"); return; }

  if (video.readyState < 2) {
    ElMessage.info("加载视频中...");
    await new Promise(resolve => {
      video.onloadeddata = resolve;
      setTimeout(resolve, 10000);
    });
  }
  if (video.readyState < 2) { ElMessage.error("视频加载失败"); return; }

  isDetecting.value = true;
  currentDetection.value = null;
  currentFrameIndex.value = 0;
  lastBoxes = [];
  isProcessingFrame = false;

  nextTick(() => { initCanvas(); clearCanvas(); });
  await nextTick();

  try { await video.play(); }
  catch { ElMessage.warning("自动播放被阻止，请手动点击播放"); }

  animateLoop();

  const intervalMs = Math.floor(1000 / detectionFPS.value);
  detectionTimer = setInterval(captureAndDetect, intervalMs);
  ElMessage.success("开始实时检测");
}

function stopRealtimeDetection() {
  if (detectionTimer) { clearInterval(detectionTimer); detectionTimer = null; }
  if (animationFrameId) { cancelAnimationFrame(animationFrameId); animationFrameId = null; }
  const video = videoRef.value;
  if (video) video.pause();
  isDetecting.value = false;
  clearCanvas();
  lastBoxes = [];
  isProcessingFrame = false;
}

onBeforeUnmount(() => {
  stopRealtimeDetection();
  if (videoUrl.value) URL.revokeObjectURL(videoUrl.value);
});
</script>

<style scoped lang="scss">
.video-detection {
  width: 100%;
}

.video-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

/* ---- Video panel ---- */
.video-panel {
  flex: 1;
  min-width: 0;
}

.video-viewport {
  position: relative;
  width: 100%;
  background: oklch(0.12 0.005 185);
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-subtle);
  aspect-ratio: 16 / 9;
}

.video-player {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
}

.detection-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s;
}
.detection-canvas.canvas-active { opacity: 1; }

.video-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 13px;
  background: oklch(0.10 0.005 185 / 0.85);
}
.placeholder-hint {
  font-size: 11px;
  opacity: 0.5;
}

.video-file-input-hidden { display: none; }

.video-hud {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 6px;
  z-index: 3;
}
.hud-item {
  padding: 3px 8px;
  background: oklch(0.08 0.005 185 / 0.78);
  backdrop-filter: blur(8px);
  border-radius: var(--radius-xs);
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: var(--text-muted);
  border: 1px solid oklch(0.30 0.01 185 / 0.25);
}
.hud-value {
  color: var(--text-primary);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.video-info-bar {
  display: flex;
  gap: 18px;
  padding: 8px 12px;
  font-size: 11px;
  color: var(--text-secondary);
  background: var(--bg-surface);
  border-radius: var(--radius-sm);
  margin-top: 8px;
  border: 1px solid var(--border-subtle);
}

/* ---- Side panel ---- */
.side-panel {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.side-card {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  border: 1px solid var(--border-subtle);
}

.side-card-hd {
  font-size: 11px;
  font-weight: 620;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.setting-item {
  margin-bottom: 14px;
}
.setting-label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.setting-val {
  color: var(--accent);
  font-weight: 540;
  font-variant-numeric: tabular-nums;
}

.detection-actions {
  display: flex;
  gap: 8px;
}

.results-badge {
  font-size: 10px;
  font-weight: 620;
  color: var(--accent);
  background: var(--accent-soft);
  padding: 1px 7px;
  border-radius: var(--radius-full);
}

.results-empty {
  font-size: 12px;
  color: var(--text-muted);
  padding: 16px 0;
  text-align: center;
}

.results-card {
  flex: 1;
  max-height: 300px;
  overflow-y: auto;
}

.results-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.result-tag {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 9px;
  background: var(--bg-glass);
  border-radius: var(--radius-full);
  font-size: 11px;
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
}

.tag-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  flex-shrink: 0;
}
.tag-pct {
  color: var(--text-muted);
  font-weight: 500;
}
</style>
