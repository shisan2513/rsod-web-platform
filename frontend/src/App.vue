<template>
  <router-view v-if="isAuthPage" />
  <MainLayout v-else>
    <template #sidebar>
      <Sidebar />
    </template>
    <template #header>
      <Header />
    </template>
    <template #content>
      <router-view />
    </template>
  </MainLayout>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import MainLayout from "./layouts/MainLayout.vue";
import Sidebar from "./components/Sidebar.vue";
import Header from "./components/Header.vue";

const route = useRoute();

const isAuthPage = computed(() => {
  const authPaths = ["/login", "/register", "/forgot-password"];
  return authPaths.includes(route.path);
});
</script>

<style>
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  /* Background — cool gray-green atmosphere, never white */
  --bg-root: oklch(0.965 0.003 178);
  --bg-surface: oklch(0.978 0.002 175);
  --bg-raised: oklch(0.99 0.001 175);
  --bg-hover: oklch(0.945 0.004 175);
  --bg-glass: oklch(0.972 0.002 178 / 0.68);
  --bg-dim: oklch(0.955 0.002 178 / 0.55);

  /* Borders — ghost-like, barely there */
  --border-subtle: oklch(0.895 0.003 175);
  --border-card: oklch(0.87 0.004 175);
  --border-input: oklch(0.83 0.004 172);
  --border-glow: oklch(0.56 0.10 178 / 0.20);

  /* Typography — high contrast on detection area, muted elsewhere */
  --text-primary: oklch(0.14 0.004 180);
  --text-secondary: oklch(0.38 0.006 175);
  --text-muted: oklch(0.54 0.005 172);

  /* Accent — cold mint-teal, precise */
  --accent: oklch(0.49 0.11 178);
  --accent-hover: oklch(0.54 0.12 178);
  --accent-soft: oklch(0.91 0.04 175);
  --accent-muted: oklch(0.87 0.03 172);
  --accent-gradient: linear-gradient(135deg, oklch(0.52 0.11 180), oklch(0.47 0.12 173));

  /* Semantic */
  --success: oklch(0.50 0.12 158);
  --warning: oklch(0.56 0.10 85);
  --danger: oklch(0.48 0.15 25);

  /* Shadows — cold-tinted ambient */
  --shadow-xs: 0 1px 2px oklch(0.12 0.003 185 / 0.035);
  --shadow-sm: 0 1px 3px oklch(0.12 0.003 185 / 0.045),
               0 1px 2px oklch(0.12 0.003 185 / 0.03);
  --shadow-md: 0 4px 20px oklch(0.12 0.003 185 / 0.065),
               0 0 0 1px oklch(0.12 0.003 185 / 0.025);
  --shadow-lg: 0 8px 40px oklch(0.12 0.003 185 / 0.085),
               0 0 0 1px oklch(0.12 0.003 185 / 0.035);
  --shadow-btn: 0 2px 10px oklch(0.35 0.08 178 / 0.18);
  --shadow-glow: 0 0 16px oklch(0.52 0.10 178 / 0.12);
  --shadow-hero: 0 0 40px oklch(0.48 0.10 178 / 0.08),
                 0 0 80px oklch(0.50 0.08 180 / 0.04);

  /* Radii */
  --radius-xs: 5px;
  --radius-sm: 9px;
  --radius-md: 13px;
  --radius-lg: 17px;
  --radius-xl: 21px;
  --radius-full: 9999px;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-3xl: 64px;
}

/* Element Plus overrides — light theme */
html {
  --el-color-primary: var(--accent);
  --el-color-primary-light-3: oklch(0.72 0.08 175);
  --el-color-primary-light-5: oklch(0.82 0.06 175);
  --el-color-primary-light-7: oklch(0.90 0.04 170);
  --el-color-primary-light-9: oklch(0.95 0.02 168);
  --el-color-primary-dark-2: oklch(0.45 0.10 175);
  --el-bg-color-page: var(--bg-root);
  --el-bg-color: var(--bg-surface);
  --el-bg-color-overlay: var(--bg-raised);
  --el-text-color-primary: var(--text-primary);
  --el-text-color-regular: var(--text-primary);
  --el-text-color-secondary: var(--text-secondary);
  --el-text-color-placeholder: var(--text-muted);
  --el-border-color: var(--border-card);
  --el-border-color-light: var(--border-subtle);
  --el-border-color-lighter: var(--border-subtle);
  --el-border-color-extra-light: oklch(0.93 0.003 168);
  --el-border-color-dark: oklch(0.80 0.005 165);
  --el-fill-color: oklch(0.95 0.003 168);
  --el-fill-color-light: oklch(0.97 0.002 170);
  --el-fill-color-lighter: oklch(0.98 0.001 170);
  --el-fill-color-blank: transparent;
  --el-color-success: var(--success);
  --el-color-warning: var(--warning);
  --el-color-danger: var(--danger);
  --el-mask-color: oklch(0.15 0.005 180 / 0.35);
  --el-border-radius-base: var(--radius-sm);
  --el-border-radius-small: var(--radius-xs);
  --el-border-radius-round: var(--radius-full);
}

/* Noise texture overlay */
html::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: none;
  opacity: 0.032;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.82' numOctaves='5' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 200px 200px;
}

html {
  background:
    radial-gradient(ellipse 80% 60% at 50% 30%, oklch(0.60 0.04 180 / 0.07) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 85% 80%, oklch(0.55 0.03 185 / 0.04) 0%, transparent 55%),
    var(--bg-root);
  color: var(--text-primary);
  font-size: 15px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", "PingFang SC", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  line-height: 1.55;
  min-height: 100vh;
}

#app { min-height: 100vh; }
</style>
