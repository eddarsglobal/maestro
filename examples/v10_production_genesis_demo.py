import tempfile
from maestro import ProductionGenesisSystem
from maestro.genesis.e2e import EndToEndMissionHarness

with tempfile.TemporaryDirectory() as td:
    system = ProductionGenesisSystem(td)

    boot = system.start()
    print("BOOT:", boot["status"], boot["version"])
    print("GENESIS COUNCILS:", boot["boot"]["genesis_councils"])

    health = system.health_report()
    print("HEALTH:", health.status.value)

    e2e = EndToEndMissionHarness().run()
    print("E2E DAG COMPLETE:", e2e.dag_complete)
    print("AY SYSTEM JUSTE:", e2e.ay_system_juste)
    print("TX COMMITTED:", e2e.tx_committed)
    print("MISSION COMPLETE:", e2e.mission_complete)
    print("EVIDENCE:", e2e.evidence_count)
