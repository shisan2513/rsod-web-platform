<template>
  <div class="forgot-container">
    <div class="forgot-card">
      <div class="forgot-header">
        <div class="logo-icon">
          <el-icon :size="22"><Lock /></el-icon>
        </div>
        <h1 class="forgot-title">找回密码</h1>
        <p class="forgot-subtitle">输入注册邮箱，我们将发送重置链接</p>
      </div>

      <el-form
        ref="forgotFormRef"
        :model="forgotForm"
        :rules="forgotRules"
        class="forgot-form"
      >
        <el-form-item prop="email">
          <el-input
            v-model="forgotForm.email"
            placeholder="注册邮箱"
            size="large"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" class="submit-btn" @click="handleSubmit">
            发送重置链接
          </el-button>
        </el-form-item>
      </el-form>

      <div class="back-link">
        <span>想起密码了？</span>
        <router-link to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { Lock, Message } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

const router = useRouter();

const forgotForm = reactive({
  email: "",
});

const forgotRules = {
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
};

const forgotFormRef = ref(null);

const handleSubmit = () => {
  forgotFormRef.value.validate((valid) => {
    if (valid) {
      ElMessage.success("重置链接已发送到您的邮箱");
      setTimeout(() => {
        router.push("/login");
      }, 1500);
    }
  });
};
</script>

<style scoped>
.forgot-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at 50% 0%, oklch(0.60 0.06 175 / 0.10) 0%, transparent 60%),
              radial-gradient(ellipse at 85% 80%, oklch(0.58 0.05 170 / 0.06) 0%, transparent 50%),
              var(--bg-root);
}

.forgot-card {
  width: 100%;
  max-width: 400px;
  padding: 44px 40px;
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-card);
  box-shadow: var(--shadow-lg);
}

.forgot-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  width: 44px;
  height: 44px;
  margin: 0 auto 14px;
  background: var(--accent);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.forgot-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
  letter-spacing: 0.02em;
}

.forgot-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
}

.forgot-form {
  margin-bottom: 24px;
}

.submit-btn {
  width: 100%;
  height: 44px;
  border-radius: var(--radius-sm);
  font-size: 15px;
  font-weight: 500;
}

.back-link {
  text-align: center;
  font-size: 13px;
  color: var(--text-secondary);
}

.back-link a {
  color: var(--accent);
  margin-left: 4px;
}

.back-link a:hover {
  text-decoration: underline;
}
</style>
