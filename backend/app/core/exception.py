class TelemetryError(Exception):
    """
    Base exception for telemetry domain.
    All telemetry-related errors must inherit from this.
    """
    pass


class InvalidTelemetryPayload(TelemetryError):
    """
    Raised when incoming telemetry payload is invalid
    or does not meet minimum requirements.
    """
    pass


class TelemetryPersistenceError(TelemetryError):
    """
    Raised when telemetry data cannot be persisted
    due to DB/network/system failures.
    """
    pass
