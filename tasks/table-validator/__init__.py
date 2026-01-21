#region generated meta
import typing
class Inputs(typing.TypedDict):
    data: list[dict]
    rules: list[dict]
    stopOnError: bool | None
class Outputs(typing.TypedDict):
    valid: typing.NotRequired[bool]
    errors: typing.NotRequired[list[dict]]
    summary: typing.NotRequired[dict]
#endregion

from oocana import Context
import pandas as pd
import re


async def main(params: Inputs, context: Context) -> Outputs:
    """
    Validate table data against defined rules.

    Supports various validation types:
    - notNull: Check for non-null values
    - unique: Check for unique values
    - range: Check numeric values are within range
    - pattern: Check string matches regex pattern
    - enum: Check value is in allowed list
    - length: Check string length
    - dataType: Check value type
    - custom: Custom validation expression
    """

    # Extract parameters
    data = params["data"]
    rules = params["rules"]
    stop_on_error = params.get("stopOnError", False)

    if not data:
        raise ValueError("Data cannot be empty")

    if not rules:
        raise ValueError("At least one validation rule is required")

    df = pd.DataFrame(data)
    errors: list[ValidationError] = []
    errors_by_rule: dict[str, int] = {}
    error_row_indices = set()
    warning_row_indices = set()

    # Process each rule
    for rule in rules:
        column = rule.get("column")
        rule_type = rule.get("type")
        params_dict = rule.get("params", {})
        severity = rule.get("severity", "error")
        custom_message = rule.get("message", "")

        if not column:
            raise ValueError("Each rule must specify a 'column'")
        if not rule_type:
            raise ValueError(f"Each rule must specify a 'type' for column '{column}'")

        # Check if column exists
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in data. Available columns: {list(df.columns)}")

        # Initialize error counter for this rule
        rule_name = f"{column}:{rule_type}"
        errors_by_rule[rule_name] = 0

        # Validate based on rule type
        if rule_type == "notNull":
            for idx, value in enumerate(df[column]):
                if pd.isna(value) or value is None:
                    message = custom_message or f"Value cannot be null"
                    errors.append({
                        "row": idx,
                        "column": column,
                        "rule": rule_type,
                        "value": None,
                        "message": message,
                        "severity": severity
                    })
                    errors_by_rule[rule_name] += 1
                    if severity == "error":
                        error_row_indices.add(idx)
                    else:
                        warning_row_indices.add(idx)

                    if stop_on_error and severity == "error":
                        break

        elif rule_type == "unique":
            # Find duplicates
            duplicates = df[column].duplicated(keep=False)
            for idx in df[duplicates].index:
                value = df.loc[idx, column]
                message = custom_message or f"Value must be unique, found duplicate: {value}"
                errors.append({
                    "row": int(idx),
                    "column": column,
                    "rule": rule_type,
                    "value": value,
                    "message": message,
                    "severity": severity
                })
                errors_by_rule[rule_name] += 1
                if severity == "error":
                    error_row_indices.add(int(idx))
                else:
                    warning_row_indices.add(int(idx))

        elif rule_type == "range":
            min_val = params_dict.get("min")
            max_val = params_dict.get("max")

            for idx, value in enumerate(df[column]):
                if pd.notna(value):
                    try:
                        num_value = float(value)
                        if min_val is not None and num_value < min_val:
                            message = custom_message or f"Value {num_value} is below minimum {min_val}"
                            errors.append({
                                "row": idx,
                                "column": column,
                                "rule": rule_type,
                                "value": value,
                                "message": message,
                                "severity": severity
                            })
                            errors_by_rule[rule_name] += 1
                            if severity == "error":
                                error_row_indices.add(idx)
                            else:
                                warning_row_indices.add(idx)

                        if max_val is not None and num_value > max_val:
                            message = custom_message or f"Value {num_value} is above maximum {max_val}"
                            errors.append({
                                "row": idx,
                                "column": column,
                                "rule": rule_type,
                                "value": value,
                                "message": message,
                                "severity": severity
                            })
                            errors_by_rule[rule_name] += 1
                            if severity == "error":
                                error_row_indices.add(idx)
                            else:
                                warning_row_indices.add(idx)
                    except (ValueError, TypeError):
                        message = custom_message or f"Value {value} is not a valid number"
                        errors.append({
                            "row": idx,
                            "column": column,
                            "rule": rule_type,
                            "value": value,
                            "message": message,
                            "severity": severity
                        })
                        errors_by_rule[rule_name] += 1
                        if severity == "error":
                            error_row_indices.add(idx)
                        else:
                            warning_row_indices.add(idx)

        elif rule_type == "pattern":
            regex = params_dict.get("regex")
            if not regex:
                raise ValueError(f"Pattern rule for column '{column}' requires 'regex' parameter")

            pattern = re.compile(regex)
            for idx, value in enumerate(df[column]):
                if pd.notna(value):
                    str_value = str(value)
                    if not pattern.match(str_value):
                        message = custom_message or f"Value '{str_value}' does not match pattern '{regex}'"
                        errors.append({
                            "row": idx,
                            "column": column,
                            "rule": rule_type,
                            "value": value,
                            "message": message,
                            "severity": severity
                        })
                        errors_by_rule[rule_name] += 1
                        if severity == "error":
                            error_row_indices.add(idx)
                        else:
                            warning_row_indices.add(idx)

        elif rule_type == "enum":
            allowed_values = params_dict.get("allowedValues", [])
            if not allowed_values:
                raise ValueError(f"Enum rule for column '{column}' requires 'allowedValues' parameter")

            for idx, value in enumerate(df[column]):
                if pd.notna(value) and value not in allowed_values:
                    message = custom_message or f"Value '{value}' not in allowed values: {allowed_values}"
                    errors.append({
                        "row": idx,
                        "column": column,
                        "rule": rule_type,
                        "value": value,
                        "message": message,
                        "severity": severity
                    })
                    errors_by_rule[rule_name] += 1
                    if severity == "error":
                        error_row_indices.add(idx)
                    else:
                        warning_row_indices.add(idx)

        elif rule_type == "length":
            min_length = params_dict.get("minLength")
            max_length = params_dict.get("maxLength")

            for idx, value in enumerate(df[column]):
                if pd.notna(value):
                    str_value = str(value)
                    length = len(str_value)

                    if min_length is not None and length < min_length:
                        message = custom_message or f"Length {length} is below minimum {min_length}"
                        errors.append({
                            "row": idx,
                            "column": column,
                            "rule": rule_type,
                            "value": value,
                            "message": message,
                            "severity": severity
                        })
                        errors_by_rule[rule_name] += 1
                        if severity == "error":
                            error_row_indices.add(idx)
                        else:
                            warning_row_indices.add(idx)

                    if max_length is not None and length > max_length:
                        message = custom_message or f"Length {length} is above maximum {max_length}"
                        errors.append({
                            "row": idx,
                            "column": column,
                            "rule": rule_type,
                            "value": value,
                            "message": message,
                            "severity": severity
                        })
                        errors_by_rule[rule_name] += 1
                        if severity == "error":
                            error_row_indices.add(idx)
                        else:
                            warning_row_indices.add(idx)

        elif rule_type == "dataType":
            expected_type = params_dict.get("dataType")
            if not expected_type:
                raise ValueError(f"DataType rule for column '{column}' requires 'dataType' parameter")

            for idx, value in enumerate(df[column]):
                if pd.notna(value):
                    valid_type = False

                    if expected_type == "number":
                        valid_type = isinstance(value, (int, float)) and not isinstance(value, bool)
                    elif expected_type == "string":
                        valid_type = isinstance(value, str)
                    elif expected_type == "boolean":
                        valid_type = isinstance(value, bool)
                    elif expected_type == "date":
                        valid_type = isinstance(value, (pd.Timestamp, pd.DatetimeTZDtype))

                    if not valid_type:
                        message = custom_message or f"Value '{value}' is not of type '{expected_type}'"
                        errors.append({
                            "row": idx,
                            "column": column,
                            "rule": rule_type,
                            "value": value,
                            "message": message,
                            "severity": severity
                        })
                        errors_by_rule[rule_name] += 1
                        if severity == "error":
                            error_row_indices.add(idx)
                        else:
                            warning_row_indices.add(idx)

        elif rule_type == "custom":
            # Custom validation using Python expression
            custom_func = params_dict.get("customFunc")
            if not custom_func:
                raise ValueError(f"Custom rule for column '{column}' requires 'customFunc' parameter")

            # Note: In production, you'd want to use a safer evaluation method
            # This is a simplified example
            for idx, value in enumerate(df[column]):
                try:
                    # Create a safe evaluation context
                    context_vars = {"value": value, "pd": pd}
                    result = eval(custom_func, {"__builtins__": {}}, context_vars)
                    if not result:
                        message = custom_message or f"Custom validation failed for value '{value}'"
                        errors.append({
                            "row": idx,
                            "column": column,
                            "rule": rule_type,
                            "value": value,
                            "message": message,
                            "severity": severity
                        })
                        errors_by_rule[rule_name] += 1
                        if severity == "error":
                            error_row_indices.add(idx)
                        else:
                            warning_row_indices.add(idx)
                except Exception as e:
                    message = custom_message or f"Custom validation error: {str(e)}"
                    errors.append({
                        "row": idx,
                        "column": column,
                        "rule": rule_type,
                        "value": value,
                        "message": message,
                        "severity": severity
                    })
                    errors_by_rule[rule_name] += 1
                    if severity == "error":
                        error_row_indices.add(idx)
                    else:
                        warning_row_indices.add(idx)

        # Stop on first error if requested
        if stop_on_error and error_row_indices:
            break

    # Calculate summary
    total_rows = len(df)
    error_rows = len(error_row_indices)
    warning_rows = len(warning_row_indices - error_row_indices)  # Warnings not counted as errors
    valid_rows = total_rows - error_rows

    # Determine if validation passed
    has_errors = error_rows > 0
    valid = not has_errors

    summary: ValidationSummary = {
        "totalRows": total_rows,
        "validRows": valid_rows,
        "errorRows": error_rows,
        "warningRows": warning_rows,
        "errorsByRule": errors_by_rule
    }

    return {
        "valid": valid,
        "errors": errors,
        "summary": summary
    }
