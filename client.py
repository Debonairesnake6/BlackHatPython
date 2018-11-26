import socket

target_host = '127.0.0.1'
# target_host = 'google.ca'
target_port = 5050

mode = 'tcp'
# mode = 'udp'

# Create and socket object
if mode == 'tcp':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client.connect((target_host,target_port))

    # Send data
    client.send("Hello")

    # Recieve data
    data = client.recv(4096)

elif mode == 'udp':
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send data
    client.sendto('AAABBBCCC', (target_host, target_port))

    # Receive data
    data, addr = client.recvfrom(4096)

print data
