# 📊 图表 Blocks 完整设计方案

> 配合表格处理 Blocks 的数据可视化能力扩展方案

---

## 📋 目录

1. [方案概述](#方案概述)
2. [Block 清单总览](#block-清单总览)
3. [第一层级: 核心图表 Blocks (P0)](#第一层级-核心图表-blocks-p0)
4. [第二层级: 高级图表 Blocks (P1)](#第二层级-高级图表-blocks-p1)
5. [第三层级: 专业图表 Blocks (P2)](#第三层级-专业图表-blocks-p2)
6. [与表格 Blocks 集成](#与表格-blocks-集成)
7. [实施优先级建议](#实施优先级建议)
8. [技术栈建议](#技术栈建议)
9. [与 OOMOL Agent 集成](#与-oomol-agent-集成)
10. [设计亮点](#设计亮点)

---

## 方案概述

### 设计目标

让 OOMOL Agent 成为**数据可视化专家**,能够智能地将表格数据转换为各类图表,帮助用户快速洞察数据、发现趋势、展示结果。

### 核心原则

- **数据驱动**: 根据数据类型自动推荐最合适的图表
- **无缝集成**: 与表格 Blocks 完美串联,形成完整的数据分析链
- **声明式配置**: 用户只需描述"想看什么",Block 自动处理细节
- **多格式输出**: 支持 PNG/SVG/HTML/JSON 等多种导出格式
- **交互性可选**: 支持静态图表和交互式 Web 图表

### 设计理念

**不同于传统图表库的繁琐配置,我们的 Block 应该像这样使用:**

```typescript
// ❌ 传统方式 - 繁琐的配置
const chart = new Chart();
chart.setType("bar");
chart.setXAxis({ type: 'category', data: [...] });
chart.setYAxis({ type: 'value' });
chart.setSeries([{ type: 'bar', data: [...] }]);
// ... 100+ 行配置

// ✅ 我们的方式 - 简洁的 Block
@oomol/chart-bar({
  data: salesData,
  category: "region",
  value: "sales",
  title: "Sales by Region"
})
```

---

## Block 清单总览

| 优先级 | Block 名称 | 核心功能 | 适用场景 | 开发难度 | 预估工时 | 使用频率 |
|--------|-----------|---------|---------|----------|---------|---------|
| **P0** | `@oomol/chart-generator` | 智能图表生成器 | 自动推荐图表类型 | ⭐⭐⭐⭐ | 56h | ⭐⭐⭐⭐⭐ |
| **P0** | `@oomol/chart-bar` | 柱状图/条形图 | 分类对比 | ⭐⭐ | 24h | ⭐⭐⭐⭐⭐ |
| **P0** | `@oomol/chart-line` | 折线图 | 趋势展示 | ⭐⭐ | 24h | ⭐⭐⭐⭐⭐ |
| **P0** | `@oomol/chart-pie` | 饼图/环形图 | 占比分析 | ⭐⭐ | 20h | ⭐⭐⭐⭐ |
| **P0** | `@oomol/chart-scatter` | 散点图/气泡图 | 相关性分析 | ⭐⭐⭐ | 24h | ⭐⭐⭐⭐ |
| **P1** | `@oomol/chart-heatmap` | 热力图 | 矩阵数据可视化 | ⭐⭐⭐ | 32h | ⭐⭐⭐ |
| **P1** | `@oomol/chart-box` | 箱线图 | 分布分析 | ⭐⭐⭐ | 28h | ⭐⭐⭐ |
| **P1** | `@oomol/chart-histogram` | 直方图 | 数据分布 | ⭐⭐ | 20h | ⭐⭐⭐ |
| **P1** | `@oomol/chart-area` | 面积图 | 累积趋势 | ⭐⭐ | 20h | ⭐⭐⭐ |
| **P1** | `@oomol/chart-combo` | 组合图表 | 多指标展示 | ⭐⭐⭐⭐ | 40h | ⭐⭐⭐ |
| **P2** | `@oomol/chart-waterfall` | 瀑布图 | 累积变化 | ⭐⭐⭐ | 28h | ⭐⭐ |
| **P2** | `@oomol/chart-radar` | 雷达图 | 多维度对比 | ⭐⭐⭐ | 24h | ⭐⭐ |
| **P2** | `@oomol/chart-treemap` | 树状图 | 层级结构 | ⭐⭐⭐⭐ | 32h | ⭐⭐ |
| **P2** | `@oomol/chart-sankey` | 桑基图 | 流向分析 | ⭐⭐⭐⭐ | 36h | ⭐⭐ |
| **P2** | `@oomol/chart-gauge` | 仪表盘 | 指标监控 | ⭐⭐ | 20h | ⭐⭐ |

**总工时**: ~428 小时 (约 **2.5-3 个月, 2 人团队**)

---

## 第一层级: 核心图表 Blocks (P0)

> 必须实现的基础能力,覆盖 85% 的日常可视化需求

### 1️⃣ `@oomol/chart-generator` - 智能图表生成器

**功能描述**: 智能分析数据特征并自动推荐或创建最合适的图表类型

**适用场景**:
- 快速生成图表,不确定用哪种类型
- 让 AI 自动选择最佳图表
- 一站式图表创建

#### 输入端口 (Input Schema)

```typescript
{
  data: Array<Record<string, any>>;      // 表格数据 (来自 table-* blocks)
  chartType?: "auto" | "bar" | "line" | "pie" |
              "scatter" | "heatmap" | "box" | "area";

  // 数据映射
  x?: string | string[];                 // X轴字段
  y?: string | string[];                 // Y轴字段
  series?: string;                       // 系列字段 (用于分组)
  size?: string;                         // 气泡大小字段
  color?: string;                        // 颜色映射字段

  // 图表配置
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;

  // 输出选项
  outputFormat?: "png" | "svg" | "html" | "json";
  outputPath?: string;                   // 保存路径
  width?: number;                        // 宽度 (px, 默认: 800)
  height?: number;                       // 高度 (px, 默认: 600)

  // 样式选项
  theme?: "default" | "dark" | "light" | "colorful";
  colorScheme?: string[];                // 自定义配色

  // 交互选项
  interactive?: boolean;                 // 是否交互式 (仅 HTML)
  showLegend?: boolean;                  // 显示图例 (默认: true)
  showGrid?: boolean;                    // 显示网格线 (默认: true)
  showTooltip?: boolean;                 // 显示提示框 (默认: true)
}
```

#### 输出端口 (Output Schema)

```typescript
{
  chartType: string;                     // 实际使用的图表类型
  filePath?: string;                     // 输出文件路径
  base64?: string;                       // Base64 编码 (用于嵌入)
  html?: string;                         // HTML 代码
  json?: object;                         // ECharts/Plotly 配置
  recommendation?: string;               // AI 推荐原因
  success: boolean;
  metadata: {
    width: number;
    height: number;
    format: string;
    fileSize?: string;
    dataPoints: number;                  // 数据点数量
  };
}
```

#### 使用示例

**自动模式 - AI 推荐图表类型**:

```json
// 输入
{
  "data": [
    {"month": "Jan", "sales": 12000, "profit": 3000},
    {"month": "Feb", "sales": 15000, "profit": 4500},
    {"month": "Mar", "sales": 13000, "profit": 3500}
  ],
  "chartType": "auto",
  "x": "month",
  "y": ["sales", "profit"],
  "title": "Monthly Performance"
}

// 输出
{
  "chartType": "line",
  "recommendation": "检测到时间序列数据,推荐使用折线图展示趋势",
  "filePath": "/charts/monthly_performance.png",
  "success": true,
  "metadata": {
    "width": 800,
    "height": 600,
    "format": "png",
    "fileSize": "125.6 KB",
    "dataPoints": 6
  }
}
```

**指定类型模式**:

```json
{
  "data": [...],
  "chartType": "bar",
  "x": "region",
  "y": "revenue",
  "title": "Revenue by Region",
  "outputFormat": "html",
  "interactive": true
}
```

#### 智能推荐逻辑

```typescript
// 图表类型自动推荐规则
function recommendChartType(data, x, y, series) {
  // 1. 时间序列数据 → 折线图
  if (isTimeSeries(data, x)) {
    return { type: "line", reason: "检测到时间序列数据" };
  }

  // 2. 分类 + 数值 → 柱状图
  if (isCategorical(data, x) && isNumerical(data, y)) {
    return { type: "bar", reason: "分类数据对比" };
  }

  // 3. 占比数据 (总和≈100%) → 饼图
  if (sumApproximately100(data, y)) {
    return { type: "pie", reason: "占比数据" };
  }

  // 4. 两个数值变量 → 散点图
  if (isNumerical(data, x) && isNumerical(data, y)) {
    return { type: "scatter", reason: "相关性分析" };
  }

  // 5. 矩阵数据 → 热力图
  if (isMatrixData(data)) {
    return { type: "heatmap", reason: "矩阵数据可视化" };
  }

  // 默认: 柱状图
  return { type: "bar", reason: "通用数据展示" };
}
```

---

### 2️⃣ `@oomol/chart-bar` - 柱状图/条形图

**功能描述**: 创建柱状图或条形图,用于分类数据对比

**适用场景**:
- 不同类别的数值对比
- 排行榜展示
- 分组对比

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;

  // 数据映射
  category: string;                      // 分类字段 (X轴)
  value: string | string[];              // 数值字段 (Y轴,支持多个)

  // 图表配置
  orientation?: "vertical" | "horizontal"; // 方向 (默认: vertical)
  stacked?: boolean;                     // 是否堆叠 (多系列时)
  grouped?: boolean;                     // 是否分组 (多系列时, 默认: true)

  // 排序
  sortBy?: "value" | "category" | "none"; // 排序依据 (默认: none)
  sortOrder?: "asc" | "desc";            // 排序顺序
  topN?: number;                         // 只显示前N个

  // 样式
  barWidth?: number;                     // 柱宽度百分比 (0-1, 默认: 0.6)
  showValues?: boolean;                  // 显示数值标签 (默认: false)
  colorBy?: string;                      // 按字段着色

  // 输出
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  outputFormat?: "png" | "svg" | "html";
  outputPath?: string;
  theme?: string;
  width?: number;
  height?: number;
}
```

#### 输出端口

```typescript
{
  filePath?: string;
  base64?: string;
  html?: string;
  success: boolean;
  metadata: {
    chartType: "bar" | "horizontal_bar";
    orientation: string;
    categories: number;
    series: number;
    dataPoints: number;
  };
}
```

#### 使用示例

**简单柱状图**:

```json
{
  "data": [
    {"product": "Laptop", "sales": 45000},
    {"product": "Phone", "sales": 78000},
    {"product": "Tablet", "sales": 32000}
  ],
  "category": "product",
  "value": "sales",
  "title": "Product Sales",
  "sortBy": "value",
  "sortOrder": "desc"
}
```

**分组柱状图**:

```json
{
  "data": [
    {"region": "North", "Q1": 12000, "Q2": 15000, "Q3": 13000},
    {"region": "South", "Q1": 10000, "Q2": 11000, "Q3": 14000}
  ],
  "category": "region",
  "value": ["Q1", "Q2", "Q3"],
  "grouped": true,
  "title": "Quarterly Sales by Region"
}
```

**堆叠柱状图**:

```json
{
  "data": [...],
  "category": "month",
  "value": ["product_a", "product_b", "product_c"],
  "stacked": true,
  "showValues": true
}
```

**Top N 排行榜**:

```json
{
  "data": [...],
  "category": "city",
  "value": "population",
  "sortBy": "value",
  "sortOrder": "desc",
  "topN": 10,
  "title": "Top 10 Cities by Population"
}
```

---

### 3️⃣ `@oomol/chart-line` - 折线图

**功能描述**: 创建折线图,展示数据趋势和变化

**适用场景**:
- 时间序列数据
- 趋势分析
- 多指标对比

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;

  // 数据映射
  x: string;                             // X轴字段 (通常是时间)
  y: string | string[];                  // Y轴字段 (支持多条线)

  // 图表配置
  smooth?: boolean;                      // 平滑曲线 (默认: false)
  showPoints?: boolean;                  // 显示数据点 (默认: true)
  fillArea?: boolean;                    // 填充面积 (变为面积图, 默认: false)

  // 标注
  showTrend?: boolean;                   // 显示趋势线 (默认: false)
  highlightPeaks?: boolean;              // 高亮峰值 (默认: false)
  annotations?: Array<{                  // 标注点
    x: any;
    y?: any;
    label: string;
    color?: string;
  }>;

  // 样式
  lineWidth?: number;                    // 线宽 (默认: 2)
  pointSize?: number;                    // 点大小 (默认: 4)
  dashPattern?: string;                  // 虚线模式 (如 "5,5")

  // 输出
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  outputFormat?: "png" | "svg" | "html";
  outputPath?: string;
  theme?: string;
  width?: number;
  height?: number;
}
```

#### 输出端口

```typescript
{
  filePath?: string;
  base64?: string;
  html?: string;
  success: boolean;
  metadata: {
    chartType: "line";
    series: number;
    dataPoints: number;
    timeRange?: {
      start: string;
      end: string;
    };
    trend?: {
      slope: number;
      direction: "up" | "down" | "flat";
    };
  };
}
```

#### 使用示例

**单线折线图**:

```json
{
  "data": [
    {"date": "2024-01", "revenue": 125000},
    {"date": "2024-02", "revenue": 135000},
    {"date": "2024-03", "revenue": 142000}
  ],
  "x": "date",
  "y": "revenue",
  "title": "Monthly Revenue Trend",
  "showTrend": true,
  "smooth": true
}
```

**多线对比**:

```json
{
  "data": [...],
  "x": "date",
  "y": ["revenue", "cost", "profit"],
  "title": "Financial Overview",
  "showPoints": true,
  "annotations": [
    {"x": "2024-03", "label": "Product Launch", "color": "#FF0000"}
  ]
}
```

**平滑曲线 + 峰值高亮**:

```json
{
  "data": [...],
  "x": "timestamp",
  "y": "cpu_usage",
  "smooth": true,
  "highlightPeaks": true,
  "title": "CPU Usage Over Time"
}
```

---

### 4️⃣ `@oomol/chart-pie` - 饼图/环形图

**功能描述**: 创建饼图或环形图,展示占比关系

**适用场景**:
- 部分与整体的关系
- 百分比分布
- 市场份额

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;

  // 数据映射
  category: string;                      // 分类字段
  value: string;                         // 数值字段

  // 图表配置
  chartType?: "pie" | "donut";           // 饼图或环形图 (默认: pie)
  innerRadius?: number;                  // 内半径 (环形图, 0-1, 默认: 0.5)

  // 显示选项
  showPercentage?: boolean;              // 显示百分比 (默认: true)
  showValues?: boolean;                  // 显示数值 (默认: false)
  showLabels?: boolean;                  // 显示标签 (默认: true)
  minSlicePercent?: number;              // 最小切片百分比 (小于则归入"其他", 默认: 1)

  // 交互
  explode?: string | string[];           // 突出显示的切片

  // 样式
  startAngle?: number;                   // 起始角度 (度, 默认: 0)
  colorScheme?: string[];

  // 输出
  title?: string;
  outputFormat?: "png" | "svg" | "html";
  outputPath?: string;
  theme?: string;
  width?: number;
  height?: number;
}
```

#### 输出端口

```typescript
{
  filePath?: string;
  base64?: string;
  html?: string;
  success: boolean;
  metadata: {
    chartType: "pie" | "donut";
    slices: number;
    total: number;
    largestSlice: {
      category: string;
      value: number;
      percentage: number;
    };
  };
}
```

#### 使用示例

**简单饼图**:

```json
{
  "data": [
    {"category": "Desktop", "value": 45},
    {"category": "Mobile", "value": 38},
    {"category": "Tablet", "value": 17}
  ],
  "category": "category",
  "value": "value",
  "title": "Traffic by Device",
  "showPercentage": true
}
```

**环形图**:

```json
{
  "data": [...],
  "category": "region",
  "value": "sales",
  "chartType": "donut",
  "innerRadius": 0.6,
  "explode": "North",
  "minSlicePercent": 5
}
```

**合并小切片**:

```json
{
  "data": [
    {"product": "A", "sales": 45},
    {"product": "B", "sales": 30},
    {"product": "C", "sales": 15},
    {"product": "D", "sales": 5},
    {"product": "E", "sales": 3},
    {"product": "F", "sales": 2}
  ],
  "category": "product",
  "value": "sales",
  "minSlicePercent": 5,  // D, E, F 会被合并为 "Others"
  "title": "Product Market Share"
}
```

---

### 5️⃣ `@oomol/chart-scatter` - 散点图/气泡图

**功能描述**: 创建散点图或气泡图,分析两个或三个变量的关系

**适用场景**:
- 相关性分析
- 聚类可视化
- 异常值检测

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;

  // 数据映射
  x: string;                             // X轴字段
  y: string;                             // Y轴字段
  size?: string;                         // 气泡大小字段 (可选)
  color?: string;                        // 颜色分组字段 (可选)
  label?: string;                        // 标签字段 (可选)

  // 图表配置
  showTrendLine?: boolean;               // 显示趋势线 (默认: false)
  trendLineType?: "linear" | "polynomial" | "exponential"; // 趋势线类型
  showCorrelation?: boolean;             // 显示相关系数 (默认: false)

  // 分组
  groupBy?: string;                      // 分组字段

  // 样式
  pointSize?: number;                    // 点大小 (默认: 8)
  pointOpacity?: number;                 // 透明度 (0-1, 默认: 0.7)
  sizeRange?: [number, number];          // 气泡大小范围 (默认: [5, 50])

  // 输出
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  outputFormat?: "png" | "svg" | "html";
  outputPath?: string;
  theme?: string;
  width?: number;
  height?: number;
}
```

#### 输出端口

```typescript
{
  filePath?: string;
  base64?: string;
  html?: string;
  success: boolean;
  metadata: {
    chartType: "scatter" | "bubble";
    dataPoints: number;
    groups?: number;
    correlation?: {
      coefficient: number;
      pValue: number;
      strength: "strong" | "moderate" | "weak" | "none";
    };
  };
}
```

#### 使用示例

**简单散点图**:

```json
{
  "data": [
    {"age": 25, "income": 45000},
    {"age": 32, "income": 58000},
    {"age": 45, "income": 72000}
  ],
  "x": "age",
  "y": "income",
  "title": "Age vs Income",
  "showTrendLine": true,
  "showCorrelation": true
}
```

**气泡图 (带大小和颜色)**:

```json
{
  "data": [...],
  "x": "marketing_spend",
  "y": "revenue",
  "size": "customer_count",
  "color": "region",
  "title": "Marketing ROI Analysis"
}
```

**分组散点图**:

```json
{
  "data": [...],
  "x": "feature1",
  "y": "feature2",
  "groupBy": "cluster",
  "title": "Customer Segmentation",
  "showTrendLine": false
}
```

---

## 第二层级: 高级图表 Blocks (P1)

> 支持专业分析场景的高级可视化

### 6️⃣ `@oomol/chart-heatmap` - 热力图

**功能描述**: 创建热力图,可视化矩阵数据

**适用场景**:
- 相关性矩阵
- 时间热图 (如一周各时段活跃度)
- 地理热力图

#### 输入端口

```typescript
{
  data: Array<Record<string, any>> | number[][];  // 表格数据或矩阵

  // 数据映射
  xAxis: string | string[];              // X轴类目
  yAxis: string | string[];              // Y轴类目
  value: string;                         // 数值字段

  // 样式
  colorScale?: "sequential" | "diverging" | "categorical";
  colorScheme?: string[];                // 颜色方案
  minColor?: string;                     // 最小值颜色 (默认: #F0F0F0)
  maxColor?: string;                     // 最大值颜色 (默认: #FF0000)
  midColor?: string;                     // 中间值颜色 (diverging 时)

  // 显示
  showValues?: boolean;                  // 显示数值 (默认: false)
  valueFormat?: string;                  // 数值格式 (如 ".2f")

  // 输出
  title?: string;
  outputFormat?: "png" | "svg" | "html";
  outputPath?: string;
  theme?: string;
  width?: number;
  height?: number;
}
```

#### 使用示例

**相关性热力图**:

```json
{
  "data": [
    {"var1": "age", "var2": "income", "correlation": 0.75},
    {"var1": "age", "var2": "education", "correlation": 0.42},
    {"var1": "income", "var2": "education", "correlation": 0.68}
  ],
  "xAxis": "var1",
  "yAxis": "var2",
  "value": "correlation",
  "title": "Correlation Matrix",
  "colorScale": "diverging",
  "showValues": true
}
```

**时间热图**:

```json
{
  "data": [...],
  "xAxis": "hour",
  "yAxis": "day_of_week",
  "value": "traffic",
  "title": "Website Traffic Heatmap"
}
```

---

### 7️⃣ `@oomol/chart-box` - 箱线图

**功能描述**: 创建箱线图,展示数据分布和异常值

**适用场景**:
- 数据分布分析
- 多组数据对比
- 异常值检测

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;

  // 数据映射
  category?: string;                     // 分组字段 (可选)
  value: string | string[];              // 数值字段

  // 配置
  orientation?: "vertical" | "horizontal"; // 方向 (默认: vertical)
  showOutliers?: boolean;                // 显示异常值 (默认: true)
  showMean?: boolean;                    // 显示均值点 (默认: false)
  showMedian?: boolean;                  // 显示中位数线 (默认: true)

  // 输出
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  outputFormat?: "png" | "svg" | "html";
  outputPath?: string;
  theme?: string;
  width?: number;
  height?: number;
}
```

---

### 8️⃣ `@oomol/chart-histogram` - 直方图

**功能描述**: 创建直方图,展示数据频率分布

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;

  // 数据映射
  value: string;                         // 数值字段

  // 配置
  bins?: number | "auto";                // 区间数量 (默认: auto)
  binWidth?: number;                     // 区间宽度
  cumulative?: boolean;                  // 累积直方图 (默认: false)
  normalized?: boolean;                  // 归一化 (默认: false)

  // 叠加
  showKDE?: boolean;                     // 显示核密度估计曲线 (默认: false)
  showNormal?: boolean;                  // 显示正态分布拟合 (默认: false)

  // 输出
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  outputFormat?: "png" | "svg" | "html";
  outputPath?: string;
  theme?: string;
  width?: number;
  height?: number;
}
```

---

### 9️⃣ `@oomol/chart-area` - 面积图

**功能描述**: 创建面积图,展示累积趋势

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;

  // 数据映射
  x: string;
  y: string | string[];

  // 配置
  stacked?: boolean;                     // 堆叠面积图 (默认: false)
  normalized?: boolean;                  // 百分比堆叠 (默认: false)
  smooth?: boolean;                      // 平滑曲线 (默认: false)
  opacity?: number;                      // 填充透明度 (0-1, 默认: 0.6)

  // 输出
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  outputFormat?: "png" | "svg" | "html";
  outputPath?: string;
  theme?: string;
  width?: number;
  height?: number;
}
```

---

### 🔟 `@oomol/chart-combo` - 组合图表

**功能描述**: 创建组合图表 (如柱状图 + 折线图)

**适用场景**:
- 多指标不同量级展示
- 柱状图 + 折线图组合

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;

  // 数据映射
  x: string;
  series: Array<{
    field: string;
    chartType: "bar" | "line" | "area";
    yAxis?: "left" | "right";           // 使用左轴或右轴
    label?: string;
    color?: string;
  }>;

  // 配置
  dualAxis?: boolean;                    // 双Y轴 (默认: false)

  // 输出
  title?: string;
  leftAxisLabel?: string;
  rightAxisLabel?: string;
  outputFormat?: "png" | "svg" | "html";
  outputPath?: string;
  theme?: string;
  width?: number;
  height?: number;
}
```

#### 使用示例

```json
{
  "data": [
    {"month": "Jan", "sales": 120000, "growth_rate": 0.15},
    {"month": "Feb", "sales": 135000, "growth_rate": 0.12}
  ],
  "x": "month",
  "series": [
    {
      "field": "sales",
      "chartType": "bar",
      "yAxis": "left",
      "label": "Sales Amount"
    },
    {
      "field": "growth_rate",
      "chartType": "line",
      "yAxis": "right",
      "label": "Growth Rate"
    }
  ],
  "dualAxis": true,
  "title": "Sales & Growth Rate"
}
```

---

## 第三层级: 专业图表 Blocks (P2)

> 专业分析场景的高级图表

### 1️⃣1️⃣ `@oomol/chart-waterfall` - 瀑布图

**功能描述**: 创建瀑布图,展示累积变化过程

**适用场景**:
- 收入/成本分解
- 财务报表
- 变化分析

---

### 1️⃣2️⃣ `@oomol/chart-radar` - 雷达图

**功能描述**: 创建雷达图,多维度对比

**适用场景**:
- 能力评估
- 多维度对比

---

### 1️⃣3️⃣ `@oomol/chart-treemap` - 树状图

**功能描述**: 创建树状图,展示层级结构和占比

**适用场景**:
- 文件大小分布
- 预算分配
- 层级占比

---

### 1️⃣4️⃣ `@oomol/chart-sankey` - 桑基图

**功能描述**: 创建桑基图,展示流向关系

**适用场景**:
- 用户流失漏斗
- 能量流动
- 资金流向

---

### 1️⃣5️⃣ `@oomol/chart-gauge` - 仪表盘

**功能描述**: 创建仪表盘,展示单一指标

**适用场景**:
- KPI 监控
- 进度展示
- 完成度

---

## 与表格 Blocks 集成

### 完整数据分析 + 可视化工作流

```typescript
// 1. 读取数据
const data = await oomol.execute("@oomol/table-reader", {
  filePath: "/data/sales_2024.xlsx",
  sheetName: "Q1"
});

// 2. 数据清洗
const cleaned = await oomol.execute("@oomol/table-cleaner", {
  data: data.data,
  operations: [
    { type: "dropNull", columns: ["customer_id", "amount"] },
    { type: "dropDuplicates" }
  ]
});

// 3. 数据聚合
const aggregated = await oomol.execute("@oomol/table-aggregator", {
  data: cleaned.data,
  mode: "groupBy",
  groupBy: ["region"],
  aggregations: [
    { column: "sales", function: "sum", alias: "total_sales" }
  ]
});

// 4. 生成图表
const chart = await oomol.execute("@oomol/chart-bar", {
  data: aggregated.data,
  category: "region",
  value: "total_sales",
  title: "Sales by Region",
  outputPath: "/charts/sales_by_region.png",
  sortBy: "value",
  sortOrder: "desc"
});

console.log(`图表已生成: ${chart.filePath}`);
```

### 常见组合场景

| 场景 | 表格 Blocks | 图表 Block | 输出 |
|------|------------|-----------|------|
| **销售趋势分析** | table-reader → table-filter | chart-line | 折线图 |
| **区域对比** | table-reader → table-aggregator | chart-bar | 柱状图 |
| **市场份额** | table-reader → table-aggregator | chart-pie | 饼图 |
| **相关性分析** | table-reader → table-analyzer | chart-heatmap | 热力图 |
| **异常值检测** | table-reader → table-analyzer | chart-scatter | 散点图 |
| **时间序列** | table-reader → table-time-series | chart-line | 折线图 |
| **分布分析** | table-reader | chart-histogram | 直方图 |

---

## 实施优先级建议

### 📅 实施路线图

#### **阶段 1: MVP (2-3 周)**

实施 **前 5 个核心 Blocks**:

1. ✅ `chart-generator` (智能生成器)
2. ✅ `chart-bar` (柱状图)
3. ✅ `chart-line` (折线图)
4. ✅ `chart-pie` (饼图)
5. ✅ `chart-scatter` (散点图)

**工作量**: 148 小时 (2人 × 3周)

**验收标准**:
- 支持 PNG/SVG/HTML 输出
- 自动推荐图表类型
- 与表格 Blocks 无缝集成
- 支持基本样式配置

**覆盖场景**: 85% 的日常图表需求

---

#### **阶段 2: 完善功能 (2-3 周)**

实施 **P1 高级 Blocks**:

6. ✅ `chart-heatmap` (热力图)
7. ✅ `chart-box` (箱线图)
8. ✅ `chart-histogram` (直方图)
9. ✅ `chart-area` (面积图)
10. ✅ `chart-combo` (组合图)

**工作量**: 140 小时 (2人 × 3周)

**覆盖场景**: 95% 的专业分析需求

---

#### **阶段 3: 专业扩展 (按需)**

实施 **P2 专业 Blocks**:

11. ⏸️ `chart-waterfall`
12. ⏸️ `chart-radar`
13. ⏸️ `chart-treemap`
14. ⏸️ `chart-sankey`
15. ⏸️ `chart-gauge`

**工作量**: 140 小时

---

## 技术栈建议

### 方案 A: **Python + Matplotlib/Plotly** (推荐 - 与表格 Blocks 无缝集成)

#### 核心依赖

```python
# 绘图核心
matplotlib>=3.7.0       # 静态图表
seaborn>=0.12.0         # 统计图表
plotly>=5.14.0          # 交互式图表

# 图像处理
pillow>=10.0.0          # 图像处理
kaleido>=0.2.0          # Plotly 静态图导出

# 数据处理 (与 table-blocks 共享)
pandas>=2.0.0
numpy>=1.24.0
```

#### 优势
- ✅ 与表格 Blocks (pandas-based) 完美集成
- ✅ 静态图表质量高
- ✅ 导出格式丰富
- ✅ 数据科学生态成熟

---

### 方案 B: **JavaScript + ECharts/D3**

#### 核心依赖

```json
{
  "echarts": "^5.4.0",         // 功能强大的图表库
  "d3": "^7.8.0",              // 底层绘图库
  "canvas": "^2.11.0",         // Node.js Canvas
  "puppeteer": "^21.0.0"       // 图表转图片
}
```

#### 优势
- ✅ 交互性强
- ✅ Web 友好
- ✅ 跨平台

---

### 方案 C: **混合方案** (最灵活)

- **Python** 生成静态图表 (PNG/SVG) - 高质量
- **JavaScript** 生成交互式图表 (HTML) - 交互性强
- Agent 根据需求自动选择

---

## 与 OOMOL Agent 集成

### 1️⃣ 在 Chatbox 中注册图表工具

在 `packages/chatbox/src/tools/chart-tools.ts` 中:

```typescript
import { Tools, CallLimit } from "@oomol/agent-core-ng";
import { z } from "zod";

export function bindChartTools(
  tools: Tools,
  oomolExecutor: OomolExecutor
): void {

  // 注册 chart-generator
  tools.make("chart_generate", {
    description: "智能生成图表,自动推荐最合适的图表类型。支持柱状图、折线图、饼图、散点图等。",
    callLimit: CallLimit.None,
    inputSchema: z.object({
      data: z.array(z.record(z.any())).describe("表格数据"),
      chartType: z.enum(["auto", "bar", "line", "pie", "scatter"]).optional(),
      x: z.union([z.string(), z.array(z.string())]).optional(),
      y: z.union([z.string(), z.array(z.string())]).optional(),
      title: z.string().optional(),
      outputFormat: z.enum(["png", "svg", "html"]).optional(),
      interactive: z.boolean().optional(),
    }),
    invoke: async ({ arguments: args }) => {
      const result = await oomolExecutor.execute("@oomol/chart-generator", args);
      return {
        content: [
          { type: "text", text: `已生成 ${result.chartType} 图表` },
          result.recommendation && { type: "text", text: `推荐原因: ${result.recommendation}` },
          result.base64 && { type: "image", source: { type: "base64", data: result.base64 } }
        ].filter(Boolean)
      };
    }
  });

  // 注册 chart-bar
  tools.make("chart_bar", {
    description: "创建柱状图或条形图,用于分类数据对比。支持分组、堆叠、排序等。",
    callLimit: CallLimit.None,
    inputSchema: z.object({
      data: z.array(z.record(z.any())),
      category: z.string(),
      value: z.union([z.string(), z.array(z.string())]),
      orientation: z.enum(["vertical", "horizontal"]).optional(),
      stacked: z.boolean().optional(),
      sortBy: z.enum(["value", "category", "none"]).optional(),
      sortOrder: z.enum(["asc", "desc"]).optional(),
      topN: z.number().optional(),
      title: z.string().optional(),
      outputFormat: z.enum(["png", "svg", "html"]).optional(),
    }),
    invoke: async ({ arguments: args }) => {
      const result = await oomolExecutor.execute("@oomol/chart-bar", args);
      return {
        content: [
          { type: "text", text: `已生成柱状图` },
          result.base64 && { type: "image", source: { type: "base64", data: result.base64 } }
        ].filter(Boolean)
      };
    }
  });

  // 注册其他图表工具...
}
```

---

### 2️⃣ 添加图表处理 Prompts

在 `packages/chatbox/prompts/fragments/chart-handling.njk` 中:

```njk
# 数据可视化专家能力

你特别擅长将数据转换为直观的图表。当用户需要可视化数据时:

## 图表类型自动推荐

根据数据特征自动推荐最合适的图表:

1. **时间序列数据** → 折线图 (`chart_line`)
   - 数据: 日期/时间 + 数值
   - 示例: 月度销售趋势、用户增长曲线

2. **分类对比** → 柱状图 (`chart_bar`)
   - 数据: 分类 + 数值
   - 示例: 各地区销售额、产品销量排名

3. **占比分析** → 饼图 (`chart_pie`)
   - 数据: 分类 + 占比
   - 示例: 市场份额、流量来源分布

4. **相关性分析** → 散点图 (`chart_scatter`)
   - 数据: 数值 + 数值
   - 示例: 价格与销量关系、年龄与收入关系

5. **分布分析** → 直方图 (`chart_histogram`)
   - 数据: 连续数值
   - 示例: 年龄分布、成绩分布

6. **矩阵数据** → 热力图 (`chart_heatmap`)
   - 数据: 二维矩阵
   - 示例: 相关性矩阵、时段活跃度

## 标准工作流

### 完整数据分析 + 可视化流程

```
table_read → table_inspect → table_clean → table_aggregate → chart_generate
```

### 常见场景组合

**场景1: 销售趋势分析**
```
table_read → table_filter (时间范围) → chart_line
```

**场景2: 区域销售对比**
```
table_read → table_aggregate (按区域求和) → chart_bar (排序)
```

**场景3: 市场份额分析**
```
table_read → table_aggregate (按产品求和) → chart_pie
```

**场景4: 相关性分析**
```
table_read → table_analyzer (correlation) → chart_heatmap
```

## 图表优化建议

1. **数据量控制**:
   - 柱状图: 建议 ≤ 20 个分类
   - 折线图: 建议 ≤ 100 个数据点
   - 饼图: 建议 ≤ 8 个切片 (使用 minSlicePercent 合并小切片)
   - 散点图: 建议 ≤ 5000 个点

2. **聚合优先**:
   - 大数据集先用 table_aggregate 聚合
   - 使用 table_filter 筛选关键数据
   - 使用 table_sample 采样

3. **输出格式选择**:
   - 报告/文档 → PNG/SVG
   - 交互式展示 → HTML
   - 二次开发 → JSON

4. **美化建议**:
   - 添加清晰的标题
   - 标注 X/Y 轴
   - 使用合适的配色主题
   - 突出关键数据点

## 使用示例

### 示例1: 自动生成图表
用户: "帮我把这个销售数据可视化"
步骤:
1. 使用 chart_generate (chartType: "auto")
2. AI 自动推荐最合适的图表类型
3. 返回图表并说明推荐原因

### 示例2: 时间序列分析
用户: "展示最近6个月的用户增长趋势"
步骤:
1. table_filter (筛选最近6个月)
2. chart_line (x: date, y: user_count, showTrend: true)

### 示例3: Top 10 排行榜
用户: "显示销售额前10的城市"
步骤:
1. table_aggregate (按城市求和)
2. chart_bar (sortBy: "value", sortOrder: "desc", topN: 10)

## 错误处理

1. **数据点过多**: 提示用户聚合或采样
2. **缺失字段**: 明确告知缺少哪个必需字段
3. **数据类型不匹配**: 建议使用 table_transform 转换类型
```

---

## 设计亮点

### 1. **智能推荐系统**

`chart-generator` 会根据数据特征自动推荐图表:

- 检测时间序列 → 折线图
- 检测分类数据 → 柱状图
- 检测占比数据 → 饼图
- 检测数值关系 → 散点图

---

### 2. **声明式配置**

用户无需了解底层图表库,只需声明"想看什么":

```typescript
// ✅ 简洁的 Block 配置
{
  data: [...],
  category: "region",
  value: "sales",
  sortBy: "value",
  sortOrder: "desc",
  topN: 10
}
```

---

### 3. **与表格 Blocks 无缝集成**

```typescript
// 完整工作流
table_read
  → table_clean
  → table_aggregate
  → chart_bar
  → (生成图表)
```

---

### 4. **多格式输出**

同一图表可导出多种格式:

- **PNG**: 报告、文档
- **SVG**: 高质量矢量图
- **HTML**: 交互式 Web 页面
- **JSON**: 图表配置 (高级用户)
- **Base64**: 嵌入邮件/文档

---

### 5. **智能数据处理**

- 自动合并小切片 (饼图 minSlicePercent)
- 自动排序和 Top N 筛选
- 自动计算趋势线和相关系数
- 自动检测异常值

---

## 总结

这套图表 Block 方案的特点:

✅ **智能**: 自动推荐最合适的图表类型
✅ **简洁**: 声明式配置,无需了解底层库
✅ **灵活**: 支持静态/交互式,多种格式
✅ **集成**: 与表格 Blocks 无缝串联
✅ **渐进**: 从简单到专业,满足不同需求

**建议从 MVP 的 5 个核心 Block 开始实施,快速验证价值。**

---

## 下一步行动

- [ ] 评审本设计方案
- [ ] 确定技术栈 (Python vs JavaScript vs 混合)
- [ ] 实施 MVP (5 个核心图表 Blocks)
- [ ] 与表格 Blocks 集成测试
- [ ] 编写完整文档和示例
- [ ] 用户测试和反馈
- [ ] 迭代完善

---

**文档版本**: 1.0
**最后更新**: 2026-01-21
**作者**: OOMOL Agent Team
**配套文档**:
- [TABLE_BLOCKS_DESIGN.md](./TABLE_BLOCKS_DESIGN.md) - 表格处理 Blocks 设计
- [CHART_TOOLS_DESIGN.md](./CHART_TOOLS_DESIGN.md) - 图表工具设计参考
