import tempfile,time
from maestro.resilience import ResilientCluster,NodeRecord,PlacementObservation
from maestro.fabric.workers import WorkerAdvertisement
from maestro.fabric.queue import FabricWorkItem

with tempfile.TemporaryDirectory() as td:
 c=ResilientCluster(td)
 c.nodes.advertise(NodeRecord('node-a')); c.nodes.advertise(NodeRecord('node-b'))
 c.fabric.workers.advertise(WorkerAdvertisement('worker-a','node-a',{'IT'},{'code'},load=0.2))
 c.fabric.workers.advertise(WorkerAdvertisement('worker-b','node-b',{'IT'},{'code'},load=0.2))
 for _ in range(5):
  c.placement.observe(PlacementObservation('worker-a','node-a','IT',False,900,4))
  c.placement.observe(PlacementObservation('worker-b','node-b','IT',True,100,1))
 print('PLACEMENT:',c.placement.place('IT',{'code'}).worker_id)
 secret=c.identity.enroll('worker-b',b's'*32); ch=c.identity.issue_challenge('worker-b'); print('IDENTITY:',c.identity.verify(ch,c.identity.sign(secret,ch)))
 l1=c.fencing.acquire('project:T1','worker-b',ttl_seconds=1); print('FENCE-1:',l1.fencing_token)
 with c.backend.immediate() as con: con.execute('UPDATE cluster_fenced_locks SET expires_at=? WHERE lock_name=?',(time.time()-1,'project:T1'))
 l2=c.fencing.acquire('project:T1','worker-a',ttl_seconds=30); print('FENCE-2:',l2.fencing_token)
 rec,new=c.effects.prepare('deploy:T1',{'artifact':'abc'},l2.fencing_token); c.effects.commit('deploy:T1',{'status':'ok'},l2.fencing_token); print('EFFECT:',c.effects.get('deploy:T1').state.value)
 wid=c.fabric.queue.enqueue(FabricWorkItem('T1','IT','IMPLEMENT')); item=c.fabric.queue.lease_next('worker-b',{'IT'},lease_seconds=30); c.chaos.expire_work_lease(item.work_id); print('RECLAIMED:',len(c.fabric.queue.reclaim_expired()))
 snap=c.observability.snapshot(); print('CLUSTER:',snap.to_dict())
