#region generated meta
import typing

class Operation(typing.TypedDict):
    type: str
    params: dict[str, typing.Any]

class Inputs(typing.TypedDict):
    data: list[dict[str, typing.Any]]
    operations: list[Operation]

class Outputs(typing.TypedDict):
    data: list[dict[str, typing.Any]]
    new_columns: list[str]
    dropped_columns: list[str]
    renamed_columns: dict[str, str]
    report: list[str]
#endregion

from oocana import Context
import pandas as pd
import re


async def main(params: Inputs, context: Context) -> Outputs:
    """Transform table data with various operations."""

    data = params["data"]
    if not data:
        return {
            "data": [],
            "new_columns": [],
            "dropped_columns": [],
            "renamed_columns": {},
            "report": []
        }

    operations = params["operations"]
    if not operations:
        raise ValueError("No operations specified")

    # Convert to DataFrame
    df = pd.DataFrame(data)

    new_columns: list[str] = []
    dropped_columns: list[str] = []
    renamed_columns: dict[str, str] = {}
    report: list[str] = []

    for op in operations:
        op_type = op["type"]
        op_params = op["params"]

        if op_type == "addColumn":
            # Add a new column with default value
            new_col = op_params.get("newColumn")
            if not new_col:
                raise ValueError("'newColumn' parameter required for addColumn operation")

            default_value = op_params.get("defaultValue")
            df[new_col] = default_value
            new_columns.append(new_col)
            report.append(f"Added column '{new_col}' with default value: {default_value}")

        elif op_type == "computeColumn":
            # Add a computed column based on expression
            new_col = op_params.get("newColumn")
            expression = op_params.get("expression")

            if not new_col:
                raise ValueError("'newColumn' parameter required for computeColumn operation")
            if not expression:
                raise ValueError("'expression' parameter required for computeColumn operation")

            # Parse expression and replace {column_name} with actual values
            # Example: "{quantity} * {price}" -> df['quantity'] * df['price']
            try:
                # Find all column references in the expression
                pattern = r'\{([^}]+)\}'
                column_refs = re.findall(pattern, expression)

                # Validate all referenced columns exist
                for col_ref in column_refs:
                    if col_ref not in df.columns:
                        raise ValueError(f"Column '{col_ref}' referenced in expression not found")

                # Build the eval expression
                eval_expr = expression
                for col_ref in column_refs:
                    eval_expr = eval_expr.replace(f"{{{col_ref}}}", f"df['{col_ref}']")

                # Evaluate the expression
                df[new_col] = eval(eval_expr)
                new_columns.append(new_col)
                report.append(f"Added computed column '{new_col}' with expression: {expression}")

            except Exception as e:
                raise ValueError(f"Failed to compute column '{new_col}': {str(e)}")

        elif op_type == "renameColumn":
            # Rename columns
            old_name = op_params.get("oldName")
            new_name = op_params.get("newName")
            rename_map = op_params.get("renameMap")

            if rename_map:
                # Batch rename
                for old, new in rename_map.items():
                    if old not in df.columns:
                        raise ValueError(f"Column '{old}' not found for renaming")
                df = df.rename(columns=rename_map)
                renamed_columns.update(rename_map)
                report.append(f"Renamed {len(rename_map)} columns")
            elif old_name and new_name:
                # Single rename
                if old_name not in df.columns:
                    raise ValueError(f"Column '{old_name}' not found for renaming")
                df = df.rename(columns={old_name: new_name})
                renamed_columns[old_name] = new_name
                report.append(f"Renamed column '{old_name}' to '{new_name}'")
            else:
                raise ValueError("Must specify either 'renameMap' or both 'oldName' and 'newName'")

        elif op_type == "dropColumn":
            # Drop columns
            columns = op_params.get("columns")
            if not columns:
                raise ValueError("'columns' parameter required for dropColumn operation")

            # Validate columns exist
            for col in columns:
                if col not in df.columns:
                    raise ValueError(f"Column '{col}' not found for dropping")

            df = df.drop(columns=columns)
            dropped_columns.extend(columns)
            report.append(f"Dropped {len(columns)} columns: {', '.join(columns)}")

        elif op_type == "split":
            # Split a column into multiple columns
            column = op_params.get("column")
            delimiter = op_params.get("delimiter")
            new_cols = op_params.get("newColumns")
            max_split = op_params.get("maxSplit", -1)

            if not column:
                raise ValueError("'column' parameter required for split operation")
            if not delimiter:
                raise ValueError("'delimiter' parameter required for split operation")
            if not new_cols:
                raise ValueError("'newColumns' parameter required for split operation")

            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found for splitting")

            # Split the column
            split_data = df[column].astype(str).str.split(delimiter, n=max_split, expand=True)

            # Assign to new columns
            for i, new_col in enumerate(new_cols):
                if i < len(split_data.columns):
                    df[new_col] = split_data[i]
                    new_columns.append(new_col)
                else:
                    df[new_col] = None
                    new_columns.append(new_col)

            report.append(f"Split column '{column}' into {len(new_cols)} new columns")

        elif op_type == "merge":
            # Merge multiple columns into one
            source_cols = op_params.get("sourceColumns")
            target_col = op_params.get("targetColumn")
            separator = op_params.get("separator", "")
            template = op_params.get("template")

            if not source_cols:
                raise ValueError("'sourceColumns' parameter required for merge operation")
            if not target_col:
                raise ValueError("'targetColumn' parameter required for merge operation")

            # Validate source columns exist
            for col in source_cols:
                if col not in df.columns:
                    raise ValueError(f"Source column '{col}' not found for merging")

            if template:
                # Use template for merging
                # Example: "{first_name} {last_name}" -> "John Doe"
                def apply_template(row):
                    result = template
                    for col in source_cols:
                        result = result.replace(f"{{{col}}}", str(row[col]))
                    return result

                df[target_col] = df.apply(apply_template, axis=1)
            else:
                # Simple concatenation with separator
                df[target_col] = df[source_cols].astype(str).agg(separator.join, axis=1)

            new_columns.append(target_col)
            report.append(f"Merged {len(source_cols)} columns into '{target_col}'")

        elif op_type == "cast":
            # Cast column to a different type
            column = op_params.get("column")
            target_type = op_params.get("targetType")

            if not column:
                raise ValueError("'column' parameter required for cast operation")
            if not target_type:
                raise ValueError("'targetType' parameter required for cast operation")

            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found for casting")

            try:
                if target_type == "number":
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                elif target_type == "string":
                    df[column] = df[column].astype(str)
                elif target_type == "integer":
                    df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
                elif target_type == "float":
                    df[column] = pd.to_numeric(df[column], errors='coerce').astype(float)
                elif target_type == "boolean":
                    df[column] = df[column].astype(bool)
                elif target_type == "date":
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                else:
                    raise ValueError(f"Unsupported target type: {target_type}")

                report.append(f"Cast column '{column}' to type '{target_type}'")

            except Exception as e:
                raise ValueError(f"Failed to cast column '{column}' to '{target_type}': {str(e)}")

        else:
            raise ValueError(f"Unsupported operation type: {op_type}")

    # Convert back to list of dicts
    result_data = df.to_dict('records')

    return {
        "data": result_data,
        "new_columns": new_columns,
        "dropped_columns": dropped_columns,
        "renamed_columns": renamed_columns,
        "report": report
    }
