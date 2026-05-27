<template>
  <div class="camera-detection">
    <div class="camera-viewport">
      <video ref="videoRef" class="camera-video" autoplay playsinline muted />
      <canvas ref="canvasRef" class="camera-canvas" />

      <div v-if="!isActive" class="camera-placeholder">
        <el-icon :size="48"><VideoCamera /></el-icon>
        <span>点击"开始检测"启动摄像头</span>
      </div>

      <div v-if="isActive && isPaused" class="camera-pause-overlay">
        <el-icon :size="48"><VideoPause /></el-icon>
        <span>已暂停</span>
      </div>

      <div class="camera-hud">
        <div class="hud-item">
          <span class="hud-label">FPS</span>
          <span class="hud-value">{{ fps }}</span>
        </div>
        <div class="hud-item">
          <span class="hud-label">帧数</span>
          <span class="hud-value">{{ frameIndex }}</span>
        </div>
        <div class="hud-item">
          <span class="hud-label">目标</span>
          <span class="hud-value">{{ totalObjects }}</span>
        </div>
        <div class="hud-item">
          <span class="hud-label">耗时</span>
          <span class="hud-value">{{ detectionTime }}ms</span>
        </div>
      </div>
    </div>

    <div class="camera-controls">
      <el-button v-if="!isActive" type="primary" @click="start" :loading="starting">
        <el-icon><VideoPlay /></el-icon>开始检测
      </el-button>
      <template v-else>
        <el-button v-if="isPaused" type="primary" @click="resume">
          <el-icon><VideoPlay /></el-icon>恢复
        </el-button>
        <el-button v-else @click="pause">
          <el-icon><VideoPause /></el-icon>暂停
        </el-button>
        <el-button type="danger" @click="stop">
          <el-icon><Close /></el-icon>停止
        </el-button>
      </template>
    </div>

    <div v-if="isActive" class="detected-list">
      <div v-if="currentBoxes.length === 0" class="detected-empty">未检测到目标</div>
      <div v-for="(box, i) in currentBoxes" :key="i" class="detected-tag">
        <span class="dot" :style="{ background: getBoxColor(box.class_name) }"></span>
        {{ box.chinese_name || box.class_name }}
        <span class="tag-pct">{{ (box.confidence * 100).toFixed(0) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from "vue";
import { ElMessage } from "element-plus";
import { VideoCamera, VideoPlay, VideoPause, Close } from "@element-plus/icons-vue";
import { detectFrame, startCameraDetection, stopCameraDetection } from "../api/detection";

const videoRef = ref(null);
const canvasRef = ref(null);
const isActive = ref(false);
const isPaused = ref(false);
const starting = ref(false);
const fps = ref(0);
const frameIndex = ref(0);
const totalObjects = ref(0);
const detectionTime = ref(0);
const currentBoxes = ref([]);

let videoStream = null;
let captureCanvas = null;
let captureCtx = null;
let detectionFrameId = null;
let drawFrameId = null;
let lastDetectionTime = 0;
let errorCount = 0;
const maxErrors = 10;

const CLASS_COLORS = {
  Raw_Banana: "oklch(0.55 0.12 145)",
  Raw_Mango: "oklch(0.55 0.12 85)",
  Ripe_Banana: "oklch(0.60 0.15 85)",
  Ripe_Mango: "oklch(0.58 0.16 65)",
};

function getBoxColor(className) {
  return CLASS_COLORS[className] || "oklch(0.52 0.10 178)";
}

function initCanvas() {
  captureCanvas = document.createElement("canvas");
  captureCtx = captureCanvas.getContext("2d");
}

function syncCanvasSize() {
  const video = videoRef.value;
  const canvas = canvasRef.value;
  if (!video || !canvas) return;
  const w = video.videoWidth || 640;
  const h = video.videoHeight || 480;
  canvas.width = w;
  canvas.height = h;
  if (captureCanvas) {
    captureCanvas.width = w;
    captureCanvas.height = h;
  }
}

function drawBoxes() {
  const canvas = canvasRef.value;
  const video = videoRef.value;
  if (!canvas || !video) return;

  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const scaleX = canvas.width / (video.videoWidth || 640);
  const scaleY = canvas.height / (video.videoHeight || 480);

  for (const box of currentBoxes.value) {
    const x1 = box.x1 * scaleX;
    const y1 = box.y1 * scaleY;
    const x2 = box.x2 * scaleX;
    const y2 = box.y2 * scaleY;
    const w = x2 - x1;
    const h = y2 - y1;
    const color = getBoxColor(box.class_name);

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.strokeRect(x1, y1, w, h);

    ctx.fillStyle = color;
    ctx.globalAlpha = 0.12;
    ctx.fillRect(x1, y1, w, h);
    ctx.globalAlpha = 1;

    const label = `${box.chinese_name || box.class_name} ${(box.confidence * 100).toFixed(0)}%`;
    ctx.font = "bold 12px 'Inter', system-ui, sans-serif";
    const textW = ctx.measureText(label).width + 8;
    const textH = 18;
    const labelY = y1 >= textH ? y1 - textH : y1 + h;

    ctx.fillStyle = color;
    ctx.fillRect(x1, labelY, textW, textH);
    ctx.fillStyle = "#fff";
    ctx.fillText(label, x1 + 4, labelY + 13);
  }
}

function drawLoop() {
  if (!isActive.value) return;
  drawBoxes();
  drawFrameId = requestAnimationFrame(drawLoop);
}

async function sendFrame() {
  if (!isActive.value) return;

  const now = performance.now();
  const interval = 200;
  if (now - lastDetectionTime < interval) {
    detectionFrameId = requestAnimationFrame(sendFrame);
    return;
  }

  const video = videoRef.value;
  if (!video || !captureCtx || video.readyState < 2) {
    detectionFrameId = requestAnimationFrame(sendFrame);
    return;
  }

  if (!isPaused.value) {
    try {
      if (!captureCanvas.width) syncCanvasSize();
      captureCtx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);
      const dataUrl = captureCanvas.toDataURL("image/jpeg", 0.7);

      const response = await detectFrame({ image: dataUrl });
      if (response.success) {
        currentBoxes.value = response.data.boxes || [];
        frameIndex.value = response.data.frame_index || frameIndex.value;
        fps.value = response.data.fps || fps.value;
        detectionTime.value = response.data.detection_time
          ? Math.round(response.data.detection_time * 1000)
          : 0;
        totalObjects.value = response.data.total_objects || 0;
        errorCount = 0;
        lastDetectionTime = now;
      } else {
        handleError(response.message);
      }
    } catch (err) {
      handleError(err.message || "网络请求失败");
    }
  }

  detectionFrameId = requestAnimationFrame(sendFrame);
}

function handleError(msg) {
  errorCount++;
  if (errorCount <= 1) {
    ElMessage.warning(msg);
  }
  if (errorCount >= maxErrors) {
    ElMessage.error("连续检测失败，已自动停止");
    stop();
  }
}

function handleCameraError(error) {
  switch (error.name) {
    case "NotAllowedError":
      ElMessage.error("摄像头权限被拒绝，请在浏览器设置中允许访问");
      break;
    case "NotFoundError":
      ElMessage.error("未检测到摄像头设备");
      break;
    case "NotReadableError":
      ElMessage.error("摄像头被其他应用占用");
      break;
    default:
      ElMessage.error("无法访问摄像头，请检查设备");
  }
  cleanup();
}

async function start() {
  starting.value = true;
  try {
    await startCameraDetection({
      confidence_threshold: 0.5,
      iou_threshold: 0.7,
    });
  } catch {
    ElMessage.error("启动检测服务失败");
    starting.value = false;
    return;
  }

  try {
    videoStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        frameRate: { ideal: 30 },
      },
      audio: false,
    });

    const video = videoRef.value;
    video.srcObject = videoStream;
    video.onloadedmetadata = () => {
      initCanvas();
      syncCanvasSize();
      isActive.value = true;
      isPaused.value = false;
      starting.value = false;
      currentBoxes.value = [];
      errorCount = 0;
      drawFrameId = requestAnimationFrame(drawLoop);
      detectionFrameId = requestAnimationFrame(sendFrame);
    };
  } catch (err) {
    starting.value = false;
    handleCameraError(err);
    stopCameraDetection().catch(() => {});
  }
}

