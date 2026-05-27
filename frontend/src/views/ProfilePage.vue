<template>
  <div class="profile-page">
    <div class="profile-grid">
      <!-- Left column: user card + stats -->
      <div class="profile-main">
        <div class="user-card">
          <div class="user-card-top">
            <div class="avatar-wrap" @click="triggerAvatar" title="点击更换头像">
              <el-avatar :size="80" :src="userStore.user?.avatar_url || ''">
                <span class="avatar-fallback">{{ (userStore.displayName || '?')[0].toUpperCase() }}</span>
              </el-avatar>
              <div class="avatar-overlay">
                <el-icon :size="18"><Camera /></el-icon>
              </div>
              <input
                ref="avatarInput"
                type="file"
                accept="image/*"
                class="avatar-input-hidden"
                @change="handleAvatarUpload"
              />
            </div>
            <div class="user-meta">
              <div class="user-display-name">{{ userStore.displayName }}</div>
              <div class="user-username">@{{ userStore.user?.username }}</div>
              <div class="user-meta-row">
                <span class="meta-tag">{{ roleText }}</span>
                <span class="meta-tag secondary">{{ userStore.user?.email }}</span>
              </div>
              <div class="user-join">加入于 {{ formatDate(userStore.user?.created_at) }}</div>
            </div>
          </div>
          <div class="user-card-actions">
            <button class="act-btn" @click="openEditProfile"><el-icon :size="13"><Edit /></el-icon>编辑资料</button>
            <button class="act-btn" @click="openChangePassword"><el-icon :size="13"><Lock /></el-icon>修改密码</button>
          </div>
        </div>

        <div class="stats-grid">
          <div class="stat-cell">
            <span class="stat-num">{{ stats.total_detections }}</span>
            <span class="stat-label">总检测次数</span>
          </div>
          <div class="stat-cell">
            <span class="stat-num">{{ stats.total_objects }}</span>
            <span class="stat-label">累计检测目标</span>
          </div>
          <div class="stat-cell">
            <span class="stat-num">{{ stats.success_rate }}<span class="stat-unit">%</span></span>
            <span class="stat-label">检测成功率</span>
          </div>
          <div class="stat-cell">
            <span class="stat-num">{{ stats.active_days }}</span>
            <span class="stat-label">使用天数</span>
          </div>
          <div class="stat-cell">
            <span class="stat-num">{{ stats.this_month }}</span>
            <span class="stat-label">本月检测</span>
          </div>
          <div class="stat-cell">
            <span class="stat-num">{{ stats.avg_objects_per_detection }}</span>
            <span class="stat-label">平均目标数</span>
          </div>
        </div>
      </div>

      <!-- Right column: settings -->
      <div class="profile-side">
        <div class="side-card">
          <div class="side-card-hd">账户安全</div>
          <div class="security-list">
            <div class="security-row">
              <div class="sec-info">
                <span class="sec-name">密码</span>
                <span class="sec-desc">定期更换密码保护账户安全</span>
              </div>
              <button class="sec-btn" @click="openChangePassword">修改</button>
            </div>
            <div class="security-row">
              <div class="sec-info">
                <span class="sec-name">邮箱</span>
                <span class="sec-desc">{{ userStore.user?.email || '未绑定' }}</span>
              </div>
              <button class="sec-btn" @click="openEditProfile">修改</button>
            </div>
          </div>
        </div>

        <div class="side-card">
          <div class="side-card-hd">账户信息</div>
          <div class="info-kv-list">
            <div class="info-kv"><span class="kv-k">用户名</span><span class="kv-v">{{ userStore.user?.username }}</span></div>
            <div class="info-kv"><span class="kv-k">角色</span><span class="kv-v">{{ roleText }}</span></div>
            <div class="info-kv"><span class="kv-k">注册时间</span><span class="kv-v">{{ formatDate(userStore.user?.created_at) }}</span></div>
            <div class="info-kv"><span class="kv-k">账号状态</span><span class="kv-v status-active">
              <span class="status-dot"></span>正常
            </span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Profile Dialog -->
    <el-dialog v-model="editVisible" title="编辑资料" width="420px" destroy-on-close>
      <el-form :model="editForm" label-width="60px" label-position="left">
        <el-form-item label="昵称">
          <el-input v-model="editForm.nickname" placeholder="输入昵称" maxlength="30" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" placeholder="输入邮箱" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>

    <!-- Change Password Dialog -->
    <el-dialog v-model="passwordVisible" title="修改密码" width="420px" destroy-on-close>
      <el-form :model="passwordForm" label-width="80px" label-position="left">
        <el-form-item label="原密码">
          <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="输入原密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="输入新密码（至少6位）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordLoading" @click="savePassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Camera, Edit, Lock } from "@element-plus/icons-vue";
import { useUserStore } from "../stores/user";
import { getProfile, updateProfile, changePassword, uploadAvatar } from "../api/auth";

const userStore = useUserStore();

const stats = ref({
  total_detections: 0,
  total_objects: 0,
  success_rate: 0,
  active_days: 0,
  this_month: 0,
  avg_objects_per_detection: 0,
});

const roleText = computed(() => {
  const r = userStore.user?.role;
  if (r === "admin") return "管理员";
  if (r === "operator") return "操作员";
  return "普通用户";
});

function formatDate(s) {
  if (!s) return "--";
  return new Date(s).toLocaleDateString("zh-CN", { year: "numeric", month: "long", day: "numeric" });
}

