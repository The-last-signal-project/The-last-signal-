from ..packet import Packet, PacketType

class decoPacket(Packet):

  def __init__(
    self,
    
    reason,
  ):
    
    self.reason = reason
    super().__init__(
            PacketType.DECO,
            reason.encode("utf-8")
        )
   

@classmethod
def from_payload(cls, payload):
  return cls(
            payload.decode("utf-8")
        )
