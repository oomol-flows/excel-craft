# Table Blocks Quick Reference Guide

## All Available Blocks (P0 + P1 + P2)

### 📥 Data Input/Output (P0)

1. **table-reader** - Read Excel/CSV files
2. **table-writer** - Write Excel/CSV files
3. **table-inspector** - View data structure and statistics

### 🧹 Data Cleaning & Transformation (P0)

4. **table-cleaner** - Handle nulls, duplicates, type conversion
5. **table-filter** - Filter rows, select columns, sort
6. **table-transformer** - Add columns, rename, split/merge

### 📊 Data Analysis (P0 + P1)

7. **table-aggregator** - GROUP BY and pivot tables
8. **table-joiner** - JOIN multiple tables
9. **table-analyzer** - Statistical analysis, correlation, outliers
10. **table-validator** - Data quality validation

### 🔬 Advanced Features (P1 + P2)

11. **table-sampler** - Random/stratified sampling
12. **table-splitter** - Split data into train/val/test sets
13. **table-time-series** ⭐ NEW - Time series operations
14. **table-formula** ⭐ NEW - Excel-like formulas
15. **table-format** ⭐ NEW - Excel beautification

---

## P2 Blocks Quick Usage

### ⏰ table-time-series

Extract year, month, weekday from dates:
```yaml
operation: "extractFeatures"
params:
  features: ["year", "month", "weekday", "quarter"]
```

Rolling 7-day average:
```yaml
operation: "rolling"
params:
  window: 7
  aggFunc: "mean"
```

Resample to monthly:
```yaml
operation: "resample"
params:
  freq: "1M"
  aggFunc: "sum"
```

---

### 🧮 table-formula

Calculate total price:
```yaml
formulas:
  - column: "total"
    expression: "{quantity} * {price}"
```

Conditional logic:
```yaml
formulas:
  - column: "category"
    expression: "IF({amount} > 1000, 'High', 'Low')"
```

Text manipulation:
```yaml
formulas:
  - column: "full_name"
    expression: "CONCAT({first_name}, ' ', {last_name})"
  - column: "email_upper"
    expression: "UPPER(\"{email}\")"
```

---

### 🎨 table-format

Professional header:
```yaml
formatting:
  headerStyle:
    bold: true
    fontSize: 12
    fontColor: "FFFFFF"
    backgroundColor: "4472C4"
    alignment: "center"
```

Conditional color scale:
```yaml
formatting:
  conditionalFormats:
    - range: "A2:Z100"
      rule: "colorScale"
      colors: ["F8696B", "FFEB84", "63BE7B"]
```

Freeze top row and auto-fit:
```yaml
formatting:
  autoFitColumns: true
  freeze:
    row: 1
    col: 0
```

---

## Common Workflows

### Time Series Analysis
```
reader → time-series (extractFeatures)
       → formula (calculations)
       → aggregator (monthly summary)
       → writer
```

### Report Generation with Formatting
```
reader → cleaner → transformer
       → aggregator → writer
       → format (beautify)
```

### Feature Engineering
```
reader → time-series (extract features)
       → formula (derived columns)
       → validator (check quality)
       → writer
```

---

## Function Reference

### table-formula Functions

**Math**: SUM, AVG, MAX, MIN, ROUND, ABS, SQRT, POWER
**Logic**: IF, AND, OR, NOT
**Text**: CONCAT, UPPER, LOWER, TRIM, LEN

### table-time-series Operations

**resample**: Aggregate by time frequency
**rolling**: Moving window calculations
**shift**: Lag features
**diff**: Differences
**extractFeatures**: year, month, day, hour, weekday, quarter, week

### table-format Styles

**Header**: bold, italic, fontSize, fontColor, backgroundColor
**Layout**: columnWidths, rowHeights, autoFitColumns, freeze
**Conditional**: colorScale, dataBar, cellValue rules
**Validation**: list, whole, decimal, date ranges

---

## Tips & Best Practices

1. **Time Series**: Always extract time features before modeling
2. **Formulas**: Use UPPER() for text in expressions to avoid case issues
3. **Format**: Apply formatting as the LAST step after writing Excel
4. **Performance**: Use `maxRows` in reader for large files
5. **Validation**: Run table-validator before table-writer

---

## Need Help?

- Design Doc: [TABLE_BLOCKS_DESIGN.md](TABLE_BLOCKS_DESIGN.md)
- P0/P1 Summary: [P1_IMPLEMENTATION_SUMMARY.md](P1_IMPLEMENTATION_SUMMARY.md)
- P2 Summary: [P2_IMPLEMENTATION_SUMMARY.md](P2_IMPLEMENTATION_SUMMARY.md)
