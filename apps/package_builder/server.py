import socketserver
import json
import time
import sys
import os
from packages_builder import build_package

PORT = 1111
HOST = '127.0.0.1'

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"Connected by {self.client_address}")
        data = b""
        while True:
            try:
                chunk = self.request.recv(4096)
                if not chunk:
                    break
                data += chunk
                # Simple loose JSON detection/heuristic could go here if needed, 
                # but relying on client closing write end (shutdown) or short messages is common for simple tasks.
            except ConnectionResetError:
                break
        
        if not data:
            return

        try:
            packet = json.loads(data.decode('utf-8'))
            print("Received packet, building package...")
            
            # Benchmarking
            start_time = time.time()
            result = build_package(packet)
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            print(f"Package built in {duration_ms:.2f} ms")

            response = json.dumps(result).encode('utf-8')
            self.request.sendall(response)
            print("Response sent.")
        except json.JSONDecodeError as e:
            error_msg = f"Error decoding JSON: {e}"
            print(error_msg)
            self.request.sendall(json.dumps({"error": error_msg}).encode('utf-8'))
        except Exception as e:
            error_msg = f"Error processing packet: {e}"
            print(error_msg)
            self.request.sendall(json.dumps({"error": error_msg}).encode('utf-8'))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def main():
    # Allow address reuse
    socketserver.TCPServer.allow_reuse_address = True
    with ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler) as server:
        print(f"Threaded Server listening on {HOST}:{PORT}")
        server.serve_forever()

if __name__ == "__main__":
    main()
