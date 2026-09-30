from __future__ import annotations
from dataclasses import dataclass
import base64, hashlib, hmac, os, time
from .backend import ClusterBackend

class IdentityError(PermissionError): pass

@dataclass(frozen=True,slots=True)
class WorkerChallenge:
    worker_id:str
    nonce:str
    expires_at:float

class WorkerIdentityAuthority:
    """Reference HMAC worker identity. Production may replace with mTLS/Ed25519 adapter."""
    def __init__(self, backend:ClusterBackend):
        self.backend=backend
        self._secrets:dict[str,bytes]={}

    def enroll(self, worker_id:str, secret:bytes|None=None)->bytes:
        if not worker_id: raise ValueError('worker_id required')
        secret=secret or os.urandom(32)
        if len(secret)<16: raise ValueError('worker secret too short')
        self._secrets[worker_id]=secret
        return secret

    def issue_challenge(self, worker_id:str, ttl_seconds:int=30)->WorkerChallenge:
        if worker_id not in self._secrets: raise IdentityError('Unknown worker.')
        nonce=base64.urlsafe_b64encode(os.urandom(24)).decode().rstrip('='); exp=time.time()+ttl_seconds
        with self.backend.immediate() as con:
            con.execute('INSERT INTO cluster_worker_nonces(worker_id,nonce,expires_at,consumed) VALUES(?,?,?,0)',(worker_id,nonce,exp))
        return WorkerChallenge(worker_id,nonce,exp)

    @staticmethod
    def sign(secret:bytes, challenge:WorkerChallenge)->str:
        msg=f'{challenge.worker_id}|{challenge.nonce}|{challenge.expires_at:.6f}'.encode()
        return hmac.new(secret,msg,hashlib.sha256).hexdigest()

    def verify(self, challenge:WorkerChallenge, signature:str)->bool:
        secret=self._secrets.get(challenge.worker_id)
        if not secret: raise IdentityError('Unknown worker.')
        with self.backend.immediate() as con:
            row=con.execute('SELECT expires_at,consumed FROM cluster_worker_nonces WHERE worker_id=? AND nonce=?',(challenge.worker_id,challenge.nonce)).fetchone()
            if not row or row['consumed'] or row['expires_at']<=time.time(): raise IdentityError('Challenge missing, replayed, or expired.')
            expected=self.sign(secret,challenge)
            if not hmac.compare_digest(expected,signature): raise IdentityError('Invalid worker signature.')
            con.execute('UPDATE cluster_worker_nonces SET consumed=1 WHERE worker_id=? AND nonce=?',(challenge.worker_id,challenge.nonce))
        return True
