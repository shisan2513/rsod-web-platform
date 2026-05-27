<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="page-title">个人中心</h1>
      <p class="page-subtitle">管理你的账户信息和使用统计</p>
    </div>

    <div class="profile-content">
      <div class="user-info-card">
        <div class="user-avatar-section">
          <el-avatar :size="72">
            <img
              src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
              alt="用户头像"
            />
          </el-avatar>
          <div class="user-basic-info">
            <div class="user-name">{{ userStore.displayName }}</div>
            <div class="user-role">{{ userStore.user?.email || '普通用户' }}</div>
            <button class="edit-btn">编辑资料</button>
          </div>
        </div>
      </div>

      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-value">128</div>
          <div class="stat-label">总检测次数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">892</div>
          <div class="stat-label">累计检测目标</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">98.5%</div>
          <div class="stat-label">检测成功率</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">12</div>
          <div class="stat-label">使用天数</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from "../stores/user";

const userStore = useUserStore();
</script>

<style scoped lang="scss">
.profile-page { width: 100%; max-width: 900px; }
.page-header { margin-bottom: 28px; }
.page-title { font-size: 26px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; letter-spacing: -0.01em; }
.page-subtitle { font-size: 14px; color: var(--text-secondary); }
.profile-content { display: flex; flex-direction: column; gap: 24px; }
.user-info-card {
  background: var(--bg-surface); border-radius: var(--radius-lg); padding: 28px;
  border: 1px solid var(--border-card); box-shadow: var(--shadow-sm);
}
.user-avatar-section { display: flex; align-items: center; }
.user-basic-info { margin-left: 24px; }
.user-name { font-size: 22px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.user-role { font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; }
.edit-btn {
  padding: 6px 16px; border-radius: var(--radius-sm); font-size: 12px; font-weight: 500;
  color: var(--accent); background: var(--accent-soft); border: 1px solid transparent;
  cursor: pointer; transition: all 0.2s ease;
}
.edit-btn:hover { background: var(--accent); color: #fff; }
.stats-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.stat-card {
  background: var(--bg-surface); border-radius: var(--radius-md); padding: 24px 20px;
  text-align: center; border: 1px solid var(--border-card); box-shadow: var(--shadow-xs);
}
.stat-value { font-size: 30px; font-weight: 700; color: var(--accent); margin-bottom: 6px; font-variant-numeric: tabular-nums; }
.stat-label { font-size: 13px; color: var(--text-muted); }
</style>
