from __future__ import annotations

from maestro.councils.registry import COUNCILS, validate_registry
from maestro.runtime.kernel import MaestroKernel


class BootValidationError(RuntimeError):
    pass


class BootValidator:
    """
    Production boot guard.

    The process should not advertise readiness if constitutional invariants
    fail during initialization.
    """

    def validate(self) -> dict:
        validate_registry()
        kernel = MaestroKernel()

        if kernel.council_count != 18:
            raise BootValidationError("Genesis Council registry must contain exactly 18 Councils.")

        if len(COUNCILS) != 18:
            raise BootValidationError("Genesis Council registry mismatch.")

        variables = [spec.system_variable for spec in COUNCILS.values()]
        if len(set(variables)) != 18:
            raise BootValidationError("Council system variables must be unique.")

        return {
            "genesis_councils": 18,
            "kernel": "OK",
            "registry": "OK",
            "unique_variables": True,
        }
