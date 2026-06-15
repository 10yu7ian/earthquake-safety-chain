<template>
  <div class="login-page">
    <div class="ambient-grid" aria-hidden="true" />
    <div class="orb orb-cyan" aria-hidden="true" />
    <div class="orb orb-violet" aria-hidden="true" />

    <div class="login-shell">
      <div class="brand-pane">
        <div class="brand-top">
          <div class="logo-box">
            <svg viewBox="0 0 24 24" width="26" height="26" fill="none" aria-hidden="true">
              <path
                d="M12 2L4.5 5v6.5c0 4.7 3.2 9 7.5 10.5 4.3-1.5 7.5-5.8 7.5-10.5V5L12 2z"
                stroke="url(#loginLogo)"
                stroke-width="1.8"
              />
              <path
                d="M9 12l2.2 2.2L15.2 10.2"
                stroke="url(#loginLogo)"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <defs>
                <linearGradient id="loginLogo" x1="0" y1="0" x2="24" y2="24">
                  <stop offset="0%" stop-color="#00d1ff" />
                  <stop offset="100%" stop-color="#a855f7" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div class="brand-name">
            <span class="brand gradient-text">地震安链</span>
            <span class="brand-sub">地震安链 · 安全联防</span>
          </div>
        </div>

        <h2 class="slogan">
          为每一户家庭<br />建造一道<span class="gradient-text">无形盾牌</span>
        </h2>

        <div class="feature-list">
          <div class="feature-item">
            <span class="dot dot-cyan" />
            <div>
              <p class="feature-title">毫秒级燃气切断</p>
              <p class="feature-desc">地震/燃气泄漏双通道响应</p>
            </div>
          </div>
          <div class="feature-item">
            <span class="dot dot-violet" />
            <div>
              <p class="feature-title">实时节点分布</p>
              <p class="feature-desc">全市社区监控与联动</p>
            </div>
          </div>
          <div class="feature-item">
            <span class="dot dot-success" />
            <div>
              <p class="feature-title">可视化分析</p>
              <p class="feature-desc">KPI 与事件趋势一屏掌握</p>
            </div>
          </div>
        </div>

        <p class="copyright">© 2026 地震安链 · All rights reserved.</p>
      </div>

      <div class="login-card">
        <div class="card-glow" aria-hidden="true" />
        <div class="card-inner">
          <div class="card-header">
            <span class="kicker">身份验证</span>
            <h1 class="card-title">欢迎回来</h1>
            <p class="card-tip">请选择角色并输入凭据以进入控制台</p>
          </div>

          <el-form class="login-form" label-position="top" @submit.prevent="handleLogin">
            <el-form-item label="用户名">
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                autocomplete="username"
                clearable
              />
            </el-form-item>

            <el-form-item label="密码">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                autocomplete="current-password"
                show-password
              />
            </el-form-item>

            <el-form-item label="角色">
              <div class="role-switch">
                <button
                  type="button"
                  class="role-option"
                  :class="{ active: form.role === 'admin' }"
                  @click="form.role = 'admin'"
                >
                  <span class="role-ic">A</span>
                  <span>
                    <strong>管理员</strong>
                    <small>监控·调度</small>
                  </span>
                </button>
                <button
                  type="button"
                  class="role-option"
                  :class="{ active: form.role === 'resident' }"
                  @click="form.role = 'resident'"
                >
                  <span class="role-ic violet">R</span>
                  <span>
                    <strong>居民</strong>
                    <small>家庭看板</small>
                  </span>
                </button>
              </div>
            </el-form-item>

            <el-button
              class="login-btn"
              type="primary"
              :loading="loading"
              @click="handleLogin"
            >
              登 录 进 入 控 制 台
            </el-button>

            <div class="hint">
              <span>演示账号：</span>
              <code>admin / admin123</code>
              <span class="sep">·</span>
              <code>user / user123</code>
            </div>
          </el-form>

          <p class="version-text">地震安链 · v1.0.0 (2026.04)</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { login } from "@/api";

const router = useRouter();

const form = reactive({
  username: "",
  password: "",
  role: "admin",
});

const loading = ref(false);

const handleLogin = async () => {
  const { username, password, role } = form;

  if (!username || !password || !role) {
    ElMessage.error("请完整填写登录信息");
    return;
  }

  loading.value = true;
  try {
    const data = await login(username, password);
    if (!data?.access_token) {
      ElMessage.error("登录失败：未获取到令牌");
      return;
    }

    // 与后端约定一致：admin 为管理员，user 为居民；避免界面选错角色导致路由与令牌不一致
    const resolvedRole = username === "admin" ? "admin" : "resident";
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", resolvedRole);

    ElMessage.success("登录成功，正在进入系统");
    router.push(resolvedRole === "admin" ? "/dashboard" : "/resident");
  } catch (error) {
    const detail = error?.response?.data?.detail;
    const text =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d) => d.msg || JSON.stringify(d)).join("; ")
          : error?.message === "Network Error"
            ? "无法连接后端：请确认已启动 API（127.0.0.1:8000）后再试"
            : "账号或密码错误，请检查后重试";
    ElMessage.error(text);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped lang="scss">
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  overflow: hidden;
}

.ambient-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: radial-gradient(ellipse at 50% 40%, #000 30%, transparent 75%);
  pointer-events: none;
}

.orb {
  position: absolute;
  width: 520px;
  height: 520px;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.45;
  pointer-events: none;
}

