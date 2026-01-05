"""Policy guard for enforcing write operation rules."""


class PolicyGuard:
    """Enforce policy on write operations."""

    def __init__(self, allowlist: set[str], confirm_string: str):
        """Initialize the policy guard.

        Args:
            allowlist: Set of allowed tool operation IDs.
            confirm_string: Required confirmation string for write operations.
        """
        self.allowlist = allowlist
        self.confirm_string = confirm_string

    def enforce_write(self, tool_name: str, confirm: str | None):
        """Enforce policy on a write operation.

        Args:
            tool_name: Name of the tool being called.
            confirm: Confirmation string from user.

        Raises:
            ValueError: If tool not allowlisted or confirm string doesn't match.
        """
        if tool_name not in self.allowlist:
            raise ValueError(f"Tool '{tool_name}' is not allowlisted for write operations")

        if confirm != self.confirm_string:
            raise ValueError(
                "Invalid confirm string - "
                "write operations require explicit confirmation"
            )
