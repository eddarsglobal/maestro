from maestro.meta_cognition import *

meta=MetaCognition()

checkpoint=StrategyCheckpoint(
    task_id="TASK-META-1",
    strategy_id="strategy-A",
    objective="produce verified result",
    progress_score=0.30,
    evidence_score=0.20,
    retries=3,
    resource_calls=5,
    cost_fraction=0.70,
    latency_fraction=0.65,
    assumptions={
        "source_is_current": EpistemicFlag.ASSUMED,
        "schema_valid": EpistemicFlag.VERIFIED,
    },
)

assessment=meta.assess(
    checkpoint=checkpoint,
    claims=[
        {"key":"build_status","value":"PASS"},
        {"key":"build_status","value":"FAIL"},
    ],
    required_criteria=["tests","evidence","approval"],
    evidence_by_criterion={
        "tests":["E:test"],
        "evidence":[],
        "approval":[],
    },
    verified_fraction=0.33,
    assumption_fraction=0.5,
)

print("CONFIDENCE:", round(assessment.confidence,4))
print("EVIDENCE:", round(assessment.evidence_sufficiency,4))
print("CONTRADICTION:", round(assessment.contradiction_score,4))
print("DRIFT:", round(assessment.strategy_drift_score,4))
print("EPISTEMIC:", assessment.epistemic_status.value)
print("ACTIONS:", [a.value for a in assessment.recommended_actions])
print("SAFE TO CONTINUE:", assessment.safe_to_continue)

meta.calibration.record(assessment.confidence, False, 0.0)
print("CALIBRATION ERROR:", round(meta.calibration.calibration_error(),4))