.orb-cyan {
  top: -180px;
  left: -160px;
  background: radial-gradient(circle, rgba(0, 209, 255, 0.55), transparent 70%);
}

.orb-violet {
  bottom: -180px;
  right: -200px;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.5), transparent 70%);
}

.login-shell {
  position: relative;
  display: grid;
  grid-template-columns: 1.05fr 440px;
  gap: 40px;
  width: min(1100px, 100%);
  padding: 22px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.55);
}

@media (max-width: 920px) {
  .login-shell {
    grid-template-columns: 1fr;
  }
  .brand-pane {
    display: none;
  }
}

.brand-pane {
  position: relative;
  padding: 30px;
  border-radius: 22px;
  background: linear-gradient(
    160deg,
    rgba(0, 209, 255, 0.08) 0%,
    rgba(168, 85, 247, 0.06) 60%,
    transparent 100%
  );
  border: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
}

.brand-pane::after {
  content: "";
  position: absolute;
  right: -60px;
  top: 40px;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 209, 255, 0.18), transparent 70%);
  filter: blur(20px);
  pointer-events: none;
}

.brand-top {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-box {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(0, 209, 255, 0.1);
  border: 1px solid rgba(0, 209, 255, 0.4);
  display: grid;
  place-items: center;
  box-shadow: 0 0 22px rgba(0, 209, 255, 0.3);
}

.brand-name {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.brand {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.brand-sub {
  font-size: 11px;
  color: #64748b;
  letter-spacing: 0.24em;
  margin-top: 3px;
}

.slogan {
  font-size: 34px;
  font-weight: 700;
  color: #f1f5f9;
  line-height: 1.35;
  letter-spacing: 0.02em;
  margin: 26px 0;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.feature-title {
  margin: 0;
  color: #e2e8f0;
  font-weight: 600;
}

.feature-desc {
  margin: 2px 0 0;
  color: #94a3b8;
  font-size: 13px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}

.dot-cyan {
  background: #00d1ff;
  box-shadow: 0 0 12px rgba(0, 209, 255, 0.8);
}

.dot-violet {
  background: #a855f7;
  box-shadow: 0 0 12px rgba(168, 85, 247, 0.75);
}

.dot-success {
  background: #22d3a5;
  box-shadow: 0 0 12px rgba(34, 211, 165, 0.8);
}

.copyright {
  margin: 24px 0 0;
  color: #475569;
  font-size: 12px;
  letter-spacing: 0.08em;
}

.login-card {
  position: relative;
  border-radius: 22px;
  background: rgba(12, 13, 18, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.55);
  overflow: hidden;
}

.card-glow {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(300px 120px at 20% 0%, rgba(0, 209, 255, 0.2), transparent 70%),
    radial-gradient(280px 120px at 80% 100%, rgba(168, 85, 247, 0.2), transparent 70%);
  pointer-events: none;
}

.card-inner {
  position: relative;
  padding: 34px 30px 28px;
}

.card-header {
  margin-bottom: 22px;
}

.kicker {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(0, 209, 255, 0.1);
  border: 1px solid rgba(0, 209, 255, 0.35);
  color: #a8eaff;
  font-size: 11px;
  letter-spacing: 0.18em;
}

.card-title {
  margin: 12px 0 6px;
  font-size: 28px;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: 0.02em;
}

.card-tip {
  margin: 0;
  color: #94a3b8;
  font-size: 13px;
}

.role-switch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.role-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.role-option strong {
  display: block;
  color: #f1f5f9;
  font-size: 14px;
}

.role-option small {
  color: #94a3b8;
  font-size: 11px;
  letter-spacing: 0.04em;
}

.role-option:hover {
  border-color: rgba(0, 209, 255, 0.45);
  background: rgba(0, 209, 255, 0.06);
}

.role-option.active {
  border-color: rgba(0, 209, 255, 0.8);
  background: linear-gradient(135deg, rgba(0, 209, 255, 0.18), rgba(168, 85, 247, 0.12));
  box-shadow: 0 0 0 1px rgba(0, 209, 255, 0.45), 0 0 22px rgba(0, 209, 255, 0.2);
}

.role-ic {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: rgba(0, 209, 255, 0.12);
  border: 1px solid rgba(0, 209, 255, 0.45);
  color: #a8eaff;
  display: grid;
  place-items: center;
  font-weight: 700;
  font-family: var(--font-family-mono);
}

.role-ic.violet {
  background: rgba(168, 85, 247, 0.12);
  border-color: rgba(168, 85, 247, 0.5);
  color: #d4b5ff;
}

.login-btn {
  width: 100%;
  height: 46px;
  margin-top: 6px;
  border-radius: 12px;
  letter-spacing: 0.32em;
  font-weight: 700;
  font-size: 14px;
}

.hint {
  margin-top: 14px;
  text-align: center;
  color: #64748b;
  font-size: 12px;
  letter-spacing: 0.02em;
}

.hint code {
  color: #a8eaff;
  background: rgba(0, 209, 255, 0.08);
  padding: 2px 8px;
  border-radius: 6px;
  border: 1px solid rgba(0, 209, 255, 0.25);
  font-family: var(--font-family-mono);
  font-size: 11px;
  margin: 0 4px;
}

.hint .sep {
  color: #475569;
}

.version-text {
  margin: 18px 0 0;
  text-align: center;
  color: #475569;
  font-size: 11px;
  letter-spacing: 0.2em;
}
</style>
