import os
import sys
import json
import socket
import time
import subprocess
import nmap
import adbutils
import subprocess
from datetime import datetime
from pathlib import Path
import system_kit

ADB_LOG_FILE = Path("./config/sys_logs/adb_syslog.txt")
scanned_devices = Path("./config/json_files/net_devs.json")
#-------------------------------------------------------------------------#

####################### ADB Connection Section ############################

#-------------------------------------------------------------------------#

def main():


    while True:
        menu=f"""    
        [                                     0. Exit]
        [scan | connect | disconnect | devices | xdroid | clear | exit] \n
        [Main Menu] Enter selection >>> """ 
        input_menu = system_kit.sf_spacing(menu)
        option = input(input_menu).lower()
        match option:
            case "0"|"exit":
                print(f'\n\t[Info] Exiting ADB Server.....\n\n', end='')
                time.sleep(1)
                break

            case "1"|"scan":
                network_scan()
            case "2"|"connect":
                xconnect()
            case "3"|"disconnect":
                main_disconnect()
            case "4"|"devices":
                main_list_devices()
            case other:
                print(f"\n\t[X] Invalid selection\n\tPlease enter a valid option on menu above\n")
                time.sleep(3)




def xconnect():
    try:
        phone_ip = get_adb_android_ip("-d")
        start_debugging_server()
        if phone_ip is None:
            return
        connect_to_wireless(phone_ip)
    except:
        connect()

#------------------------ Auto IP Selection ------------------------------#

def check_if_ip(possible_ip: str) -> bool:
    
    ip_parts = possible_ip.split(".")
    try:
        [int(part) for part in ip_parts]
        if len(ip_parts) == 4:
            return True

    except:
        time.sleep(0.8)
        print(f"\t[Info] Auto Connect >> Failed ! >> No USB Connection\n")
        time.sleep(1.2)
        print(f"\t<< Going User input mode ")
        time.sleep(2.4)

    return False


def get_adb_android_ip(connection_type_flag: str | None = None):
    """
    connection_type_flag is either -d for usb of -e for ip
    Not yet:
        or -s ip:port to specif port
    """

    ip_args = ["adb"]
    if connection_type_flag is not None:
        ip_args += [connection_type_flag]
    ip_args += ["shell", "ip", "route"]
    ret = run_adb_command(ip_args, capture_output=True)  # only uses usb
    if "device unauthorized" in ret.stderr.decode():
        print("try pairing the device first")
        return
    possible_ip = ret.stdout.decode().strip().split(" ")[-1]
    is_ip = check_if_ip(possible_ip)
    if is_ip == True:
        return possible_ip
    else:
        raise ValueError



def write_log(message: str):
    ADB_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ADB_LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {message}\n")



def run_adb_command(command: list[str]):
    write_log(f"EXECUTING: {' '.join(command)}")
    result = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    for line in result.stdout.splitlines():
        line = line.rstrip()
        if line:
            write_log(line)

    write_log(f"COMMAND FINISHED WITH CODE {result.returncode}")

    return result.returncode

def connect_to_wireless(ip: str, port: str | int = "5555"):
    
    port = str(port)

    if ip is None:
        return

    print(f"\n\t[Info]  Device Found >> {ip}\n")
    run_adb_command(["adb", "kill-server"])
    run_adb_command(["adb", "start-server"])
    print('\t[Info] Restarting adb server ......\n')
    time.sleep(0.8)
    print('\t[Info] Connecting.....\n')
    time.sleep(1.2)
    run_adb_command(["adb", "connect", f"{ip}:{port}"])
    auto_con_devices = adbutils.adb.device_list()
    connected = False

    for d in auto_con_devices:
        auto_con_dev = d.serial

        if auto_con_dev.count(".") == 3:
            connected = True
            break

    if connected:
        print("\t[✔]  Connection Successfull\n")
        print(f'\t[Info] Connected to {ip} on port {port}\n')
        write_log(f"SUCCESSFULLY CONNECTED TO {ip}:{port}")
    else:
        print("\t[X] Connection Failed")
        write_log(f"FAILED TO CONNECT TO {ip}:{port}")



def start_debugging_server():
    try:
        result = run_adb_command(["adb", "-d", "tcpip", "5555"],capture_output=True,text=True,check=True)
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"COMMAND FAILED, maybe try pairing? Error: {e.stderr.strip()}")

#------------------------ User IP Selection ----------------------------------#


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def scan_network():
    
    net_devs_ip = {}
    count = 0
    print("\n\t[Info] Scanning network ......\n")
    time.sleep(1.2)
    try:
        ip = get_ip_address()
        ip += "/24"
        scanner = nmap.PortScanner()
        scanner.scan(hosts=ip, arguments="-sn")
    
        for host in scanner.all_hosts():

            if scanner[host]["status"]["state"] == "up":

                try:
                    if len(scanner[host]["vendor"]) == 0:
                        socket.gethostbyaddr(host)[0]
                    else:
                        scanner[host]['vendor']
                        socket.gethostbyaddr(host)[0]
                except:
                    scanner[host]['vendor']
                count = count+1
                while True:
                    if count < 10:
                        net_devs_ip[count] = host
                        with open(scanned_devices, 'w') as f:
                            json.dump(net_devs_ip, f, indent=count)
                    break
    except:

        net_devs_ip = {"0": "0.0.0.0"}
        with open(scanned_devices, 'w') as f:
            json.dump(net_devs_ip, f)
        raise ConnectionError

    print("\n") 

