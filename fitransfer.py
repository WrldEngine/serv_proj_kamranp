import socket

my_ip = socket.gethostname()

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.bind((my_ip, 8000))

connection.listen(1)

while True:
    data = connection.recv(1024)
    print(data)