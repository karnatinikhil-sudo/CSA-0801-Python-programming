"""Custom exceptions for the Digital Complaint Registration and Tracking System.

This module defines the hierarchy of domain-specific exceptions used throughout
the complaint lifecycle management, tracking, and reporting processes.
"""


class ComplaintSystemError(Exception):
    """Base exception class for all errors originating within the Complaint System.

    Attributes:
        message (str): Explanation of the error.
    """

    def __init__(self, message: str = "An error occurred in the Complaint System.") -> None:
        """Initialize ComplaintSystemError.

        Args:
            message: Descriptive error message.
        """
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        """Return formatted string representation of the error."""
        return self.message


class InvalidComplaintIDError(ComplaintSystemError):
    """Exception raised when a specified Complaint ID does not exist or is invalid."""

    def __init__(self, complaint_id: str, message: str | None = None) -> None:
        """Initialize InvalidComplaintIDError.

        Args:
            complaint_id: The invalid or missing complaint identifier.
            message: Optional custom message override.
        """
        self.complaint_id = complaint_id
        if message is None:
            message = f"Invalid or non-existent Complaint ID: '{complaint_id}'."
        super().__init__(message)


class InvalidStatusError(ComplaintSystemError):
    """Exception raised when an unsupported or invalid status transition is requested."""

    def __init__(self, status: str, valid_statuses: tuple | list | None = None, message: str | None = None) -> None:
        """Initialize InvalidStatusError.

        Args:
            status: The invalid status provided.
            valid_statuses: Optional iterable of permitted status names.
            message: Optional custom message override.
        """
        self.status = status
        self.valid_statuses = valid_statuses
        if message is None:
            if valid_statuses:
                message = (
                    f"Invalid status: '{status}'. "
                    f"Must be one of: {', '.join(valid_statuses)}."
                )
            else:
                message = f"Invalid status: '{status}'."
        super().__init__(message)


class DuplicateComplaintError(ComplaintSystemError):
    """Exception raised when an attempt is made to register or overwrite a duplicate complaint."""

    def __init__(self, complaint_id: str, message: str | None = None) -> None:
        """Initialize DuplicateComplaintError.

        Args:
            complaint_id: The duplicate complaint identifier.
            message: Optional custom message override.
        """
        self.complaint_id = complaint_id
        if message is None:
            message = f"Duplicate complaint detected for ID: '{complaint_id}'."
        super().__init__(message)
