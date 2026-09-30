import unittest
from maestro.storage.mobj import Mobj,MobjError,encode,decode
class T(unittest.TestCase):
 def test_roundtrip(self): self.assertEqual(decode(encode(Mobj(1,{'x':'hello'*100}))).payload['x'],'hello'*100)
 def test_corruption(self):
  b=bytearray(encode(Mobj(1,{'x':'hello'}))); b[-1]^=255
  with self.assertRaises(MobjError): decode(bytes(b))
