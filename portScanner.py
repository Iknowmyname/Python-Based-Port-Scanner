import socket
import datetime
import threading

def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            banner = sock.recv(1024).decode().strip()
            print(f"Port {port} is open: {banner}")
        sock.close()
    except socket.error:
        pass

def display_banner():
    print("********************************************")
    print("*              PORT SCANNER                 *")
    print("********************************************")
    print()

def port_scanner():
    display_banner()
    
    host = input("Enter the target host to scan: ")
    start_port = int(input("Enter the starting range of port: (min-0)"))
    end_port = int(input("Enter the ending range of port: (max-65536"))
    print("\nScanning in progress...\n")
    
    start_time = datetime.datetime.now()
    
    threads = []
    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=scan_port, args=(host, port))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    
    print(f"\nScan completed at {end_time}")
    print(f"Scan duration: {total_time}")

port_scanner()