def network_scanner():
    try:
        scan_network()
    except:
        time.sleep(1.2)
        print("\n\tNetwork is unreachable \n")
        time.sleep(1.2)
        try:
            print("\n\t Retrying ......... \n")
            time.sleep(0.8)
            scan_network()

        except:
            time.sleep(1.2)
            print("\n\tNetwork is unreachable \n")
            time.sleep(1.2)
   
            try:
                print("\n\tRetrying ......... \n")
                time.sleep(0.8)
                scan_network()
            except:
                time.sleep(1.2)
                print("\n\tNetwork is unreachable \n")
                time.sleep(1.2)
                print("""
                    \n\t[Please Check your network connection before retrying]\n 
                    \n\t<< Going Back to Main Menu  \n
                    """)
                time.sleep(2.4)
                
def network_scan():
    network_scanner()
    
    with open(scanned_devices, 'r') as dev_ips:
        data = json.load(dev_ips)
        print("\t[+] Scanned Devices\n\t-----------------------\n")
        try:
            for dev_key in data:
                for dev_addr in [data[dev_key]]:
                    if dev_addr == "0.0.0.0":
                        print("\t[No Device Found]\n")
                    else:
                        raise ValueError
        except:
            for dev_key in data:
                for dev_addr in [data[dev_key]]:
                    print(f"\t[{dev_key}]. {dev_addr}")
            print("\n")


def connect():

    network_scanner()    
    with open(scanned_devices, 'r') as dev_ips:
        data = json.load(dev_ips)
        try:
            for key in data:
                for ip in [data[key]]:
                    if ip == "0.0.0.0":
                        print(f"\t[-] Scanned Devices\n\t-----------------------\n")
                        print(f"\t\t[No Device Found]\n")
                    else:
                        raise ValueError
        except:
            print(f"\t[+] Scanned Devices\n\t-----------------------\n")
            for key in data:
                for ip in [data[key]]:
                    print(f"\t[{key}]. {ip}")
            print("\n")
            ip_input=input(f"\t[IP-select] Enter selection >>> ").lower()
            match ip_input:
                case ip_input:
                    try:
                        if data[ip_input].count(".") == 3:
                            print(f"\t[Info] Selected Device >> {data[ip_input]}\n")
                            run_adb_command(["adb", "kill-server"])
                            run_adb_command(["adb", "start-server"])
                            print(f'\t[Info] Restarting adb server ......\n')
                            time.sleep(0.8)
                            print(f'\t[Info] Connecting.....\n')
                            time.sleep(1.2)
                            run_adb_command(["adb", "connect", f"{data[ip_input]}:{5555}"]) 
                            con_devices = adbutils.adb.device_list()
                            if len(con_devices) != 0:  
                                time.sleep(0.8)
                                print(f"\n\t[✔]  Connection Successfull\n")
                                print(f'\t[Info] Connected to {data[ip_input]} on port 5555\n\n')
                            else:
                                print(f"\t[X] Connection Failed\n")  
                        else:
                            time.sleep(0.8)
                            print(f"\n\tInvalid IP Address\n\t<< Going back to Main Menu")
                    except:
                        if ip_input == '':
                            time.sleep(0.8)
                            print(f"\n\tNull Input | No selection made\n\t<< Going back to Main Menu")
                        else:
                            time.sleep(0.8)
                            print(f"\t[X]    Device IP Not Found\n\t<< Going back to Main Menu")


def list_devices():
    print(f'\n\tInfo] Scanning for connected devices.....')
    time.sleep(1.2)
    adb_device_scanner()

def main_list_devices():
    
    
    print(f'\n\t[Info] Scanning for connected devices.....')
    time.sleep(1.2)
    
    
    adb_device_scanner()
    

def adb_device_scanner():

    con_devices_list = adbutils.adb.device_list()
    if len(con_devices_list) == 0:
        print(f"\n\t[-] Connected Devices\n\t-----------------------\n")
        print(f"\t  [No Device Found]\n")
    else:

        for d in con_devices_list:
            con_dev = d.serial
            net_device_info =f"""
            Device            : {d.prop.device}
            Serial ip:port    : {d.serial}
            Device Model      : {d.prop.model}
            Device Name       : {d.prop.name}
            """
            net_device_display = system_kit.sf_spacing(net_device_info)
            if con_dev.count(".") != 3:
                print(f"\t[+] ADB USB Connection\n    -----------------------")
                print(net_device_display)
            elif con_dev.count(".") == 3:
                print(f"\n\t[+] ADB WiFi Connection \n\t-----------------------")
                print(net_device_display)

def disconnect():
    con_devices = adbutils.adb.device_list()    
    if len(con_devices) == 0:
        print(f"\n\t[No Device Connected]\n")
    else:
        try:
            run_adb_command(["adb", "disconnect"], capture_output=True)
            print(f'\n\t[Info] Disconnecting ......\n')
            time.sleep(1.2)
            print(f"\t[Info] All Devices/Emulators Disconnected\n")
        except:
            print(f'\n\t[Info]Error occured while trying to disconnect\n')


def main_disconnect():
    try:
        run_adb_command(["adb", "disconnect"], capture_output=True)        
        print(f'\t[Info] Disconnecting ......\n')
        time.sleep(1.2)
        print(f"\t[Info] All Devices/Emulators Disconnected\n")
    except:
        print(e)
        print(f"\t[Info]Error occured while trying to disconnect\n")  
if __name__ == "__main__":
    main()