// ---- Profile edit ----
const editVisible = ref(false);
const editLoading = ref(false);
const editForm = ref({ nickname: "", email: "" });

function openEditProfile() {
  editForm.value.nickname = userStore.user?.nickname || "";
  editForm.value.email = userStore.user?.email || "";
  editVisible.value = true;
}

async function saveProfile() {
  editLoading.value = true;
  try {
    const res = await updateProfile({
      nickname: editForm.value.nickname || undefined,
      email: editForm.value.email || undefined,
    });
    if (res.code === 200) {
      userStore.user = res.user;
      localStorage.setItem("user", JSON.stringify(res.user));
      stats.value = res.stats;
      ElMessage.success("资料已更新");
      editVisible.value = false;
    }
  } catch {
    // handled by interceptor
  } finally {
    editLoading.value = false;
  }
}

// ---- Password change ----
const passwordVisible = ref(false);
const passwordLoading = ref(false);
const passwordForm = ref({ old_password: "", new_password: "" });

function openChangePassword() {
  passwordForm.value = { old_password: "", new_password: "" };
  passwordVisible.value = true;
}

async function savePassword() {
  if (passwordForm.value.new_password.length < 6) {
    ElMessage.warning("新密码至少6位");
    return;
  }
  passwordLoading.value = true;
  try {
    await changePassword(passwordForm.value);
    ElMessage.success("密码修改成功，请重新登录");
    passwordVisible.value = false;
    setTimeout(() => {
      userStore.logout();
      window.location.href = "/login";
    }, 1200);
  } catch {
    // handled by interceptor
  } finally {
    passwordLoading.value = false;
  }
}

// ---- Avatar upload ----
const avatarInput = ref(null);

function triggerAvatar() {
  avatarInput.value?.click();
}

async function handleAvatarUpload(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  try {
    const res = await uploadAvatar(file);
    if (res.code === 200) {
      userStore.user = { ...userStore.user, avatar_url: res.avatar_url };
      localStorage.setItem("user", JSON.stringify(userStore.user));
      ElMessage.success("头像已更新");
    }
  } catch {
    // handled by interceptor
  }
  event.target.value = "";
}

// ---- Load data ----
async function loadData() {
  try {
    const res = await getProfile();
    if (res.code === 200) {
      userStore.user = res.user;
      localStorage.setItem("user", JSON.stringify(res.user));
      stats.value = res.stats;
    }
  } catch {
    // handled by interceptor
  }
}

onMounted(() => {
  loadData();
});
</script>

<style scoped lang="scss">
.profile-page {
  width: 100%;
  max-width: 1000px;
}

.profile-grid {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.profile-main {
  flex: 1;
  min-width: 0;
}

/* ---- User card ---- */
.user-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid var(--border-card);
  box-shadow: var(--shadow-sm);
  margin-bottom: 20px;
}

.user-card-top {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.avatar-wrap {
  position: relative;
  cursor: pointer;
  flex-shrink: 0;
  border-radius: 50%;

  &:hover .avatar-overlay {
    opacity: 1;
  }
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: oklch(0 0 0 / 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.25s ease;
  color: #fff;
}

.avatar-fallback {
  font-size: 28px;
  font-weight: 620;
  color: var(--accent);
}

.avatar-input-hidden { display: none; }

.user-meta {
  flex: 1;
  min-width: 0;
}

.user-display-name {
  font-size: 22px;
  font-weight: 640;
  color: var(--text-primary);
  letter-spacing: -0.01em;
  margin-bottom: 2px;
}

.user-username {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.user-meta-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.meta-tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 520;
}

.meta-tag.secondary {
  background: var(--bg-glass);
  color: var(--text-secondary);
}

.user-join {
  font-size: 11px;
  color: var(--text-muted);
}

.user-card-actions {
  display: flex;
  gap: 8px;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid var(--border-subtle);
}

.act-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 14px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  color: var(--text-secondary);
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  transition: all 0.2s ease;

  &:hover {
    color: var(--text-primary);
    border-color: var(--border-card);
    background: var(--bg-hover);
  }
}

/* ---- Stats grid ---- */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-cell {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: 22px 18px;
  text-align: center;
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-xs);
  transition: border-color 0.3s ease;

  &:hover {
    border-color: oklch(0.56 0.08 178 / 0.18);
  }
}

.stat-num {
  display: block;
  font-size: 28px;
  font-weight: 680;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.stat-unit {
  font-size: 16px;
  font-weight: 480;
  color: var(--text-muted);
}

.stat-label {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 6px;
}

/* ---- Side column ---- */
.profile-side {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.side-card {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: 16px 18px;
  border: 1px solid var(--border-subtle);
}

.side-card-hd {
  font-size: 11px;
  font-weight: 620;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 14px;
}

.security-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.security-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sec-name {
  display: block;
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 520;
}

.sec-desc {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 1px;
}

.sec-btn {
  padding: 4px 12px;
  border-radius: var(--radius-xs);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  color: var(--accent);
  background: var(--accent-soft);
  border: 1px solid transparent;
  transition: all 0.2s ease;

  &:hover {
    background: var(--accent);
    color: #fff;
  }
}

.info-kv-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-kv {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kv-k {
  font-size: 12px;
  color: var(--text-muted);
}

.kv-v {
  font-size: 12px;
  font-weight: 520;
  color: var(--text-primary);
}

.status-active {
  display: flex;
  align-items: center;
  gap: 5px;
}

.status-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--success);
}
</style>
