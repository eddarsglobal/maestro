from maestro.runtime.kernel import MaestroKernel


def main() -> None:
    kernel = MaestroKernel()
    print(f"MAESTRO CORE v0.1 — councils={kernel.council_count}")
