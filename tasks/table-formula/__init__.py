#region generated meta
import typing

class Inputs(typing.TypedDict):
    data: list[dict[str, typing.Any]]
    formulas: list[dict[str, typing.Any]]
    functions: typing.NotRequired[dict[str, str] | None]

class Outputs(typing.TypedDict):
    data: list[dict[str, typing.Any]]
    new_columns: list[str]
    errors: list[dict[str, typing.Any]]
#endregion

from oocana import Context
import math
import re
from datetime import datetime, timedelta
from typing import Any


async def main(params: Inputs, context: Context) -> Outputs:
    """Apply formulas to calculate new columns."""

    data = params["data"]
    formulas = params["formulas"]
    custom_functions = params.get("functions") or {}

    if not data:
        raise ValueError("Input data cannot be empty")

    if not formulas:
        raise ValueError("At least one formula is required")

    result_data = [row.copy() for row in data]
    new_columns = []
    errors = []

    # Build formula evaluator
    evaluator = FormulaEvaluator(custom_functions)

    # Apply each formula
    for formula_def in formulas:
        column_name = formula_def["column"]
        expression = formula_def["expression"]
        formula_type = formula_def.get("type", "formula")

        new_columns.append(column_name)

        # Apply formula to each row
        for row_idx, row in enumerate(result_data):
            try:
                if formula_type == "formula":
                    result = evaluator.evaluate_formula(expression, row)
                else:
                    result = evaluator.evaluate_custom(expression, row)

                row[column_name] = result

            except Exception as e:
                errors.append({
                    "row": row_idx,
                    "column": column_name,
                    "error": str(e)
                })
                row[column_name] = None

    return {
        "data": result_data,
        "new_columns": new_columns,
        "errors": errors
    }


class FormulaEvaluator:
    """Excel-like formula evaluator."""

    def __init__(self, custom_functions: dict[str, str]):
        self.custom_functions = custom_functions

    def evaluate_formula(self, expression: str, row: dict) -> Any:
        """Evaluate formula expression with built-in functions."""

        # Replace column references {col} with actual values
        def replace_column(match):
            col_name = match.group(1)
            if col_name not in row:
                raise ValueError(f"Column '{col_name}' not found")
            value = row[col_name]
            if isinstance(value, str):
                return f'"{value}"'
            return str(value)

        processed_expr = re.sub(r'\{([^}]+)\}', replace_column, expression)

        # Parse and evaluate with built-in functions
        return self._eval_with_functions(processed_expr, row)

    def evaluate_custom(self, expression: str, row: dict) -> Any:
        """Evaluate custom Python expression."""

        # Replace column references
        def replace_column(match):
            col_name = match.group(1)
            if col_name not in row:
                raise ValueError(f"Column '{col_name}' not found")
            return f'row["{col_name}"]'

        processed_expr = re.sub(r'\{([^}]+)\}', replace_column, expression)

        # Evaluate with row context
        try:
            return eval(processed_expr, {"row": row, "math": math, "datetime": datetime})
        except Exception as e:
            raise ValueError(f"Failed to evaluate custom expression: {str(e)}")

    def _eval_with_functions(self, expr: str, row: dict) -> Any:
        """Evaluate expression with built-in Excel-like functions."""

        # Math functions
        expr = re.sub(r'SUM\((.*?)\)', lambda m: str(self._sum(m.group(1))), expr)
        expr = re.sub(r'AVG\((.*?)\)', lambda m: str(self._avg(m.group(1))), expr)
        expr = re.sub(r'MAX\((.*?)\)', lambda m: str(max(self._parse_args(m.group(1)))), expr)
        expr = re.sub(r'MIN\((.*?)\)', lambda m: str(min(self._parse_args(m.group(1)))), expr)
        expr = re.sub(r'ROUND\((.*?),\s*(\d+)\)', lambda m: str(round(float(m.group(1)), int(m.group(2)))), expr)
        expr = re.sub(r'ABS\((.*?)\)', lambda m: str(abs(float(m.group(1)))), expr)
        expr = re.sub(r'SQRT\((.*?)\)', lambda m: str(math.sqrt(float(m.group(1)))), expr)
        expr = re.sub(r'POWER\((.*?),\s*(.*?)\)', lambda m: str(math.pow(float(m.group(1)), float(m.group(2)))), expr)

        # Logic functions
        expr = re.sub(r'IF\((.*?),\s*(.*?),\s*(.*?)\)', lambda m: self._if(m.group(1), m.group(2), m.group(3)), expr)
        expr = re.sub(r'AND\((.*?)\)', lambda m: str(self._and(m.group(1))), expr)
        expr = re.sub(r'OR\((.*?)\)', lambda m: str(self._or(m.group(1))), expr)
        expr = re.sub(r'NOT\((.*?)\)', lambda m: str(not self._eval_bool(m.group(1))), expr)

        # Text functions
        expr = re.sub(r'CONCAT\((.*?)\)', lambda m: self._concat(m.group(1)), expr)
        expr = re.sub(r'UPPER\("(.*?)"\)', lambda m: f'"{m.group(1).upper()}"', expr)
        expr = re.sub(r'LOWER\("(.*?)"\)', lambda m: f'"{m.group(1).lower()}"', expr)
        expr = re.sub(r'TRIM\("(.*?)"\)', lambda m: f'"{m.group(1).strip()}"', expr)
        expr = re.sub(r'LEN\("(.*?)"\)', lambda m: str(len(m.group(1))), expr)

        # Evaluate final expression
        try:
            result = eval(expr)
            return result
        except Exception as e:
            raise ValueError(f"Formula evaluation failed: {str(e)}")

    def _sum(self, args_str: str) -> float:
        """Sum function."""
        args = self._parse_args(args_str)
        return sum(float(x) for x in args)

    def _avg(self, args_str: str) -> float:
        """Average function."""
        args = self._parse_args(args_str)
        return sum(float(x) for x in args) / len(args)

    def _if(self, condition: str, true_val: str, false_val: str) -> str:
        """IF function."""
        cond_result = self._eval_bool(condition)
        return true_val if cond_result else false_val

    def _and(self, args_str: str) -> bool:
        """AND function."""
        conditions = args_str.split(',')
        return all(self._eval_bool(c.strip()) for c in conditions)

    def _or(self, args_str: str) -> bool:
        """OR function."""
        conditions = args_str.split(',')
        return any(self._eval_bool(c.strip()) for c in conditions)

    def _concat(self, args_str: str) -> str:
        """CONCAT function."""
        args = self._parse_args(args_str)
        result = ''.join(str(x).strip('"') for x in args)
        return f'"{result}"'

    def _parse_args(self, args_str: str) -> list:
        """Parse comma-separated arguments."""
        args = []
        current = ""
        depth = 0

        for char in args_str:
            if char == ',' and depth == 0:
                args.append(current.strip())
                current = ""
            else:
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                current += char

        if current:
            args.append(current.strip())

        return args

    def _eval_bool(self, expr: str) -> bool:
        """Evaluate boolean expression."""
        try:
            result = eval(expr)
            return bool(result)
        except:
            return False
