import socket

HOST = "0.0.0.0"  # Listen on all network interfaces
PORT = 8080  # Koyeb expects a service to be listening

def start_health_check():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"Health check running on port {PORT}")

        while True:
            conn, addr = server.accept()
            conn.sendall(b"HTTP/1.1 200 OK\n\nBot is running")
            conn.close()

if __name__ == "__main__":
    start_health_check()
