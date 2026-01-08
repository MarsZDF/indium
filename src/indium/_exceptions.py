"""Exception hierarchy for indium.

Following elemental-* family pattern: all exceptions inherit from ValueError
for compatibility with standard validation flows.
"""

from typing import Optional


class IndiumError(ValueError):
    """Base exception for all indium errors."""

    pass


class InvalidTextError(IndiumError):
    """Raised when text contains invalid or malformed Unicode.

    Attributes:
        position: Optional position where the invalid character was found
    """

    def __init__(self, message: str, position: Optional[int] = None) -> None:
        """Initialize InvalidTextError.

        Args:
            message: Error description
            position: Position of invalid character (if known)
        """
        super().__init__(message)
        self.position = position


class TruncationError(IndiumError):
    """Raised when text cannot be safely truncated at requested position.

    This may occur when the truncation point falls within a grapheme cluster
    that cannot be split.
    """

    pass
