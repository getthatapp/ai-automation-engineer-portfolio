"""Notification-specific exceptions."""


class NotificationDeliveryError(Exception):
    """Raised by notification providers when delivery cannot complete."""
