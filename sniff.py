import socket

# the public network interface
HOST = socket.gethostbyname(socket.gethostname())

# create a raw socket and bind it to the public interface
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
s.bind((HOST, 0))

# Include IP headers
s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# receive all packages
s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# receive a package
print s.recvfrom(34340)

# disabled promiscuous mode
s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


from ctypes import c_int32, c_uint32, Structure, Union

class _bits(Structure):
    _fields_ = [
        ("odd", c_uint32, 1),
        ("half", c_uint32, 31),
    ]

class Int(Union):
    _fields_ = [
        ("bits", _bits),
        ("number", c_uint32),
    ]


a = Int(number=12345)
a.bits.odd, a.bits.half
