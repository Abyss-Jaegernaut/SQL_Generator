from __future__ import annotations

from dataclasses import dataclass

from core import models


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


def validate_table(table: models.TableModel) -> ValidationResult:
    errors: list[str] = []
    if not table.name:
        errors.append("Table name is required.")
    if not table.columns:
        errors.append("At least one column is required.")
    if not table.primary_keys:
        errors.append("Primary key is required.")
    if len(table.primary_keys) > 1:
        errors.append("V1.0.1 supports exactly one primary key.")
    for col in table.columns:
        if col.is_auto_increment and not col.is_primary_key:
            errors.append(f"AUTO INCREMENT is only allowed on the PK (column: {col.name}).")
    return ValidationResult(is_valid=not errors, errors=errors)


def validate_data_value(value: str, sql_type: str) -> ValidationResult:
    """Check if a string value is valid for a given SQL type."""
    import re
    
    if not value or value.upper() == "NULL":
        return ValidationResult(True, [])
        
    t = sql_type.upper()
    errors = []
    
    if "INT" in t:
        if not re.match(r"^-?\d+$", value):
            errors.append(f"Doit être un nombre entier")
            
    elif "DECIMAL" in t or "FLOAT" in t or "NUMERIC" in t:
        if not re.match(r"^-?\d+(\.\d+)?$", value):
            errors.append(f"Doit être un nombre (ex: 10.5)")
            
    elif "DATE" == t:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            errors.append(f"Format Date attendu: YYYY-MM-DD")
            
    elif "DATETIME" in t or "TIMESTAMP" in t:
        if not re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", value):
            errors.append(f"Format DateTime attendu: YYYY-MM-DD HH:MM:SS")
            
    elif "BIT" == t or "BOOLEAN" == t:
        if value not in ["0", "1", "True", "False", "true", "false"]:
            errors.append(f"Doit être 0, 1, True ou False")
            
    # For VARCHAR and others, we don't strictly validate length here 
    # but we could add length checks if needed.
    
    return ValidationResult(is_valid=not errors, errors=errors)