function pause() {
  isPaused.value = true;
}

function resume() {
  isPaused.value = false;
  lastDetectionTime = 0;
}

function cleanup() {
  isActive.value = false;
  isPaused.value = false;
  starting.value = false;
  if (detectionFrameId) cancelAnimationFrame(detectionFrameId);
  if (drawFrameId) cancelAnimationFrame(drawFrameId);
  detectionFrameId = null;
  drawFrameId = null;
  if (videoStream) {
    videoStream.getTracks().forEach(t => t.stop());
    videoStream = null;
  }
  if (videoRef.value) videoRef.value.srcObject = null;
  currentBoxes.value = [];
  fps.value = 0;
  frameIndex.value = 0;
  totalObjects.value = 0;
  detectionTime.value = 0;
}

function stop() {
  cleanup();
  stopCameraDetection().catch(() => {});
}

onBeforeUnmount(() => {
  cleanup();
  stopCameraDetection().catch(() => {});
});
</script>

<style scoped lang="scss">
.camera-detection {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.camera-viewport {
  position: relative;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  aspect-ratio: 4 / 3;
  background: oklch(0.12 0.005 185);
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-subtle);
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.camera-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.camera-placeholder,
.camera-pause-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-muted);
  font-size: 14px;
  background: oklch(0.10 0.005 185 / 0.85);
  backdrop-filter: blur(4px);
  z-index: 2;
}

.camera-hud {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 8px;
  z-index: 3;
}

.hud-item {
  padding: 4px 10px;
  background: oklch(0.08 0.005 185 / 0.78);
  backdrop-filter: blur(8px);
  border-radius: var(--radius-xs);
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text-muted);
  border: 1px solid oklch(0.30 0.01 185 / 0.25);
}

.hud-value {
  color: var(--text-primary);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.camera-controls {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.detected-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  max-width: 800px;
  margin: 0 auto;
}

.detected-empty {
  font-size: 12px;
  color: var(--text-muted);
  padding: 8px 0;
}

.detected-tag {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  background: var(--bg-glass);
  border-radius: var(--radius-full);
  font-size: 11px;
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-pct {
  color: var(--text-muted);
  font-weight: 500;
}
</style>
