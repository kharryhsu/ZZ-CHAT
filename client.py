import socket
import argparse
import threading
import sys

def client_write(client_socket, client_lock):
    while True:
        try:
            msg = input()
            
            if not msg.strip():
                continue
            
            if msg.lower() == 'exit':
                client_socket.send(msg.encode('utf-8'))
                print("Closing connection.")
                client_socket.close()
                break

            with client_lock:
                sys.stdout.write(f'<You>: {msg}\n')
                sys.stdout.write("> ")
                sys.stdout.flush()

            client_socket.send(msg.encode('utf-8'))
            msg = ""
        except Exception as e:
            print(f"Error sending data: {e}")
            break
        
def client_read(client_socket, client_lock):
    while True:
        try:
            data = client_socket.recv(2048).decode('utf-8')
            
            if not data:
                print("Server closed the connection.")
                break
            
            with client_lock:
                sys.stdout.write(f'\r{data}\n')
                sys.stdout.write(f"> ")
                sys.stdout.flush()
        except (ConnectionAbortedError, ConnectionResetError):
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

def start_client(addr='localhost', port=12345):
    try:
        print(f'Connecting to server at {addr}:{port}')
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((addr, port))
        
        print(f'Connected to server at {addr}:{port}')
        
        client_lock = threading.Lock()
        
        read_thread = threading.Thread(target=client_read, args=(client_socket, client_lock))
        read_thread.start()
        
        write_thread = threading.Thread(target=client_write, args=(client_socket, client_lock))
        write_thread.start()
        
        read_thread.join()
        write_thread.join()
        
    except ConnectionRefusedError:
        print(f"Connection failed. Is the server running at {addr}:{port}?")
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        client_socket.close()
        print("Client connection closed.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="TCP Client")
    parser.add_argument('--addr', type=str, default='localhost', help="Server address (default: localhost)")
    parser.add_argument('--port', type=int, default=12345, help="Server port (default: 12345)")
    
    return parser.parse_args()

def configure_with_input():
    addr = input("Enter server address (default 'localhost'): ") or 'localhost'
    port = input("Enter server port (default 12345): ")
    port = int(port) if port else 12345
    
    return addr, port

if __name__ == "__main__":
    args = parse_arguments()
    
    if args.addr == 'localhost' and args.port == 12345:
        addr, port = configure_with_input()
    else:
        addr, port = args.addr, args.port
    
    start_client(addr=addr, port=port)