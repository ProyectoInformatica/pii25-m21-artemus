from dataclasses import dataclass
from model.Smoke_Model import SmokeModel


@dataclass
class SmokeRiskResult:
    is_emergency: bool
    density: int
    status: str
    message: str


def check_smoke_risk(measurement: SmokeModel) -> SmokeRiskResult:
    """
    Evaluate the smoke measurement to determine immediate risk.
    """
    density = measurement.value
    status = measurement.status  # "CLEAR", "WARNING", "ALARM"

    # Define risk based on the status determined by the controller
    is_emergency = status == "ALARM"

    if is_emergency:
        message = (
            f"EMERGENCY: High smoke density detected ({density}). "
            f"Status is {status}."
        )
    elif status == "WARNING":
        message = (
            f"CAUTION: Elevated smoke levels ({density}). "
            f"Monitor situation closely."
        )
    else:
        message = f"Air quality is normal (Density: {density})."

    return SmokeRiskResult(
        is_emergency=is_emergency,
        density=density,
        status=status,
        message=message,
    )
