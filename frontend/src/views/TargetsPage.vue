<template>
  <div class="targets-page">
    <div class="page-header">
      <h1 class="page-title">目标库</h1>
      <p class="page-subtitle">平台支持检测的所有遥感目标类别</p>
    </div>

    <div class="search-container">
      <el-input v-model="searchQuery" placeholder="搜索目标类别..." size="default" class="search-input">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon target-icon"><el-icon :size="18"><Aim /></el-icon></div>
        <div class="stat-info">
          <div class="stat-value">{{ totalTargets }}</div>
          <div class="stat-label">目标总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon category-icon"><el-icon :size="18"><Grid /></el-icon></div>
        <div class="stat-info">
          <div class="stat-value">{{ categories.length }}</div>
          <div class="stat-label">类别数量</div>
        </div>
      </div>
    </div>

    <div class="target-categories">
      <div v-for="category in filteredCategories" :key="category.id" class="category-card">
        <div class="category-header">
          <div class="category-icon" :style="{ backgroundColor: category.color }">
            <component :is="category.icon" />
          </div>
          <div class="category-info">
            <div class="category-name">{{ category.name }}</div>
            <div class="category-count">{{ category.targets.length }} 个目标</div>
          </div>
        </div>
        <div class="target-list">
          <div v-for="target in category.targets" :key="target.id" class="target-item" @click="showTargetDetail(target)">
            <span>{{ target.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredCategories.length === 0" class="empty-state">
      <el-icon :size="56" class="empty-icon"><Search /></el-icon>
      <p class="empty-text">未找到匹配的目标类别</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  Search, Aim, Grid, Bicycle, OfficeBuilding, Sunny, Setting,
} from "@element-plus/icons-vue";

const searchQuery = ref("");

const categories = ref([
  { id: 1, name: "交通工具类", icon: Bicycle, color: "#4d8c6e", targets: [
    { id: 1, name: "飞机", categoryId: 1 }, { id: 2, name: "船舶", categoryId: 1 }, { id: 3, name: "汽车", categoryId: 1 }, { id: 4, name: "火车", categoryId: 1 }, { id: 5, name: "卡车", categoryId: 1 },
  ]},
  { id: 2, name: "建筑设施类", icon: OfficeBuilding, color: "#5a8a7a", targets: [
    { id: 6, name: "油罐", categoryId: 2 }, { id: 7, name: "立交桥", categoryId: 2 }, { id: 8, name: "体育场", categoryId: 2 }, { id: 9, name: "港口", categoryId: 2 }, { id: 10, name: "机场跑道", categoryId: 2 },
  ]},
  { id: 3, name: "自然地貌类", icon: Sunny, color: "#7a9460", targets: [
    { id: 11, name: "湖泊", categoryId: 3 }, { id: 12, name: "河流", categoryId: 3 }, { id: 13, name: "森林", categoryId: 3 }, { id: 14, name: "农田", categoryId: 3 }, { id: 15, name: "山地", categoryId: 3 },
  ]},
  { id: 4, name: "其他目标", icon: Setting, color: "#6e7d8a", targets: [
    { id: 16, name: "风力发电机", categoryId: 4 }, { id: 17, name: "太阳能板", categoryId: 4 }, { id: 18, name: "桥梁", categoryId: 4 }, { id: 19, name: "烟囱", categoryId: 4 }, { id: 20, name: "储水池", categoryId: 4 },
  ]},
]);

const filteredCategories = computed(() => {
  if (!searchQuery.value) return categories.value;
  const query = searchQuery.value.toLowerCase();
  return categories.value.map((category) => ({
    ...category,
    targets: category.targets.filter((target) => target.name.toLowerCase().includes(query)),
  })).filter((category) => category.name.toLowerCase().includes(query) || category.targets.length > 0);
});

const totalTargets = computed(() => categories.value.reduce((sum, cat) => sum + cat.targets.length, 0));

const showTargetDetail = (target) => console.log("查看目标:", target);
</script>

<style scoped lang="scss">
.targets-page { width: 100%; max-width: 1100px; }
.page-header { margin-bottom: 28px; }
.page-title { font-size: 26px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; letter-spacing: -0.01em; }
.page-subtitle { font-size: 14px; color: var(--text-secondary); }
.search-container { margin-bottom: 24px; }
.search-input { max-width: 280px; }
.stats-cards { display: flex; gap: 16px; margin-bottom: 28px; }
.stat-card {
  flex: 1; max-width: 200px; background: var(--bg-surface); border-radius: var(--radius-md);
  padding: 18px 20px; border: 1px solid var(--border-card); box-shadow: var(--shadow-xs);
  display: flex; align-items: center; gap: 14px;
}
.stat-icon { width: 44px; height: 44px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; color: #fff; }
.target-icon { background: oklch(0.48 0.08 155); }
.category-icon { background: var(--accent); }
.stat-value { font-size: 22px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; }
.stat-label { font-size: 12px; color: var(--text-muted); }
.target-categories { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.category-card {
  background: var(--bg-surface); border-radius: var(--radius-md); padding: 20px 24px;
  border: 1px solid var(--border-card); box-shadow: var(--shadow-xs);
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.category-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.category-header { display: flex; align-items: center; margin-bottom: 16px; }
.category-icon { width: 44px; height: 44px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 20px; margin-right: 14px; }
.category-name { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 3px; }
.category-count { font-size: 12px; color: var(--text-muted); }
.target-list { display: flex; flex-wrap: wrap; gap: 8px; }
.target-item {
  padding: 6px 14px; background: var(--bg-hover); border-radius: var(--radius-full);
  font-size: 13px; color: var(--text-secondary); cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.target-item:hover { background: var(--accent-soft); color: var(--accent); }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 0; }
.empty-icon { color: var(--text-muted); margin-bottom: 16px; }
.empty-text { font-size: 15px; color: var(--text-secondary); }
</style>
