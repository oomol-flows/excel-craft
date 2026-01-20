#region generated meta
import typing

class HeaderStyle(typing.TypedDict, total=False):
    bold: bool
    background_color: str
    font_size: int

class FreezePaneConfig(typing.TypedDict):
    row: int
    col: int

class FormattingOptions(typing.TypedDict, total=False):
    header_style: HeaderStyle
    column_widths: dict[str, int]
    auto_filter: bool
    freeze_pane: FreezePaneConfig

class Inputs(typing.TypedDict):
    data: list[dict[str, typing.Any]]
    output_path: str
    format: typing.NotRequired[str]
    sheet_name: typing.NotRequired[str]
    include_header: typing.NotRequired[bool]
    encoding: typing.NotRequired[str]
    append: typing.NotRequired[bool]
    formatting: typing.NotRequired[FormattingOptions]

class Outputs(typing.TypedDict):
    file_path: str
    rows_written: int
    columns_written: int
    file_size: int
    success: bool
    format: str
#endregion

from oocana import Context
import pandas as pd
import os


async def main(params: Inputs, context: Context) -> Outputs:
    """Write table data to file."""

    data = params["data"]
    output_path = params["output_path"]

    if not data:
        raise ValueError("Input data is empty")

    # Default output path to session directory if relative
    if not os.path.isabs(output_path):
        output_path = os.path.join(context.session_dir, output_path)

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Determine format
    format_type = params.get("format")
    if not format_type:
        # Infer from file extension
        ext = os.path.splitext(output_path)[1].lower()
        if ext == '.xlsx':
            format_type = "excel"
        elif ext == '.csv':
            format_type = "csv"
        elif ext == '.tsv':
            format_type = "tsv"
        else:
            raise ValueError(f"Cannot infer format from extension: {ext}. Please specify 'format' parameter.")

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Get options
    include_header = params.get("include_header")
    if include_header is None:
        include_header = True

    encoding = params.get("encoding") or "utf-8"
    append_mode = params.get("append") or False

    # Write based on format
    if format_type == "excel":
        # Excel format
        sheet_name = params.get("sheet_name") or "Sheet1"
        formatting = params.get("formatting")

        if formatting:
            # Use xlsxwriter for advanced formatting
            import xlsxwriter

            # Create workbook
            workbook = xlsxwriter.Workbook(output_path)
            worksheet = workbook.add_worksheet(sheet_name)

            # Create header format
            header_style = formatting.get("header_style", {})
            header_format = workbook.add_format()

            if header_style.get("bold"):
                header_format.set_bold()
            if header_style.get("background_color"):
                header_format.set_bg_color(header_style["background_color"])
            if header_style.get("font_size"):
                header_format.set_font_size(header_style["font_size"])

            # Write headers
            if include_header:
                for col_idx, col_name in enumerate(df.columns):
                    worksheet.write(0, col_idx, col_name, header_format)

            # Write data
            for row_idx, row_data in enumerate(df.itertuples(index=False), start=1 if include_header else 0):
                for col_idx, value in enumerate(row_data):
                    worksheet.write(row_idx, col_idx, value)

            # Apply column widths
            column_widths = formatting.get("column_widths", {})
            for col_name, width in column_widths.items():
                if col_name in df.columns:
                    col_idx = df.columns.get_loc(col_name)
                    worksheet.set_column(col_idx, col_idx, width)

            # Apply auto filter
            if formatting.get("auto_filter"):
                last_col_idx = len(df.columns) - 1
                last_row_idx = len(df)
                worksheet.autofilter(0, 0, last_row_idx, last_col_idx)

            # Apply freeze pane
            freeze_pane = formatting.get("freeze_pane")
            if freeze_pane:
                worksheet.freeze_panes(freeze_pane["row"], freeze_pane["col"])

            workbook.close()

        else:
            # Simple Excel write
            mode = 'a' if append_mode else 'w'
            if_sheet_exists = 'overlay' if append_mode else None

            with pd.ExcelWriter(output_path, engine='openpyxl', mode=mode, if_sheet_exists=if_sheet_exists) as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False, header=include_header)

    elif format_type == "csv":
        # CSV format
        mode = 'a' if append_mode else 'w'
        df.to_csv(output_path, index=False, header=include_header, encoding=encoding, mode=mode)

    elif format_type == "tsv":
        # TSV format
        mode = 'a' if append_mode else 'w'
        df.to_csv(output_path, sep='\t', index=False, header=include_header, encoding=encoding, mode=mode)

    else:
        raise ValueError(f"Unsupported output format: {format_type}")

    # Get file size
    file_size = os.path.getsize(output_path)

    return {
        "file_path": output_path,
        "rows_written": len(df),
        "columns_written": len(df.columns),
        "file_size": file_size,
        "success": True,
        "format": format_type
    }
