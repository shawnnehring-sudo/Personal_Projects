import socket

MAGIC = 0xA5
LED_COUNT = 61
PACKET_SIZE = 1 + LED_COUNT * 3


class ESP32Client:
    """
    Sends one complete 61-LED RGB framebuffer over UDP.

    Packet:
      byte 0      = 0xA5
      bytes 1..183 = R,G,B for LED 0..60
    """

    def __init__(self, host: str = "", port: int = 4210):
        self.host = host.strip()
        self.port = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    @property
    def enabled(self) -> bool:
        return bool(self.host)

    def set_host(self, host: str):
        self.host = host.strip()

    def send_frame(self, colors: list[tuple[int, int, int]]):
        if not self.enabled:
            return
        if len(colors) != LED_COUNT:
            raise ValueError(f"Expected {LED_COUNT} LED colors.")

        packet = bytearray([MAGIC])
        for r, g, b in colors:
            packet.extend((
                max(0, min(255, int(r))),
                max(0, min(255, int(g))),
                max(0, min(255, int(b))),
            ))
        self.sock.sendto(packet, (self.host, self.port))
