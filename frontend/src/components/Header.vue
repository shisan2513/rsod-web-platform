<template>
  <div class="header-container">
    <div class="header-left">
      <div class="breadcrumbs">
        <span class="breadcrumb-text">{{ route.name }}</span>
      </div>
    </div>

    <div class="header-center">
      <el-select
        :model-value="modelStore.currentModel"
        @update:model-value="modelStore.setModel"
        size="small"
        class="model-select"
      >
        <el-option label="YOLO11n" value="yolo11n" />
        <el-option label="YOLO11s" value="yolo11s" />
        <el-option label="YOLO11m" value="yolo11m" />
      </el-select>
    </div>

    <div class="header-right">
      <div class="status-indicator">
        <span class="status-dot"></span>
        <span class="status-text">就绪</span>
      </div>

      <div class="action-icons">
        <el-icon class="action-icon" :size="17"><Bell /></el-icon>
        <el-icon class="action-icon" :size="17"><QuestionFilled /></el-icon>
      </div>

      <div class="user-dropdown" @click="router.push('/profile')">
        <span class="user-name">{{ userStore.displayName }}</span>
        <el-avatar :size="28" class="user-avatar">
          <img
            src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
            alt="用户头像"
          />
        </el-avatar>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
import { Bell, QuestionFilled } from "@element-plus/icons-vue";
import { useUserStore } from "../stores/user";

const userStore = useUserStore();
import { useModelStore } from "../stores/model";

const route = useRoute();
const router = useRouter();
const modelStore = useModelStore();
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 24px;
}

.header-left {
  flex-shrink: 0;
}

.breadcrumbs {
  display: flex;
  align-items: center;
}

.breadcrumb-text {
  font-size: 13px;
  font-weight: 480;
  color: var(--text-secondary);
  letter-spacing: -0.01em;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.model-select {
  width: 150px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  background: oklch(0.90 0.04 155 / 0.30);
  border: 1px solid oklch(0.55 0.10 155 / 0.10);
}

.status-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--success);
  animation: status-breathe 2.4s ease-in-out infinite;
}

@keyframes status-breathe {
  0%, 100% { opacity: 1; box-shadow: 0 0 4px oklch(0.52 0.12 155 / 0.4); }
  50% { opacity: 0.5; box-shadow: 0 0 8px oklch(0.52 0.12 155 / 0.15); }
}

.status-text {
  font-size: 12px;
  color: var(--success);
  font-weight: 500;
}

.action-icons {
  display: flex;
  align-items: center;
  gap: 2px;
}

.action-icon {
  color: var(--text-secondary);
  padding: 5px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: color 0.2s ease, background-color 0.2s ease;
}

.action-icon:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 2px;
  border-radius: var(--radius-full);
  transition: box-shadow 0.25s ease;
}

.user-dropdown:hover {
  box-shadow: 0 0 0 3px var(--accent-soft);
}
</style>
