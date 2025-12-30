from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import datetime

# ---------- INPUT ----------

class TransitRequest(BaseModel):
    """
    Schema for incoming transit analysis requests.
    """
    chart_data: dict
    transit_date: str

    @field_validator('transit_date')
    @classmethod
    def validate_date_format(cls, v):
        """
        Ensures the transit_date string matches the YYYY-MM-DD format.
        """
        try:
            # Attempt to parse the string as a date
            datetime.datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")


# ---------- OUTPUT ----------

class TransitResponse(BaseModel):
    """
    Full JSON response schema for the transit engine.
    Types are intentionally flexible (Dict[str, Any])
    to accommodate dynamic and numeric keys.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="allow"
    )

    meta: Dict[str, Any]

    natal_chart: Dict[str, Any]

    transits: Dict[str, Any]

    derived_tables: Dict[str, Any]

    raw_logs: Optional[Dict[str, Any]] = None