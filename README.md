# DataCraft - Table Processing Blocks

A comprehensive collection of OOMOL task blocks for processing Excel, CSV, and TSV table files.

## 📦 Blocks Overview

This package provides 7 core table processing blocks (P0 priority) that cover the complete data processing pipeline:

### 1. **table-reader** - Table Reader
- Read Excel (.xlsx, .xls), CSV, or TSV files
- Auto-detect file format
- Support multiple sheets (Excel)
- Handle large files with row limits
- Auto-detect encoding for CSV files

### 2. **table-inspector** - Table Inspector
- View table structure and statistics
- Check data types and missing values
- Analyze data quality
- Get column-level statistics
- Preview sample data

### 3. **table-filter** - Table Filter
- Filter rows with multiple operators (==, !=, >, <, contains, in, etc.)
- Select specific columns
- Sort data (ascending/descending)
- Pagination support (limit/offset)

### 4. **table-cleaner** - Data Cleaner
- Handle missing values (drop or fill)
- Remove duplicate rows
- Type conversion
- Text normalization (trim, replace)
- Numeric normalization (min-max, z-score)

### 5. **table-transformer** - Data Transformer
- Add computed columns
- Rename/drop columns
- Split columns (e.g., full name → first/last name)
- Merge columns
- Type casting

### 6. **table-aggregator** - Data Aggregator
- GROUP BY operations
- Pivot tables
- Multiple aggregation functions (sum, avg, count, min, max, etc.)
- Multi-dimensional analysis

### 7. **table-writer** - Table Writer
- Export to Excel, CSV, or TSV
- Excel formatting (header style, column widths, freeze panes)
- Auto-filter support
- Append mode

## 🚀 Quick Start

### Example Flow: Data Cleaning Pipeline

```yaml
# 1. Read data
reader →
# 2. Inspect quality
inspector →
# 3. Clean (remove nulls, duplicates)
cleaner →
# 4. Transform (compute new columns)
transformer →
# 5. Filter (select specific data)
filter →
# 6. Export results
writer
```

## 🛠️ Dependencies

The project uses Python >=3.11 with the following libraries:

```
pandas>=2.3.3        # Core data processing
openpyxl>=3.1.5      # Excel reading/writing
xlsxwriter>=3.2.9    # Advanced Excel formatting
chardet>=5.2.0       # Encoding detection
```

## 📖 Usage Examples

### Example 1: Simple Data Cleanup

```yaml
nodes:
  - node_id: read#1
    task: self::table-reader
    inputs_from:
      - handle: file_path
        value: "/data/sales.xlsx"

  - node_id: clean#1
    task: self::table-cleaner
    inputs_from:
      - handle: data
        from_node:
          - node_id: read#1
            output_handle: data
      - handle: operations
        value:
          - type: "dropNull"
          - type: "dropDuplicates"

  - node_id: write#1
    task: self::table-writer
    inputs_from:
      - handle: data
        from_node:
          - node_id: clean#1
            output_handle: data
      - handle: output_path
        value: "/output/sales_clean.xlsx"
```

### Example 2: Sales Analysis

```yaml
# Read → Clean → Aggregate by Region → Export
nodes:
  - node_id: read#1
    task: self::table-reader
    inputs_from:
      - handle: file_path
        value: "/data/sales.csv"

  - node_id: aggregate#1
    task: self::table-aggregator
    inputs_from:
      - handle: data
        from_node:
          - node_id: read#1
            output_handle: data
      - handle: mode
        value: "groupBy"
      - handle: group_by
        value: ["region"]
      - handle: aggregations
        value:
          - column: "amount"
            function: "sum"
            alias: "total_sales"
          - column: "customer_id"
            function: "countUnique"
            alias: "customer_count"
```

## 🎯 Design Principles

1. **Pipeline Architecture**: All blocks use standard `Array<Record<string, any>>` format for seamless chaining
2. **Progressive Complexity**: From simple to advanced, suitable for different skill levels
3. **Type Safety**: Complete input/output type definitions
4. **Error Handling**: Clear error messages with validation
5. **Performance**: Support for large files with streaming and optimization

## 📚 Documentation

For detailed specifications, see [TABLE_BLOCKS_DESIGN.md](./TABLE_BLOCKS_DESIGN.md)

## 🔧 Development

### Setup

```bash
# Install dependencies
poetry install --no-root
npm install

# Or use bootstrap script
poetry run oomol bootstrap
```

### Testing

Create sample data and run the demo flow in `flows/flow-1/`.

## 📊 Roadmap

### ✅ P0 - Core Blocks (Completed)
- table-reader
- table-inspector
- table-filter
- table-cleaner
- table-transformer
- table-aggregator
- table-writer

### 🔜 P1 - Advanced Features (Planned)
- table-joiner (multi-table joins)
- table-validator (data validation)
- table-analyzer (statistical analysis)
- table-sampler (data sampling)
- table-splitter (dataset splitting)

### 🎯 P2 - Expert Features (Future)
- table-time-series
- table-formula
- table-format

## 📄 License

MIT

## 👥 Author

**shaun** - beingswu@gmail.com

---

Built with ❤️ for OOMOL
