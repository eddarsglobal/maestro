from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import hashlib, json, struct, zlib

MAGIC=b"MSTR"; VERSION=1; FLAG_COMPRESSED=1
HEADER=struct.Struct(">4sBBHQQ32s")

class MobjError(RuntimeError): pass

@dataclass(slots=True)
class Mobj:
    object_type:int
    payload:dict[str,Any]
    compressed:bool=True

def encode(obj:Mobj, compression_level:int=9)->bytes:
    if not 0<=obj.object_type<=255: raise ValueError("object_type must fit one byte")
    raw=json.dumps(obj.payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    digest=hashlib.sha256(raw).digest(); flags=0; payload=raw
    if obj.compressed:
        payload=zlib.compress(raw,compression_level); flags|=FLAG_COMPRESSED
    return HEADER.pack(MAGIC,VERSION,obj.object_type,flags,len(raw),len(payload),digest)+payload

def decode(blob:bytes)->Mobj:
    if len(blob)<HEADER.size: raise MobjError("object too small")
    magic,version,otype,flags,raw_size,payload_size,digest=HEADER.unpack(blob[:HEADER.size])
    if magic!=MAGIC: raise MobjError("bad magic")
    if version!=VERSION: raise MobjError("unsupported version")
    payload=blob[HEADER.size:]
    if len(payload)!=payload_size: raise MobjError("payload size mismatch")
    try: raw=zlib.decompress(payload) if flags&FLAG_COMPRESSED else payload
    except zlib.error as e: raise MobjError("corrupt compressed payload") from e
    if len(raw)!=raw_size or hashlib.sha256(raw).digest()!=digest: raise MobjError("integrity check failed")
    return Mobj(otype,json.loads(raw.decode()),bool(flags&FLAG_COMPRESSED))
