import socket
s = socket.socket()
s.settimeout(5.0)
try:
    s.connect(('10.1.0.65', 8080))
    print("SUCCESS: Connected to 10.1.0.65:8080")
except Exception as e:
    print("FAILED:", type(e), e)
finally:
    s.close()
