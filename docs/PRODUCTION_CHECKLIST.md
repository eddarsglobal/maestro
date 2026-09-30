# MAESTRO v1.0 Production Checklist

Before a real deployment:

- [ ] Environment secrets are externalized.
- [ ] Provider credentials are scoped and rotated.
- [ ] A3/A4 approval channels are configured.
- [ ] Production tool allowlists are reviewed.
- [ ] Network egress policy is configured.
- [ ] Durable DB/object-store backend is selected.
- [ ] Backup/restore is tested.
- [ ] Worker identity policy is configured.
- [ ] Fencing/idempotency support of external targets is verified.
- [ ] Observability/export destination is configured.
- [ ] Council adapters are tested against real tools/providers.
- [ ] Failure injection/chaos tests run in staging.
- [ ] Legal/security requirements are reviewed for the deployment jurisdiction/use case.
- [ ] Rollback procedure is rehearsed.
