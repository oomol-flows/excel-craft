#region generated meta
import typing

class Inputs(typing.TypedDict):
    file_path: str
    format: typing.NotRequired[str]
    sheet_name: typing.NotRequired[str]
    sheet_index: typing.NotRequired[int]
    header_row: typing.NotRequired[int]
    encoding: typing.NotRequired[str]
    skip_rows: typing.NotRequired[int]
    max_rows: typing.NotRequired[int]

class Outputs(typing.TypedDict):
    data: list[dict[str, typing.Any]]
    columns: list[str]
    shape: dict[str, int]
    metadata: dict[str, typing.Any]
#endregion

from oocana import Context
import pandas as pd
import os
import chardet


async def main(params: Inputs, context: Context) -> Outputs:
    """Read table data from Excel, CSV, or TSV files."""

    file_path = params["file_path"]
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get file size and name
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    # Auto-detect format if not specified
    format_type = params.get("format") or "auto"
    if format_type == "auto":
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.xlsx', '.xls']:
            format_type = "excel"
        elif ext == '.csv':
            format_type = "csv"
        elif ext == '.tsv':
            format_type = "tsv"
        else:
            raise ValueError(f"Cannot auto-detect format for extension: {ext}")

    # Read data based on format
    df: pd.DataFrame
    metadata: dict[str, typing.Any] = {
        "fileName": file_name,
        "format": format_type,
        "fileSize": file_size
    }

    if format_type == "excel":
        # Read Excel file
        sheet_name = params.get("sheet_name")
        sheet_index = params.get("sheet_index") or 0
        header_row = params.get("header_row") or 0
        skip_rows = params.get("skip_rows") or 0
        max_rows = params.get("max_rows")

        # Get all sheet names first
        import openpyxl
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        sheet_names = wb.sheetnames
        wb.close()

        metadata["sheetNames"] = sheet_names

        # Determine which sheet to read
        if sheet_name:
            target_sheet = sheet_name
        else:
            target_sheet = sheet_index

        # Read the Excel file
        read_params = {
            "sheet_name": target_sheet,
            "header": header_row,
        }

        if skip_rows:
            read_params["skiprows"] = skip_rows

        if max_rows:
            read_params["nrows"] = max_rows

        df = pd.read_excel(file_path, **read_params)

    elif format_type in ["csv", "tsv"]:
        # Read CSV/TSV file
        encoding = params.get("encoding")
        if not encoding:
            # Auto-detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'

        metadata["encoding"] = encoding

        header_row = params.get("header_row") or 0
        skip_rows = params.get("skip_rows") or 0
        max_rows = params.get("max_rows")

        delimiter = '\t' if format_type == "tsv" else ','

        read_params = {
            "encoding": encoding,
            "header": header_row,
            "sep": delimiter,
        }

        if skip_rows:
            read_params["skiprows"] = skip_rows

        if max_rows:
            read_params["nrows"] = max_rows

        df = pd.read_csv(file_path, **read_params)

    else:
        raise ValueError(f"Unsupported format: {format_type}")

    # Convert DataFrame to list of dicts
    data = df.to_dict('records')

    # Get column names
    columns = df.columns.tolist()

    # Get shape
    shape = {
        "rows": len(df),
        "cols": len(df.columns)
    }

    return {
        "data": data,
        "columns": columns,
        "shape": shape,
        "metadata": metadata
    }
