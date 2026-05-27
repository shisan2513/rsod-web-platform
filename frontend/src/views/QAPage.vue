<template>
  <div class="qa-page">
    <div class="page-header">
      <h1 class="page-title">AI 问答</h1>
      <p class="page-subtitle">关于遥感目标检测的任何问题，都可以问我</p>
    </div>

    <div class="chat-container">
      <div class="chat-messages">
        <div class="message ai-message">
          <div class="message-avatar">
            <el-icon :size="16"><ChatDotRound /></el-icon>
          </div>
          <div class="message-bubble">
            <p>你好，我是遥感目标检测 AI 助手。可以帮你解答关于飞机、油罐、操场、立交桥、农业病虫害等遥感目标检测的相关问题，也可以为你提供检测结果的详细分析。</p>
          </div>
        </div>

        <div v-for="(msg, i) in messages" :key="i" class="message" :class="msg.role === 'user' ? 'user-message' : 'ai-message'">
          <div v-if="msg.role === 'ai'" class="message-avatar">
            <el-icon :size="16"><ChatDotRound /></el-icon>
          </div>
          <div class="message-bubble">{{ msg.content }}</div>
          <div v-if="msg.role === 'user'" class="message-avatar user-avatar">
            <el-icon :size="16"><User /></el-icon>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="question"
          placeholder="输入你的问题..."
          :rows="2"
          type="textarea"
        />
        <button class="send-btn" :class="{ loading: sending }" @click="sendMessage">
          <el-icon v-if="!sending" :size="18"><Position /></el-icon>
          <el-icon v-else :size="18" class="spin"><Loading /></el-icon>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { ChatDotRound, User, Position, Loading } from "@element-plus/icons-vue";

const question = ref("");
const sending = ref(false);
const messages = ref([]);

const sendMessage = () => {
  if (!question.value.trim() || sending.value) return;
  const text = question.value.trim();
  messages.value.push({ role: "user", content: text });
  question.value = "";
  sending.value = true;
  setTimeout(() => {
    messages.value.push({ role: "ai", content: "这是一个模拟回复。AI 问答功能将在后续版本中接入大语言模型。" });
    sending.value = false;
  }, 1200);
};
</script>

<style scoped lang="scss">
.qa-page { width: 100%; max-width: 800px; height: 100%; display: flex; flex-direction: column; }
.page-header { margin-bottom: 24px; }
.page-title { font-size: 26px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; letter-spacing: -0.01em; }
.page-subtitle { font-size: 14px; color: var(--text-secondary); }

.chat-container {
  flex: 1; background: var(--bg-surface); border-radius: var(--radius-lg);
  border: 1px solid var(--border-card); box-shadow: var(--shadow-sm);
  display: flex; flex-direction: column; overflow: hidden;
}

.chat-messages { flex: 1; padding: 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; }

.message { display: flex; align-items: flex-start; gap: 10px; max-width: 85%; }
.ai-message { align-self: flex-start; }
.user-message { align-self: flex-end; flex-direction: row-reverse; }

.message-avatar {
  width: 32px; height: 32px; border-radius: var(--radius-full);
  background: var(--accent-soft); color: var(--accent);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.user-message .user-avatar { background: var(--bg-hover); color: var(--text-secondary); }

.message-bubble {
  padding: 10px 16px; border-radius: var(--radius-md); font-size: 14px;
  line-height: 1.6; color: var(--text-primary);
  background: var(--bg-hover);
}
.user-message .message-bubble { background: var(--accent-soft); color: var(--text-primary); }

.chat-input {
  padding: 16px 20px; border-top: 1px solid var(--border-subtle);
  display: flex; gap: 10px; align-items: flex-end;
}

.send-btn {
  width: 40px; height: 40px; border-radius: var(--radius-sm);
  background: var(--accent); color: #fff; border: none;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; flex-shrink: 0;
  transition: background-color 0.2s ease;
}
.send-btn:hover { background: var(--accent-hover); }
.send-btn.loading { background: var(--accent-soft); color: var(--accent); }

.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
