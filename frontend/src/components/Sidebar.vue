<template>
  <div class="sidebar-container">
    <div class="logo-section">
      <div class="logo-icon">
        <el-icon :size="18"><Picture /></el-icon>
      </div>
      <span class="logo-title">RSOD</span>
    </div>

    <nav class="nav-menu">
      <div
        v-for="item in menuList"
        :key="item.path"
        class="nav-item"
        :class="{ active: currentPath === item.path }"
        @click="handleMenuClick(item)"
      >
        <el-icon :size="17" class="nav-icon"><component :is="item.icon" /></el-icon>
        <span class="nav-text">{{ item.name }}</span>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="user-chip" @click="handleMenuClick({ path: '/profile' })">
        <el-avatar :size="26" class="footer-avatar">
          <img
            src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
            alt="用户头像"
          />
        </el-avatar>
        <span class="footer-name">{{ userStore.displayName }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  Picture, Clock, ChatDotRound, Grid, User,
} from "@element-plus/icons-vue";
import { useUserStore } from "../stores/user";

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const menuList = [
  { name: "智能检测", icon: Picture, path: "/detection" },
  { name: "历史记录", icon: Clock, path: "/history" },
  { name: "AI 问答", icon: ChatDotRound, path: "/qa" },
  { name: "目标库", icon: Grid, path: "/targets" },
  { name: "个人中心", icon: User, path: "/profile" },
];

const currentPath = computed(() => route.path);

const handleMenuClick = (item) => {
  router.push(item.path);
};
</script>

<style scoped>
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo-section {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 18px;
  gap: 10px;
  border-bottom: 1px solid var(--border-subtle);
}

.logo-icon {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.logo-title {
  font-size: 15px;
  font-weight: 650;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.nav-menu {
  flex: 1;
  padding: 14px 10px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 9px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color 0.25s cubic-bezier(0.16, 1, 0.3, 1),
              color 0.25s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 450;
  position: relative;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  transform: translateX(1px);
}

.nav-item.active {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 600;
  box-shadow: inset 0 0 0 1px oklch(0.58 0.10 175 / 0.10),
              0 0 12px oklch(0.58 0.10 175 / 0.06);
}

.nav-item.active .nav-icon {
  color: var(--accent);
}

.nav-icon {
  margin-right: 10px;
  flex-shrink: 0;
  color: inherit;
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.nav-item:hover .nav-icon {
  transform: scale(1.05);
}

.nav-text {
  line-height: 1;
}

.sidebar-footer {
  padding: 12px 10px;
  border-top: 1px solid var(--border-subtle);
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 7px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.user-chip:hover {
  background: var(--bg-hover);
}

.footer-name {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}
</style>
