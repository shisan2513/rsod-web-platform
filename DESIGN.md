# Design

## Register

product

## Theme — Dark pro

**Scene:** 遥感专业学生在教室或宿舍桌面上使用平台，下午自然光充足或夜间台灯环境，屏幕为笔记本 14-16 寸。用户专注操作：选图、检测、看结果，不需要长时间凝视阅读，但需要清晰的视觉反馈。界面应像专业摄影器材的操作面板——暗色、精准、安静、不抢戏。

暗色主题选择理由：遥感影像本身就是高饱和彩色图像，暗色界面能让图像成为唯一视觉焦点，类似 Lightroom 的暗色工作区逻辑。

## Color

### Strategy: Restrained

暗色底座 + 单一冷调强调色。界面 90% 为暗色中性色，强调色仅用于操作按钮、激活态、数据高亮。让遥感图像的色彩承担所有视觉张力。

### Palette

```
Root bg:        oklch(0.14 0.008 255)   — near-black, blue-leaning
Surface:        oklch(0.18 0.006 255)   — card, panel
Surface raised: oklch(0.22 0.005 255)   — hover, overlay
Border subtle:  oklch(0.24 0.005 255)   — separator
Border strong:  oklch(0.32 0.006 255)   — focus, active border
Text primary:   oklch(0.92 0.002 255)   — heading, body
Text secondary: oklch(0.65 0.008 255)   — label, meta
Text muted:     oklch(0.45 0.006 255)   — placeholder, hint
Accent:         oklch(0.62 0.14 230)    — buttons, links, active states
Accent hover:   oklch(0.68 0.15 230)
Accent soft:    oklch(0.22 0.04 240)    — selected bg, tag
Success:        oklch(0.62 0.13 160)
Danger:         oklch(0.58 0.15 20)
```

### Application

- Primary buttons, active nav items, links → Accent
- Sidebar, header → Surface + backdrop-blur
- Content area bg → Root bg, no white
- Cards → Surface
- Detection result tags → Accent soft bg + Accent text
- Confidence values → Success

## Typography

### Font

System font stack, Apple platforms get SF Pro via system-ui:

```
-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", system-ui, sans-serif
```

### Scale

```
Page title:   28px / 600  — 检测页标题
Card title:   16px / 600  — 卡片标题
Body:         14px / 400  — 正文、列表
Label:        13px / 400  — 标签、元信息
Caption:      12px / 400  — 辅助信息
```

### Rules

- 中文正文 line-height: 1.6
- 标题 line-height: 1.3
- 数字（置信度、统计值）用 tabular-nums
- 标题与正文间距 ≥标题字号 × 0.5

## Spacing

### Rhythm

```
xs:  4px   — icon-label gap
sm:  8px   — inline gap
md:  16px  — card padding, list gap
lg:  24px  — section gap, page padding
xl:  32px  — page header bottom
2xl: 48px  — major section separation
```

### Layout

- 内容区 padding: 32px（水平）, 24px（顶部，页面头部自带节奏）
- 卡片 padding: 20-24px，内部元素间距 16px
- 侧边栏宽度: 220px
- 顶栏高度: 64px

## Elevation & Surface

Apple 式的深度通过透明度分层而非阴影堆叠：

- **Root bg** — 最低层，内容在此之上浮动
- **Surface cards** — 比 root 亮约 4%，微弱的 1px 细亮边框（border subtle），不使用阴影
- **Raised / hover** — 再亮 4%，用于 hover 状态和临时浮层
- **Header / Sidebar** — backdrop-blur(20px) + 半透明深色背景，产生磨砂玻璃效果

不使用 box-shadow 卡片。深度通过明度差和细微边框传达。

### Frosted glass

Sidebar, Header, Modal backdrop 使用：

```css
background: oklch(0.16 0.004 255 / 0.85);
backdrop-filter: blur(20px) saturate(1.4);
-webkit-backdrop-filter: blur(20px) saturate(1.4);
border-right: 1px solid oklch(0.24 0.005 255);
```

## Border Radius

```
sm:  6px   — tag, badge, small button
md:  10px  — card, input, dropdown
lg:  16px  — modal, large panel
full: 9999px — avatar, pill
```

## Icons

Element Plus Icons (填入式，2px 线宽风格)。大小阶梯：14 / 16 / 18 / 20 / 24px。

## Motion

- 页面切换：无动画（路由即显）
- Hover：150ms ease-out，仅变背景色
- Tab 切换：active 指示器 200ms ease-out
- 数值更新：无动画，直接替换
- 加载态：Element Plus 默认 spinner

不弹跳、不弹性、不渐变入场。Apple 的动画克制——快且不引人注意。

## Components

### Sidebar
- 磨砂玻璃底 + 右侧细线分隔
- 当前页：accent soft 背景 + 左侧 3px accent 指示条
- 收起/展开：不实现，保持 220px 固定

### Header
- 磨砂玻璃底 + 底部细线分隔
- 左侧面包屑，右侧操作区
- 用户头像 32px 圆形

### Card
- Surface 背景，1px subtle 边框
- 内部标题区 + 内容区
- 不使用阴影

### Button
- Primary: accent 实色底 + 白色文字，hover 加深
- Secondary: surface 底 + subtle 边框，hover 亮起
- 圆角 6-8px，高度 36-40px

### Empty state
- 居中的图标 + 说明文字 + 可选操作按钮
- 图标使用 muted 色，不抢眼

## Anti-patterns (reinforced from PRODUCT.md)

- 禁止白色背景（#fff / #ffffff），用 surface token 替代
- 禁止纯黑文字（#000）
- 禁止大阴影卡片
- 禁止渐变按钮
- 禁止彩色侧边条纹（border-left accent 仅限 nav active indicator，3px 以内且仅用于导航）
- 禁止表格堆砌
- 禁止霓虹/赛博朋克配色

## Implementation

所有色值使用 OKLCH 格式写入 `:root` CSS 变量。变量名使用 `--` 前缀的 kebab-case。组件通过 `var(--token)` 引用，不硬编码色值。
