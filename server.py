import socket
import argparse
import threading

list_clients = []
client_lock = threading.Lock()

def handle_client(client_socket, client_address):
    global list_clients
    
    try:
        client_socket.send("Welcome to this chatroom!").encode('utf-8')
        
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            
            if not data:
                print(f'Client {client_address} disconnected.\n')
                break
            
            print(f'<{client_address}>: {data}')
            
            msg = f'<{client_address}>: {data}'
            
            for client in list_clients:
                if client != client_socket:
                    try:
                        client.send(msg.encode('utf-8'))
                    except:
                        print(f'Error sending message to {client_address}.')
                        print(f'Ending connection with {client_address}.\n')
                        
                        client.close()
                        
                        if client in list_clients:
                            list_clients.remove(client)
    except Exception as e:
        print(f'Error handling client {client_address}: {e}\n')
    finally:
        client_socket.close()
        
        if client in list_clients:
            list_clients.remove(client)
        
        print(f'Connection with {client_address} closed.')   
        print(f"Number of connected clients: {list_clients.len()}\n")
        
        if list_clients.len() < 1:
            print("Waiting for connection...\n")
        
def start_server(addr='localhost', port=12345):
    global list_clients
    
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((addr, port))
        server_socket.listen(10)
        
        print(f'Server is listening on port {addr}:{port}...')
        print("\nWaiting for connection...\n")
        
        while True:
            client_socket, client_address = server_socket.accept()
            
            with client_lock:
                list_clients.append(client_socket)
            
            print(f'<{client_address}> connected.')
            
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    except Exception as e:
        print(f'Server error: {e}')
    finally:
        server_socket.close()
        print("Server shutdown.")

def parse_argument():
    parser = argparse.ArgumentParser(description="TCP Server")
    parser.add_argument('--addr', type=str, default='localhost', help="Server address (default: localhost)")
    parser.add_argument('--port', type=int, default=12345, help="Server port (default: 12345)")

    return parser.parse_args()

def configure_with_input():
    addr = input("Enter server address (default 'localhost'): ") or 'localhost'
    port = input("Enter server port (default 12345): ")
    port = int(port) if port else 12345
    
    return addr, port

if __name__ == '__main__':
    args = parse_argument()
    
    if args.addr == 'localhost' and args.port == 12345:
        addr, port = configure_with_input()
    else:
        addr, port = args.addr, args.port
        
    start_server(addr=addr, port=port)