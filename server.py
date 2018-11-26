import socket
import threading

bind_ip = '0.0.0.0'
bind_port = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print '[*] Listening on %s:%d' % (bind_ip, bind_port)


# Client-handling socket
def handle_client(client_socket):

    # Print what the client sends
    request = client_socket.recv(1024)

    print '[*] Received: %s' % request

    # Send back a packet
    client_socket.send('ACK!')

    client_socket.close()


while True:

    client, address = server.accept()

    print '[*] Accepted connection from: %s:%d' % (address[0], address[1])

    # Create thread to handle incoming connection
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
