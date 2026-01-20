# 📦 表格处理 Blocks 完整设计方案

> 为 OOMOL Agent 设计的 Excel/CSV 表格处理能力扩展方案

---

## 📋 目录

1. [方案概述](#方案概述)
2. [Block 清单总览](#block-清单总览)
3. [第一层级: 核心基础 Blocks (P0)](#第一层级-核心基础-blocks-p0)
4. [第二层级: 高级功能 Blocks (P1)](#第二层级-高级功能-blocks-p1)
5. [第三层级: 专家功能 Blocks (P2)](#第三层级-专家功能-blocks-p2)
6. [实施优先级建议](#实施优先级建议)
7. [技术栈建议](#技术栈建议)
8. [与 OOMOL Agent 集成](#与-oomol-agent-集成)
9. [设计亮点](#设计亮点)

---

## 方案概述

### 设计目标

让 OOMOL Agent 成为**表格处理专家**,能够智能处理 Excel、CSV 等表格文件,提供从数据读取、清洗、转换、分析到导出的完整工作流。

### 核心原则

- **管道式设计**: 所有 Block 可无缝串联组合
- **渐进式复杂度**: 从简单到专业,满足不同用户需求
- **类型安全**: 完整的输入输出类型定义
- **性能优化**: 支持大文件处理和流式操作

### 目标用户

| 用户类型 | 典型需求 | 使用 Blocks |
|---------|---------|------------|
| **数据分析师** | 数据清洗、统计分析、报表生成 | P0 + P1 全部 |
| **业务人员** | 简单筛选、查看、导出 | P0 前 4 个 |
| **开发工程师** | 数据验证、格式转换、ETL | P0 + table-validator/joiner |
| **数据科学家** | 时间序列、高级统计、采样 | P0 + P1 + P2 |

---

## Block 清单总览

| 优先级 | Block 名称 | 核心功能 | 开发难度 | 预估工时 | 使用频率 |
|--------|-----------|---------|----------|---------|---------|
| **P0** | `@oomol/table-reader` | 多格式读取 | ⭐⭐⭐ | 40h | ⭐⭐⭐⭐⭐ |
| **P0** | `@oomol/table-inspector` | 数据概览 | ⭐⭐ | 24h | ⭐⭐⭐⭐⭐ |
| **P0** | `@oomol/table-filter` | 筛选排序 | ⭐⭐ | 32h | ⭐⭐⭐⭐⭐ |
| **P0** | `@oomol/table-cleaner` | 数据清洗 | ⭐⭐⭐ | 48h | ⭐⭐⭐⭐ |
| **P0** | `@oomol/table-transformer` | 数据转换 | ⭐⭐⭐⭐ | 56h | ⭐⭐⭐⭐ |
| **P0** | `@oomol/table-aggregator` | 聚合分析 | ⭐⭐⭐⭐ | 64h | ⭐⭐⭐⭐ |
| **P0** | `@oomol/table-writer` | 文件写入 | ⭐⭐⭐ | 32h | ⭐⭐⭐⭐⭐ |
| **P1** | `@oomol/table-joiner` | 表格关联 | ⭐⭐⭐⭐ | 48h | ⭐⭐⭐ |
| **P1** | `@oomol/table-validator` | 数据验证 | ⭐⭐⭐ | 40h | ⭐⭐⭐ |
| **P1** | `@oomol/table-analyzer` | 统计分析 | ⭐⭐⭐⭐⭐ | 72h | ⭐⭐⭐ |
| **P1** | `@oomol/table-sampler` | 数据采样 | ⭐⭐ | 24h | ⭐⭐ |
| **P1** | `@oomol/table-splitter` | 表格拆分 | ⭐⭐ | 20h | ⭐⭐ |
| **P2** | `@oomol/table-time-series` | 时间序列 | ⭐⭐⭐⭐ | 64h | ⭐⭐ |
| **P2** | `@oomol/table-formula` | 公式计算 | ⭐⭐⭐⭐⭐ | 80h | ⭐⭐ |
| **P2** | `@oomol/table-format` | 格式美化 | ⭐⭐⭐ | 40h | ⭐⭐ |

**总工时**: ~684 小时 (约 **4-5 个月, 2 人团队**)

---

## 第一层级: 核心基础 Blocks (P0)

> 必须实现的基础能力,覆盖 80% 的日常使用场景

### 1️⃣ `@oomol/table-reader` - 表格读取器

**功能描述**: 读取各种格式的表格文件并返回结构化数据

**适用场景**:
- 读取 CSV/Excel 文件
- 自动检测文件格式
- 指定工作表和表头位置
- 大文件限制行数读取

#### 输入端口 (Input Schema)

```typescript
{
  filePath: string;                    // 文件路径 (必需)
  format?: "auto" | "csv" | "excel" | "tsv";  // 格式 (默认: auto)
  sheetName?: string;                  // Excel工作表名 (默认: 第一个)
  sheetIndex?: number;                 // 工作表索引 (从0开始)
  headerRow?: number;                  // 表头行号 (默认: 0)
  encoding?: string;                   // CSV编码 (默认: utf-8)
  skipRows?: number;                   // 跳过前N行
  maxRows?: number;                    // 最多读取N行 (大文件优化)
}
```

#### 输出端口 (Output Schema)

```typescript
{
  data: Array<Record<string, any>>;    // 数据行数组
  columns: string[];                   // 列名数组
  shape: {                             // 表格形状
    rows: number;
    cols: number;
  };
  metadata: {                          // 元数据
    fileName: string;
    format: string;
    sheetNames?: string[];             // Excel所有工作表名
    fileSize: number;
    encoding?: string;
  };
}
```

#### 使用示例

```json
// 输入
{
  "filePath": "/data/sales_2024.xlsx",
  "sheetName": "Q1",
  "maxRows": 10000
}

// 输出
{
  "data": [
    {"date": "2024-01-01", "amount": 1250.5, "region": "North"},
    {"date": "2024-01-02", "amount": 980.0, "region": "South"}
  ],
  "columns": ["date", "amount", "region"],
  "shape": {"rows": 2, "cols": 3},
  "metadata": {
    "fileName": "sales_2024.xlsx",
    "format": "excel",
    "sheetNames": ["Q1", "Q2", "Q3", "Q4"],
    "fileSize": 204800
  }
}
```

---

### 2️⃣ `@oomol/table-inspector` - 表格检视器

**功能描述**: 快速查看表格结构、统计信息和数据质量

**适用场景**:
- 了解数据概况
- 检查数据类型
- 发现数据质量问题
- 查看数据样本

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;    // 来自 table-reader
  inspectLevel?: "basic" | "detailed" | "quality";  // 检视深度 (默认: basic)
}
```

#### 输出端口

```typescript
{
  summary: {
    rowCount: number;
    columnCount: number;
    memoryUsage: string;               // "2.5 MB"
  };
  columns: Array<{
    name: string;
    type: "number" | "string" | "date" | "boolean" | "mixed";
    nullCount: number;
    uniqueCount: number;
    nullPercent: number;               // 缺失值百分比
    sampleValues: any[];               // 前5个值
    stats?: {                          // 数值列统计 (仅 detailed)
      min: number;
      max: number;
      mean: number;
      median: number;
      std: number;
    };
  }>;
  quality: {                           // 仅 quality 模式
    completeness: number;              // 完整度百分比
    duplicateRows: number;
    issues: string[];                  // 发现的问题
  };
  preview: Array<Record<string, any>>;  // 前10行预览
}
```

#### 使用示例

```json
// 输入
{
  "data": [...],
  "inspectLevel": "detailed"
}

// 输出
{
  "summary": {
    "rowCount": 1500,
    "columnCount": 8,
    "memoryUsage": "1.2 MB"
  },
  "columns": [
    {
      "name": "age",
      "type": "number",
      "nullCount": 15,
      "uniqueCount": 45,
      "nullPercent": 1.0,
      "sampleValues": [25, 32, 41, 28, 35],
      "stats": {
        "min": 18,
        "max": 65,
        "mean": 35.4,
        "median": 34.0,
        "std": 12.3
      }
    }
  ],
  "preview": [...]
}
```

---

### 3️⃣ `@oomol/table-filter` - 表格筛选器

**功能描述**: 根据条件筛选行和列,支持排序和分页

**适用场景**:
- 按条件筛选数据
- 选择特定列
- 排序数据
- 分页查询

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  conditions?: Array<{                 // 行筛选条件 (AND 逻辑)
    column: string;
    operator: "==" | "!=" | ">" | "<" | ">=" | "<=" |
              "contains" | "startsWith" | "endsWith" |
              "in" | "notIn" | "isNull" | "notNull" | "between";
    value: any | any[];                // 单值或数组
  }>;
  columns?: string[];                  // 选择特定列 (空则全部)
  limit?: number;                      // 限制返回行数
  offset?: number;                     // 跳过前N行
  sortBy?: Array<{                     // 排序规则
    column: string;
    order: "asc" | "desc";
  }>;
}
```

#### 输出端口

```typescript
{
  data: Array<Record<string, any>>;
  filteredCount: number;               // 筛选后行数
  totalCount: number;                  // 原始总行数
  columns: string[];                   // 输出列名
}
```

#### 使用示例

```json
// 输入
{
  "data": [...],
  "conditions": [
    {"column": "age", "operator": ">=", "value": 18},
    {"column": "region", "operator": "in", "value": ["North", "South"]}
  ],
  "columns": ["name", "age", "salary"],
  "sortBy": [{"column": "salary", "order": "desc"}],
  "limit": 100
}

// 输出
{
  "data": [...],
  "filteredCount": 85,
  "totalCount": 1500,
  "columns": ["name", "age", "salary"]
}
```

---

### 4️⃣ `@oomol/table-cleaner` - 数据清洗器

**功能描述**: 处理缺失值、去重、类型转换等常见清洗任务

**适用场景**:
- 删除或填充缺失值
- 去除重复行
- 数据类型转换
- 文本清理(去空格、大小写)
- 值替换

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  operations: Array<{
    type: "dropNull" | "fillNull" | "dropDuplicates" |
          "convertType" | "trim" | "replace" | "normalize";
    columns?: string[];                // 作用列 (空则全部)
    params?: {
      // fillNull 参数
      fillValue?: any;                 // 固定填充值
      method?: "mean" | "median" | "mode" | "forward" | "backward";

      // convertType 参数
      targetType?: "number" | "string" | "date" | "boolean";
      dateFormat?: string;             // 日期格式

      // replace 参数
      replaceMap?: Record<string, any>;  // 替换映射
      pattern?: string;                // 正则表达式
      replacement?: string;

      // normalize 参数
      method?: "minmax" | "zscore";    // 归一化方法
    };
  }>;
}
```

#### 输出端口

```typescript
{
  data: Array<Record<string, any>>;
  report: Array<{
    operation: string;
    affected: number;                  // 影响行数
    details: string;
  }>;
}
```

#### 使用示例

```json
// 输入
{
  "data": [...],
  "operations": [
    {
      "type": "dropNull",
      "columns": ["email", "phone"]
    },
    {
      "type": "fillNull",
      "columns": ["age"],
      "params": {"method": "mean"}
    },
    {
      "type": "dropDuplicates"
    },
    {
      "type": "trim",
      "columns": ["name", "address"]
    }
  ]
}

// 输出
{
  "data": [...],
  "report": [
    {"operation": "dropNull", "affected": 45, "details": "删除了45行含空值的数据"},
    {"operation": "fillNull", "affected": 120, "details": "使用均值 32.5 填充"},
    {"operation": "dropDuplicates", "affected": 18, "details": "删除了18个重复行"},
    {"operation": "trim", "affected": 1500, "details": "清理了2列的空白字符"}
  ]
}
```

---

### 5️⃣ `@oomol/table-transformer` - 数据转换器

**功能描述**: 添加计算列、数据变换、列重命名、列拆分合并

**适用场景**:
- 创建派生字段
- 列重命名
- 删除不需要的列
- 拆分/合并列
- 数据类型转换

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  operations: Array<{
    type: "addColumn" | "renameColumn" | "dropColumn" |
          "computeColumn" | "split" | "merge" | "cast";
    params: {
      // addColumn / computeColumn
      newColumn?: string;
      expression?: string;             // "{col1} + {col2}" 或 "UPPER({name})"
      defaultValue?: any;

      // renameColumn
      oldName?: string;
      newName?: string;
      renameMap?: Record<string, string>;  // 批量重命名

      // dropColumn
      columns?: string[];

      // split
      column?: string;
      delimiter?: string;
      newColumns?: string[];
      maxSplit?: number;

      // merge
      sourceColumns?: string[];
      targetColumn?: string;
      separator?: string;
      template?: string;               // "{col1} - {col2}"

      // cast
      column?: string;
      targetType?: string;
    };
  }>;
}
```

#### 输出端口

```typescript
{
  data: Array<Record<string, any>>;
  newColumns: string[];                // 新增的列名
  droppedColumns: string[];            // 删除的列名
  renamedColumns: Record<string, string>;  // 重命名映射
  report: string[];
}
```

#### 使用示例

```json
// 输入
{
  "data": [...],
  "operations": [
    {
      "type": "computeColumn",
      "params": {
        "newColumn": "total_price",
        "expression": "{quantity} * {unit_price}"
      }
    },
    {
      "type": "split",
      "params": {
        "column": "full_name",
        "delimiter": " ",
        "newColumns": ["first_name", "last_name"]
      }
    },
    {
      "type": "renameColumn",
      "params": {
        "renameMap": {
          "qty": "quantity",
          "price": "unit_price"
        }
      }
    }
  ]
}

// 输出
{
  "data": [...],
  "newColumns": ["total_price", "first_name", "last_name"],
  "droppedColumns": ["full_name"],
  "renamedColumns": {"qty": "quantity", "price": "unit_price"},
  "report": [
    "添加计算列 'total_price'",
    "拆分列 'full_name' 为 2 列",
    "重命名了 2 个列"
  ]
}
```

---

### 6️⃣ `@oomol/table-aggregator` - 数据聚合器

**功能描述**: 分组聚合、透视表、统计计算

**适用场景**:
- GROUP BY 聚合
- 透视表分析
- 多维度统计
- 交叉表生成

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  mode: "groupBy" | "pivot";

  // groupBy 模式参数
  groupBy?: string[];                  // 分组列
  aggregations?: Array<{
    column: string;
    function: "sum" | "avg" | "count" | "min" | "max" |
              "median" | "std" | "var" | "countUnique" |
              "first" | "last" | "list";
    alias?: string;                    // 结果列名
  }>;

  // pivot 模式参数
  pivot?: {
    index: string[];                   // 行索引
    columns: string;                   // 列转换
    values: string;                    // 值列
    aggFunc: string;                   // 聚合函数
    fillValue?: any;                   // 填充缺失值
  };
}
```

#### 输出端口

```typescript
{
  data: Array<Record<string, any>>;
  mode: "groupBy" | "pivot";
  shape: {
    rows: number;
    cols: number;
  };
  groupCount?: number;                 // 分组数量
  pivotColumns?: string[];             // 透视表生成的列
}
```

#### 使用示例

**GroupBy 模式**:
```json
// 输入
{
  "data": [...],
  "mode": "groupBy",
  "groupBy": ["region", "category"],
  "aggregations": [
    {"column": "sales", "function": "sum", "alias": "total_sales"},
    {"column": "quantity", "function": "avg", "alias": "avg_quantity"},
    {"column": "customer_id", "function": "countUnique", "alias": "customer_count"}
  ]
}

// 输出
{
  "data": [
    {"region": "North", "category": "Electronics", "total_sales": 45000, "avg_quantity": 12.5, "customer_count": 320},
    {"region": "South", "category": "Electronics", "total_sales": 38000, "avg_quantity": 10.2, "customer_count": 280}
  ],
  "mode": "groupBy",
  "shape": {"rows": 8, "cols": 5},
  "groupCount": 8
}
```

**Pivot 模式**:
```json
// 输入
{
  "data": [...],
  "mode": "pivot",
  "pivot": {
    "index": ["region"],
    "columns": "product",
    "values": "sales",
    "aggFunc": "sum",
    "fillValue": 0
  }
}

// 输出
{
  "data": [
    {"region": "North", "Laptop": 25000, "Phone": 15000, "Tablet": 5000},
    {"region": "South", "Laptop": 20000, "Phone": 12000, "Tablet": 6000}
  ],
  "mode": "pivot",
  "shape": {"rows": 4, "cols": 4},
  "pivotColumns": ["Laptop", "Phone", "Tablet"]
}
```

---

### 7️⃣ `@oomol/table-writer` - 表格写入器

**功能描述**: 将数据写入文件 (CSV/Excel/TSV)

**适用场景**:
- 导出处理结果
- 生成报表文件
- 追加数据到现有文件
- Excel 格式化导出

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  outputPath: string;                  // 输出文件路径
  format?: "csv" | "excel" | "tsv";    // 格式 (默认: 从扩展名推断)
  options?: {
    sheetName?: string;                // Excel工作表名 (默认: Sheet1)
    includeHeader?: boolean;           // 包含表头 (默认: true)
    encoding?: string;                 // CSV编码 (默认: utf-8)
    append?: boolean;                  // 追加模式 (默认: false)

    // Excel 格式化选项
    formatting?: {
      headerStyle?: {
        bold?: boolean;
        backgroundColor?: string;
        fontSize?: number;
      };
      columnWidths?: Record<string, number>;  // 列宽映射
      autoFilter?: boolean;            // 自动筛选
      freezePane?: {row: number, col: number};  // 冻结窗格
    };
  };
}
```

#### 输出端口

```typescript
{
  filePath: string;                    // 实际写入路径
  rowsWritten: number;
  columnsWritten: number;
  fileSize: string;                    // "1.5 MB"
  success: boolean;
  format: string;
}
```

#### 使用示例

```json
// 输入
{
  "data": [...],
  "outputPath": "/output/sales_report_2024.xlsx",
  "format": "excel",
  "options": {
    "sheetName": "Q1_Report",
    "formatting": {
      "headerStyle": {
        "bold": true,
        "backgroundColor": "#4472C4",
        "fontSize": 12
      },
      "columnWidths": {"date": 15, "amount": 12},
      "autoFilter": true,
      "freezePane": {"row": 1, "col": 0}
    }
  }
}

// 输出
{
  "filePath": "/output/sales_report_2024.xlsx",
  "rowsWritten": 1500,
  "columnsWritten": 8,
  "fileSize": "245.6 KB",
  "success": true,
  "format": "excel"
}
```

---

## 第二层级: 高级功能 Blocks (P1)

> 增强数据处理能力,支持专业分析场景

### 8️⃣ `@oomol/table-joiner` - 表格合并器

**功能描述**: 多表关联 (类似 SQL JOIN)

**适用场景**:
- 合并多个数据源
- 关联查找
- 数据补全

#### 输入端口

```typescript
{
  leftData: Array<Record<string, any>>;
  rightData: Array<Record<string, any>>;
  joinType: "inner" | "left" | "right" | "outer";
  leftKey: string | string[];          // 左表关联键
  rightKey: string | string[];         // 右表关联键
  suffixes?: [string, string];         // 重复列后缀 (默认: ["_x", "_y"])
  dropDuplicates?: boolean;            // 删除重复行 (默认: false)
}
```

#### 输出端口

```typescript
{
  data: Array<Record<string, any>>;
  matchedRows: number;                 // 成功匹配行数
  leftUnmatched: number;               // 左表未匹配行数
  rightUnmatched: number;              // 右表未匹配行数
  joinType: string;
  keyColumns: string[];
}
```

---

### 9️⃣ `@oomol/table-validator` - 数据验证器

**功能描述**: 根据规则验证数据质量

**适用场景**:
- 数据质量检查
- 业务规则验证
- 数据入库前校验

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  rules: Array<{
    column: string;
    type: "notNull" | "unique" | "range" | "pattern" |
          "enum" | "length" | "type" | "custom";
    params?: {
      min?: number;
      max?: number;
      regex?: string;
      allowedValues?: any[];
      minLength?: number;
      maxLength?: number;
      dataType?: string;
      customFunc?: string;             // JavaScript 表达式
    };
    severity?: "error" | "warning";    // 严重级别
    message?: string;                  // 自定义错误消息
  }>;
  stopOnError?: boolean;               // 遇到错误停止 (默认: false)
}
```

#### 输出端口

```typescript
{
  valid: boolean;
  errors: Array<{
    row: number;
    column: string;
    rule: string;
    value: any;
    message: string;
    severity: "error" | "warning";
  }>;
  summary: {
    totalRows: number;
    validRows: number;
    errorRows: number;
    warningRows: number;
    errorsByRule: Record<string, number>;
  };
}
```

---

### 🔟 `@oomol/table-analyzer` - 统计分析器

**功能描述**: 高级统计分析 (相关性、分布、趋势、异常值)

**适用场景**:
- 探索性数据分析
- 特征相关性分析
- 异常值检测
- 数据分布分析

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  analysisType: "correlation" | "distribution" |
                "outliers" | "trend" | "summary";
  columns?: string[];                  // 分析列 (空则所有数值列)
  params?: {
    // correlation 参数
    method?: "pearson" | "spearman" | "kendall";

    // outliers 参数
    method?: "iqr" | "zscore" | "isolation_forest";
    threshold?: number;

    // trend 参数
    timeColumn?: string;
    method?: "linear" | "polynomial" | "moving_average";
    window?: number;

    // distribution 参数
    bins?: number;
  };
}
```

#### 输出端口

```typescript
{
  analysisType: string;
  result: any;                         // 根据 analysisType 返回不同结构
  visualizationData?: {                // 可视化数据 (可选)
    type: "bar" | "line" | "scatter" | "heatmap" | "histogram";
    data: any;
    config: any;
  };
}
```

**结果结构示例**:

**Correlation 模式**:
```json
{
  "analysisType": "correlation",
  "result": {
    "correlationMatrix": {
      "age_income": 0.75,
      "age_education": 0.42,
      "income_education": 0.68
    },
    "strongCorrelations": [
      {"pair": ["age", "income"], "value": 0.75, "strength": "strong"}
    ]
  },
  "visualizationData": {
    "type": "heatmap",
    "data": [...]
  }
}
```

**Outliers 模式**:
```json
{
  "analysisType": "outliers",
  "result": {
    "outlierCount": 23,
    "outlierIndices": [45, 128, 567, ...],
    "outliersByColumn": {
      "salary": 12,
      "age": 8,
      "score": 3
    },
    "outliers": [
      {"row": 45, "column": "salary", "value": 500000, "reason": "zscore > 3.0"}
    ]
  }
}
```

---

### 1️⃣1️⃣ `@oomol/table-sampler` - 数据采样器

**功能描述**: 随机采样、分层采样、系统采样

**适用场景**:
- 大数据集采样
- 训练/测试集划分
- 数据预览

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  method: "random" | "stratified" | "systematic" | "head" | "tail";
  size: number | number;               // 采样数量或比例 (0-1)
  params?: {
    stratifyColumn?: string;           // 分层列
    seed?: number;                     // 随机种子 (可复现)
    replacement?: boolean;             // 有放回采样 (默认: false)
  };
}
```

#### 输出端口

```typescript
{
  sample: Array<Record<string, any>>;
  indices: number[];                   // 原始数据索引
  sampleSize: number;
  originalSize: number;
  method: string;
}
```

---

### 1️⃣2️⃣ `@oomol/table-splitter` - 表格拆分器

**功能描述**: 按条件或比例拆分表格

**适用场景**:
- 训练/验证/测试集划分
- 按类别拆分文件
- 分批处理

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  method: "ratio" | "condition" | "chunks" | "stratified";
  params: {
    // ratio 参数
    ratios?: number[];                 // [0.7, 0.2, 0.1]
    names?: string[];                  // ["train", "val", "test"]
    shuffle?: boolean;
    seed?: number;

    // condition 参数
    conditions?: Array<{
      name: string;
      expression: string;              // "{age} >= 18"
    }>;

    // chunks 参数
    chunkSize?: number;

    // stratified 参数
    stratifyColumn?: string;
  };
}
```

#### 输出端口

```typescript
{
  splits: Array<{
    name: string;
    data: Array<Record<string, any>>;
    size: number;
    percentage: number;
  }>;
  method: string;
}
```

---

## 第三层级: 专家功能 Blocks (P2)

> 为特定专业场景设计的高级功能

### 1️⃣3️⃣ `@oomol/table-time-series` - 时间序列处理器

**功能描述**: 时间序列特有操作 (重采样、滚动窗口、时间解析)

**适用场景**:
- 时间序列分析
- 时间重采样
- 滚动统计
- 时间特征提取

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  timeColumn: string;                  // 时间列
  operation: "resample" | "rolling" | "shift" |
             "diff" | "parseDate" | "extractFeatures";
  params: {
    // resample 参数
    freq?: string;                     // "1D", "1H", "1M", "1W"
    aggFunc?: string | Record<string, string>;

    // rolling 参数
    window?: number;                   // 窗口大小
    minPeriods?: number;
    center?: boolean;

    // shift 参数
    periods?: number;

    // parseDate 参数
    format?: string;                   // "%Y-%m-%d %H:%M:%S"

    // extractFeatures 参数
    features?: Array<"year" | "month" | "day" | "hour" |
                     "weekday" | "quarter" | "week">;
  };
}
```

#### 输出端口

```typescript
{
  data: Array<Record<string, any>>;
  operation: string;
  newColumns?: string[];               // 新增列 (如时间特征)
  timeRange?: {
    start: string;
    end: string;
    periods: number;
  };
}
```

---

### 1️⃣4️⃣ `@oomol/table-formula` - 公式计算器

**功能描述**: 支持类 Excel 公式计算

**适用场景**:
- 复杂业务规则计算
- 类 Excel 公式支持
- 跨列计算

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  formulas: Array<{
    column: string;                    // 新列名
    expression: string;                // 公式表达式
    type?: "formula" | "custom";       // 公式类型
  }>;
  functions?: {                        // 自定义函数
    [name: string]: string;            // JavaScript 函数代码
  };
}
```

**支持的公式函数**:
- 数学: `SUM`, `AVG`, `MAX`, `MIN`, `ROUND`, `ABS`, `SQRT`, `POWER`
- 逻辑: `IF`, `AND`, `OR`, `NOT`, `SWITCH`, `CASE`
- 文本: `CONCAT`, `UPPER`, `LOWER`, `TRIM`, `LEN`, `SUBSTRING`
- 日期: `DATE`, `YEAR`, `MONTH`, `DAY`, `NOW`, `DATEDIFF`
- 查找: `VLOOKUP`, `INDEX`, `MATCH`

#### 输入端口

```typescript
{
  data: Array<Record<string, any>>;
  formulas: Array<{
    column: string;
    expression: string;
  }>;
}
```

#### 输出端口

```typescript
{
  data: Array<Record<string, any>>;
  newColumns: string[];
  errors?: Array<{
    row: number;
    column: string;
    error: string;
  }>;
}
```

#### 使用示例

```json
// 输入
{
  "data": [...],
  "formulas": [
    {
      "column": "total",
      "expression": "SUM({price}, {tax})"
    },
    {
      "column": "discount",
      "expression": "IF({quantity} > 10, {price} * 0.9, {price})"
    },
    {
      "column": "full_name",
      "expression": "CONCAT({first_name}, ' ', {last_name})"
    }
  ]
}
```

---

### 1️⃣5️⃣ `@oomol/table-format` - 格式化美化器

**功能描述**: Excel 样式美化、条件格式

**适用场景**:
- Excel 报表美化
- 条件格式化
- 专业报表生成

#### 输入端口

```typescript
{
  filePath: string;                    // Excel 文件路径
  sheetName?: string;                  // 工作表名 (默认: 第一个)
  formatting: {
    // 表头样式
    headerStyle?: {
      bold?: boolean;
      italic?: boolean;
      fontSize?: number;
      fontColor?: string;
      backgroundColor?: string;
      alignment?: "left" | "center" | "right";
      borderStyle?: "thin" | "medium" | "thick";
    };

    // 列宽和行高
    columnWidths?: Record<string, number>;
    rowHeights?: Record<number, number>;
    autoFitColumns?: boolean;

    // 条件格式
    conditionalFormats?: Array<{
      range: string;                   // "A2:D100"
      rule: "cellValue" | "expression" | "colorScale" | "dataBar";
      condition?: string;              // "> 1000"
      style?: object;
      colors?: string[];               // 颜色范围
    }>;

    // 冻结窗格
    freeze?: {
      row: number;
      col: number;
    };

    // 数据验证
    dataValidation?: Array<{
      range: string;
      type: "list" | "whole" | "decimal" | "date";
      values?: any[];
      min?: number;
      max?: number;
    }>;
  };
}
```

#### 输出端口

```typescript
{
  filePath: string;
  success: boolean;
  appliedFormats: string[];            // 应用的格式类型
}
```

---

## 实施优先级建议

### 📅 实施路线图

#### **阶段 1: MVP 基础版 (2-3 周)**

**目标**: 完成"读取 → 查看 → 筛选 → 导出"的基本流程

**实施 Blocks**:
1. ✅ `table-reader` - 读取文件
2. ✅ `table-inspector` - 查看概况
3. ✅ `table-filter` - 筛选排序
4. ✅ `table-writer` - 写入文件

**工作量**: 128 小时 (2人 × 2周)

**验收标准**:
- 支持 CSV/Excel 读取
- 显示数据概览和统计
- 支持基本筛选和排序
- 导出为 CSV/Excel

**用户价值**: 解决 **60%** 的日常表格查看和简单处理需求

---

#### **阶段 2: 核心功能版 (4-5 周)**

**目标**: 支持完整的数据清洗和分析工作流

**实施 Blocks**:
5. ✅ `table-cleaner` - 数据清洗
6. ✅ `table-transformer` - 数据转换
7. ✅ `table-aggregator` - 聚合分析
8. ✅ `table-joiner` - 表格合并

**工作量**: 216 小时 (2人 × 4周)

**验收标准**:
- 缺失值处理、去重、类型转换
- 计算列、列拆分合并
- GROUP BY 和透视表
- 多表 JOIN 关联

**用户价值**: 解决 **85%** 的数据分析场景

---

#### **阶段 3: 增强功能版 (3-4 周)**

**目标**: 提供专业数据分析能力

**实施 Blocks**:
9. ✅ `table-validator` - 数据验证
10. ✅ `table-analyzer` - 统计分析
11. ✅ `table-sampler` - 数据采样
12. ✅ `table-splitter` - 表格拆分

**工作量**: 156 小时 (2人 × 3周)

**验收标准**:
- 数据质量规则验证
- 相关性分析、异常值检测
- 随机/分层采样
- 数据集划分

**用户价值**: 满足 **95%** 的专业数据分析需求

---

#### **阶段 4: 专家功能版 (按需开发)**

**目标**: 满足专家用户特殊需求

**实施 Blocks**:
13. ⏸️ `table-time-series` - 时间序列
14. ⏸️ `table-formula` - 公式计算
15. ⏸️ `table-format` - 格式美化

**工作量**: 184 小时 (按需投入)

**用户价值**: 覆盖 **100%** 场景,支持高级专业需求

---

### 📊 阶段对比

| 阶段 | 周期 | Block 数 | 工时 | 场景覆盖 | 用户类型 |
|------|------|---------|------|---------|---------|
| MVP | 2-3周 | 4 | 128h | 60% | 业务人员 |
| 核心 | 4-5周 | 4 | 216h | 85% | 数据分析师 |
| 增强 | 3-4周 | 4 | 156h | 95% | 专业分析师 |
| 专家 | 按需 | 3 | 184h | 100% | 数据科学家 |

---

### 🎯 快速启动建议

**如果资源有限,建议先实施前 4 个 Block**:

```
Week 1-2:
  ├─ table-reader (40h)
  ├─ table-inspector (24h)
  └─ table-filter (32h)

Week 3:
  └─ table-writer (32h)

✅ MVP 完成,可对外发布测试版
```

**优势**:
- ✅ 快速验证技术可行性
- ✅ 及早获取用户反馈
- ✅ 迭代式开发降低风险
- ✅ 投资回报比高

---

## 技术栈建议

### 🐍 **Python 方案** (推荐 - 数据处理生态成熟)

#### 核心依赖库

```python
# 数据处理核心
pandas>=2.0.0          # DataFrame 操作
numpy>=1.24.0          # 数值计算

# Excel/CSV 读写
openpyxl>=3.1.0        # Excel .xlsx 读写
xlrd>=2.0.0            # 老版本 .xls 读取
xlsxwriter>=3.0.0      # Excel 高性能写入
chardet>=5.0.0         # 编码自动检测

# 数据分析
scipy>=1.10.0          # 统计分析
scikit-learn>=1.2.0    # 机器学习 (异常值检测)
statsmodels>=0.14.0    # 时间序列分析

# 数据验证
cerberus>=1.3.0        # 数据验证框架
jsonschema>=4.17.0     # Schema 验证

# 工具库
python-dateutil>=2.8.0  # 日期解析
tqdm>=4.65.0           # 进度条
```

#### 项目结构示例

```
oomol-table-blocks/
├── table_reader/
│   ├── __init__.py
│   ├── reader.py
│   └── detectors.py
├── table_inspector/
│   ├── __init__.py
│   └── inspector.py
├── table_filter/
│   ├── __init__.py
│   └── filter.py
├── table_cleaner/
│   ├── __init__.py
│   └── cleaner.py
├── table_transformer/
│   ├── __init__.py
│   └── transformer.py
├── table_aggregator/
│   ├── __init__.py
│   └── aggregator.py
├── table_writer/
│   ├── __init__.py
│   └── writer.py
├── common/
│   ├── types.py        # 通用类型定义
│   ├── errors.py       # 异常类
│   └── utils.py        # 工具函数
├── tests/
└── requirements.txt
```

---

### 🟨 **JavaScript/TypeScript 方案** (前端友好)

#### 核心依赖库

```json
{
  "dependencies": {
    // Excel/CSV 处理
    "xlsx": "^0.18.5",              // SheetJS - Excel 处理
    "papaparse": "^5.4.1",          // CSV 解析
    "exceljs": "^4.3.0",            // Excel 高级操作

    // 数据处理
    "danfojs": "^1.1.2",            // DataFrame 库 (类 pandas)
    "lodash": "^4.17.21",           // 工具库
    "mathjs": "^11.11.0",           // 数学计算

    // 统计分析
    "simple-statistics": "^7.8.3",  // 统计函数
    "regression": "^2.0.1",         // 回归分析

    // 数据验证
    "ajv": "^8.12.0",               // JSON Schema 验证
    "validator": "^13.11.0",        // 字符串验证

    // 日期处理
    "date-fns": "^2.30.0",          // 日期工具

    // 类型
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  }
}
```

#### 优劣对比

| 维度 | Python | JavaScript/TypeScript |
|------|--------|----------------------|
| **数据处理生态** | ⭐⭐⭐⭐⭐ 成熟 | ⭐⭐⭐ 发展中 |
| **性能** | ⭐⭐⭐⭐ 优秀 | ⭐⭐⭐ 良好 |
| **学习曲线** | ⭐⭐⭐⭐ 平缓 | ⭐⭐⭐⭐⭐ 友好 |
| **社区支持** | ⭐⭐⭐⭐⭐ 强大 | ⭐⭐⭐ 中等 |
| **前端集成** | ⭐⭐ 需要桥接 | ⭐⭐⭐⭐⭐ 原生支持 |
| **统计分析** | ⭐⭐⭐⭐⭐ 完整 | ⭐⭐⭐ 基础 |
| **部署** | ⭐⭐⭐ 需要环境 | ⭐⭐⭐⭐ 跨平台 |

**推荐**: 如果主要做数据处理和分析,选择 **Python**;如果需要前端集成和跨平台,选择 **JavaScript/TypeScript**

---

### 🏗️ **架构设计建议**

#### 分层架构

```
┌─────────────────────────────────┐
│   OOMOL Agent Integration       │  ← Agent 工具注册层
├─────────────────────────────────┤
│   Block API Layer                │  ← 标准化 API 接口
├─────────────────────────────────┤
│   Core Processing Layer          │  ← 核心处理逻辑
├─────────────────────────────────┤
│   Library Wrappers               │  ← 第三方库封装
├─────────────────────────────────┤
│   Utils & Common                 │  ← 工具和公共模块
└─────────────────────────────────┘
```

#### 通用数据格式

所有 Block 使用统一的数据格式,便于串联:

```typescript
type TableData = Array<Record<string, any>>;

interface BlockInput {
  data: TableData;
  // ... 其他参数
}

interface BlockOutput {
  data: TableData;
  metadata?: Record<string, any>;
  // ... 其他信息
}
```

---

## 与 OOMOL Agent 集成

### 1️⃣ 在 Chatbox 中注册表格工具

在 [packages/chatbox/src/tools/table-tools.ts](packages/chatbox/src/tools/table-tools.ts) 中:

```typescript
import { Tools, CallLimit } from "@oomol/agent-core-ng";
import { z } from "zod";

export function bindTableTools(
  tools: Tools,
  oomolExecutor: OomolExecutor
): void {

  // 1. 注册 table-reader
  tools.make("table_read", {
    description: "读取 Excel/CSV 文件并返回结构化数据。支持多格式、多工作表、大文件限制。",
    callLimit: CallLimit.None,
    inputSchema: z.object({
      filePath: z.string().describe("文件路径"),
      format: z.enum(["auto", "csv", "excel", "tsv"]).optional().describe("文件格式"),
      sheetName: z.string().optional().describe("Excel工作表名"),
      maxRows: z.number().optional().describe("最多读取行数"),
    }),
    invoke: async ({ arguments: args }) => {
      const result = await oomolExecutor.execute("@oomol/table-reader", args);
      return {
        content: [
          {
            type: "text",
            text: `成功读取 ${result.shape.rows} 行 × ${result.shape.cols} 列数据`,
          },
          {
            type: "json",
            json: result,
          },
        ],
      };
    },
  });

  // 2. 注册 table-inspector
  tools.make("table_inspect", {
    description: "查看表格结构、数据类型、统计信息和数据质量。快速了解数据概况。",
    callLimit: CallLimit.TurnUnique,
    inputSchema: z.object({
      data: z.array(z.record(z.any())),
      inspectLevel: z.enum(["basic", "detailed", "quality"]).optional(),
    }),
    invoke: async ({ arguments: args }) => {
      const result = await oomolExecutor.execute("@oomol/table-inspector", args);
      return {
        content: [
          {
            type: "text",
            text: `数据概览: ${result.summary.rowCount} 行, ${result.summary.columnCount} 列`,
          },
          {
            type: "json",
            json: result,
          },
        ],
      };
    },
  });

  // 3. 注册 table-filter
  tools.make("table_filter", {
    description: "根据条件筛选行和列,支持排序和分页。用于数据查询和过滤。",
    callLimit: CallLimit.None,
    inputSchema: z.object({
      data: z.array(z.record(z.any())),
      conditions: z.array(z.object({
        column: z.string(),
        operator: z.enum(["==", "!=", ">", "<", ">=", "<=", "contains", "in", "isNull"]),
        value: z.any().optional(),
      })).optional(),
      columns: z.array(z.string()).optional(),
      sortBy: z.array(z.object({
        column: z.string(),
        order: z.enum(["asc", "desc"]),
      })).optional(),
      limit: z.number().optional(),
    }),
    invoke: async ({ arguments: args }) => {
      const result = await oomolExecutor.execute("@oomol/table-filter", args);
      return {
        content: [
          {
            type: "text",
            text: `筛选结果: ${result.filteredCount}/${result.totalCount} 行`,
          },
          {
            type: "json",
            json: result,
          },
        ],
      };
    },
  });

  // 4. 注册其他 Blocks...
  // table_clean, table_transform, table_aggregate, table_write, etc.
}
```

---

### 2️⃣ 在主入口注册工具

在 [packages/chatbox/src/session/session-tools.ts](packages/chatbox/src/session/session-tools.ts) 中:

```typescript
import { bindTableTools } from "../tools/table-tools.js";

export function createSessionTools(
  $: Agent$<ChatboxEventTemplate, ChatboxTurnData>,
  // ... 其他参数
): Tools {
  const tools = new Tools();

  // ... 现有工具绑定

  // 绑定表格处理工具
  bindTableTools(tools, oomolExecutor);

  return tools;
}
```

---

### 3️⃣ 添加表格处理 Prompts

在 [packages/chatbox/prompts/fragments/table-handling.njk](packages/chatbox/prompts/fragments/table-handling.njk) 中:

```njk
# 表格处理专家能力

你特别擅长处理 Excel、CSV 等表格文件。当用户需要处理表格时:

## 标准工作流

1. **读取阶段**: 使用 `table_read` 读取文件
   - 自动检测格式 (format: "auto")
   - 大文件使用 maxRows 限制
   - Excel 文件指定 sheetName

2. **查看阶段**: 使用 `table_inspect` 了解数据
   - 查看列类型和统计信息
   - 检查缺失值和数据质量
   - 预览前几行数据

3. **处理阶段**: 根据需求选择工具
   - 数据筛选 → `table_filter`
   - 数据清洗 → `table_clean` (去重、缺失值、类型转换)
   - 数据转换 → `table_transform` (计算列、列拆分合并)
   - 数据聚合 → `table_aggregate` (GROUP BY、透视表)
   - 表格合并 → `table_join`
   - 数据验证 → `table_validate`
   - 统计分析 → `table_analyze`

4. **输出阶段**: 使用 `table_write` 导出结果
   - 支持 CSV/Excel 格式
   - Excel 支持格式化 (表头样式、列宽、冻结窗格)

## 工具选择优先级

**简单查询**: table_read → table_filter → table_write

**数据清洗**: table_read → table_inspect → table_clean → table_write

**数据分析**: table_read → table_clean → table_aggregate → table_write

**复杂ETL**: table_read → table_clean → table_transform → table_join → table_aggregate → table_write

## 最佳实践

1. **始终先 inspect**: 了解数据结构后再处理
2. **管道式处理**: 一步步串联工具,不要跳步
3. **大文件优化**:
   - 使用 maxRows 限制读取
   - 使用 table_filter 的 limit 分页
4. **错误处理**: 检查每一步的返回结果,发现问题及时调整
5. **数据保留**: 重要的中间结果用 table_write 保存

## 常见场景示例

### 场景1: 去重并导出
```
table_read → table_clean (dropDuplicates) → table_write
```

### 场景2: 筛选符合条件的数据
```
table_read → table_filter (conditions) → table_write
```

### 场景3: 销售数据分析
```
table_read → table_aggregate (groupBy: region, sum: sales) → table_write
```

### 场景4: 多表关联
```
table_read (左表) → table_read (右表) → table_join → table_write
```
```

在 [packages/chatbox/prompts/tool-usage.njk](packages/chatbox/prompts/tool-usage.njk) 中引入:

```njk
{% include "fragments/table-handling.njk" %}
```

---

### 4️⃣ 创建表格处理技能

在 [packages/chatbox/src/tools/skill-bridge.ts](packages/chatbox/src/tools/skill-bridge.ts) 中注册技能:

```typescript
export function registerTableSkills(skillRegistry: SkillRegistry): void {

  // 注册表格专家技能
  skillRegistry.registerSpecialist(
    "table-expert",
    "专门处理 Excel、CSV 等表格文件的数据分析和操作专家",
    "table-handling"  // 指向 prompts/fragments/table-handling.njk
  );

  // 注册具体场景技能
  skillRegistry.registerSpecialist(
    "table-cleaner-expert",
    "数据清洗专家,处理缺失值、去重、类型转换等数据质量问题",
    "table-cleaning"
  );

  skillRegistry.registerSpecialist(
    "table-analyst-expert",
    "数据分析专家,进行统计分析、相关性分析、异常值检测",
    "table-analysis"
  );
}
```

---

### 5️⃣ 在 Agent 中自动检测表格文件

在 [packages/chatbox/src/session/session.ts](packages/chatbox/src/session/session.ts) 中添加文件类型检测:

```typescript
function detectTableFiles(attachments: Attachment[]): boolean {
  const tableExtensions = ['.csv', '.xlsx', '.xls', '.tsv', '.ods'];
  return attachments.some(att =>
    tableExtensions.some(ext => att.name.toLowerCase().endsWith(ext))
  );
}

// 在 Agent 输入处理中
if (detectTableFiles(input.attachments)) {
  // 自动激活表格处理技能
  eventHandlers.set("activeSkill", "table-expert");
}
```

---

## 设计亮点

### 1. **管道式设计 (Pipeline Architecture)**

所有 Block 的输入/输出都是标准的 `Array<Record<string, any>>` 格式,可以无缝串联:

```typescript
// 完整的 ETL 流程
const result = await pipeline([
  { block: "table-reader", params: { filePath: "data.xlsx" } },
  { block: "table-inspector", params: { inspectLevel: "quality" } },
  { block: "table-cleaner", params: { operations: [...] } },
  { block: "table-filter", params: { conditions: [...] } },
  { block: "table-aggregator", params: { groupBy: [...] } },
  { block: "table-writer", params: { outputPath: "result.csv" } },
]);
```

**优势**:
- ✅ 灵活组合,满足各种场景
- ✅ 易于测试和调试
- ✅ 符合函数式编程思想

---

### 2. **渐进式复杂度 (Progressive Complexity)**

| 用户层级 | 使用 Blocks | 复杂度 |
|---------|------------|-------|
| **入门** | reader + inspector + writer | ⭐ |
| **进阶** | + filter + cleaner | ⭐⭐ |
| **专业** | + transformer + aggregator + joiner | ⭐⭐⭐ |
| **专家** | + validator + analyzer + time-series + formula | ⭐⭐⭐⭐⭐ |

**用户可以按需学习,不会被复杂功能淹没**

---

### 3. **灵活的参数设计 (Flexible Parameters)**

每个 Block 都支持:
- **简单模式**: 只传必需参数,其他使用默认值
- **高级模式**: 完全控制每个细节

```typescript
// 简单模式 - 使用默认值
{
  "filePath": "data.csv"
}

// 高级模式 - 完全控制
{
  "filePath": "data.csv",
  "format": "csv",
  "encoding": "utf-8",
  "headerRow": 1,
  "skipRows": 2,
  "maxRows": 10000
}
```

---

### 4. **详细的操作报告 (Detailed Reports)**

每个 Block 都返回详细的执行报告:

```typescript
{
  "data": [...],
  "report": [
    {"operation": "dropNull", "affected": 45, "details": "删除了45行含空值的数据"},
    {"operation": "fillNull", "affected": 120, "details": "使用均值 32.5 填充"},
    {"operation": "dropDuplicates", "affected": 18, "details": "删除了18个重复行"}
  ]
}
```

**优势**:
- ✅ 用户清楚知道发生了什么
- ✅ 便于调试和审计
- ✅ 提升用户信任度

---

### 5. **性能优化考虑 (Performance Optimizations)**

- **流式处理**: 支持大文件分批读取
- **惰性加载**: 只读取需要的列和行
- **索引优化**: 关键操作使用索引加速
- **内存管理**: 及时释放不再需要的数据

```typescript
// 大文件处理示例
{
  "filePath": "huge_data.csv",
  "maxRows": 10000,        // 只读前1万行
  "columns": ["id", "amount"]  // 只读2列
}
```

---

### 6. **错误处理友好 (Error Handling)**

- **参数验证**: 使用 Zod Schema 严格验证输入
- **清晰的错误信息**: 告诉用户哪里出错了
- **部分失败处理**: 尽量返回部分结果,而不是全部失败

```typescript
// 错误信息示例
{
  "success": false,
  "error": {
    "code": "COLUMN_NOT_FOUND",
    "message": "列 'age' 不存在于数据中",
    "availableColumns": ["name", "email", "salary"]
  }
}
```

---

### 7. **可视化数据支持 (Visualization Ready)**

高级分析 Block (如 `table-analyzer`) 返回可视化数据:

```typescript
{
  "result": {...},
  "visualizationData": {
    "type": "heatmap",
    "data": [...],
    "config": {
      "title": "Correlation Matrix",
      "xAxis": [...],
      "yAxis": [...]
    }
  }
}
```

可以直接对接图表库 (如 ECharts、Plotly)

---

## 附录: 完整工作流示例

### 示例 1: 销售数据清洗和分析

```typescript
// 步骤 1: 读取数据
const rawData = await table_read({
  filePath: "/data/sales_2024.xlsx",
  sheetName: "Q1"
});

// 步骤 2: 查看概况
const inspection = await table_inspect({
  data: rawData.data,
  inspectLevel: "quality"
});

// 步骤 3: 数据清洗
const cleanedData = await table_clean({
  data: rawData.data,
  operations: [
    { type: "dropNull", columns: ["customer_id", "amount"] },
    { type: "fillNull", columns: ["region"], params: { fillValue: "Unknown" } },
    { type: "dropDuplicates" },
    { type: "convertType", columns: ["date"], params: { targetType: "date" } }
  ]
});

// 步骤 4: 计算派生字段
const transformedData = await table_transform({
  data: cleanedData.data,
  operations: [
    {
      type: "computeColumn",
      params: {
        newColumn: "total_revenue",
        expression: "{quantity} * {unit_price}"
      }
    }
  ]
});

// 步骤 5: 按区域聚合
const aggregatedData = await table_aggregate({
  data: transformedData.data,
  mode: "groupBy",
  groupBy: ["region"],
  aggregations: [
    { column: "total_revenue", function: "sum", alias: "revenue" },
    { column: "customer_id", function: "countUnique", alias: "customers" },
    { column: "quantity", function: "avg", alias: "avg_quantity" }
  ]
});

// 步骤 6: 导出结果
const output = await table_write({
  data: aggregatedData.data,
  outputPath: "/output/sales_report_Q1.xlsx",
  options: {
    sheetName: "Regional_Summary",
    formatting: {
      headerStyle: { bold: true, backgroundColor: "#4472C4" },
      autoFilter: true,
      freezePane: { row: 1, col: 0 }
    }
  }
});
```

---

### 示例 2: 用户行为数据分层采样

```typescript
// 读取大文件 (限制100万行)
const userData = await table_read({
  filePath: "/data/user_behavior.csv",
  maxRows: 1000000
});

// 按用户等级分层采样
const sampledData = await table_sample({
  data: userData.data,
  method: "stratified",
  size: 0.1,  // 10%
  params: {
    stratifyColumn: "user_level",
    seed: 42
  }
});

// 拆分为训练/验证/测试集
const splits = await table_split({
  data: sampledData.sample,
  method: "ratio",
  params: {
    ratios: [0.7, 0.2, 0.1],
    names: ["train", "val", "test"],
    shuffle: true,
    seed: 42
  }
});

// 分别导出
for (const split of splits.splits) {
  await table_write({
    data: split.data,
    outputPath: `/output/${split.name}.csv`
  });
}
```

---

### 示例 3: 多表关联和数据验证

```typescript
// 读取订单表和用户表
const orders = await table_read({ filePath: "/data/orders.csv" });
const users = await table_read({ filePath: "/data/users.csv" });

// LEFT JOIN 关联
const joinedData = await table_join({
  leftData: orders.data,
  rightData: users.data,
  joinType: "left",
  leftKey: "user_id",
  rightKey: "id"
});

// 数据验证
const validation = await table_validate({
  data: joinedData.data,
  rules: [
    { column: "email", type: "pattern", params: { regex: "^[^@]+@[^@]+\\.[^@]+$" } },
    { column: "age", type: "range", params: { min: 18, max: 120 } },
    { column: "amount", type: "notNull" }
  ]
});

if (!validation.valid) {
  console.log(`发现 ${validation.errors.length} 个数据问题`);
  // 处理错误...
}
```

---

## 总结

这套表格处理 Block 方案具有以下特点:

✅ **完整**: 覆盖从读取到分析到导出的完整流程
✅ **模块化**: 每个 Block 职责单一,易于维护
✅ **可扩展**: 管道式设计,灵活组合
✅ **易用**: 渐进式复杂度,适合不同用户
✅ **实用**: 基于真实需求设计,解决实际问题
✅ **高质量**: 完整的类型定义、错误处理和文档

**建议从 MVP (前 4 个 Block) 开始实施,快速验证价值,然后逐步扩展功能。**

---

## 下一步行动

1. [ ] 评审本设计方案
2. [ ] 确定技术栈 (Python vs JavaScript)
3. [ ] 搭建项目骨架
4. [ ] 实施 MVP (table-reader, inspector, filter, writer)
5. [ ] 编写测试用例
6. [ ] 集成到 OOMOL Agent
7. [ ] 用户测试和反馈
8. [ ] 迭代完善

---

**文档版本**: 1.0
**最后更新**: 2024-01-20
**作者**: OOMOL Agent Team
