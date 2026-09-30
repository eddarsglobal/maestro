import tempfile
from maestro.fabric import DistributedIntelligenceFabric,FabricWorkItem,WorkerAdvertisement

with tempfile.TemporaryDirectory() as td:
 f=DistributedIntelligenceFabric(td)
 f.workers.advertise(WorkerAdvertisement('worker-it-a','node-a',{'IT'},{'python','repo'},0.7))
 f.workers.advertise(WorkerAdvertisement('worker-it-b','node-b',{'IT'},{'python','repo'},0.2))
 placement=f.placement.place('IT',{'python','repo'})
 print('PLACEMENT:',placement.worker_id,placement.node_id,round(placement.score,3))
 ctx=f.contexts.publish({'task':'build api','evidence':['E1','E2']}); print('CONTEXT HASH:',ctx.sha256[:16])
 work=FabricWorkItem('TASK-1','IT','IMPLEMENT',{'context_ref':ctx.sha256},idempotency_key='TASK-1:IT:IMPLEMENT')
 wid=f.queue.enqueue(work); leased=f.queue.lease_next(placement.worker_id,{'IT'},30); print('LEASED:',leased.work_id==wid,leased.leased_by)
 f.queue.complete(wid,placement.worker_id); print('STATUS:',f.queue.get(wid).status.value)
 lock=f.locks.acquire('mission:TASK-1','node-a',30); print('LOCK:',bool(lock))
 batch=f.academy.ingest([{'scenario':'S1','score':0.91}],[{'policy':'P2','delta':0.04}]); print('ACADEMY BATCH:',batch.batch_id,batch.items)
