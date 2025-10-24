import os
import sys
from netmiko import ConnectHandler
import textfsm
import io

# ตรวจสอบ argument
if len(sys.argv) < 2:
    print("Error: No command provided")
    sys.exit(1)

parts = sys.argv[1].split()

if len(parts) < 3:
    print("Error: invalid command format")
    sys.exit(1)

student_id = parts[0]
host = parts[1]
command_type = parts[2]

# ถ้าเป็นคำสั่ง motd
if command_type == "motd":
    if len(parts) > 3:
        # --- MODE: SET MOTD ---
        motd_message = " ".join(parts[3:])

        # เขียน hosts ไฟล์ชั่วคราว
        with open("hosts", "w") as f:
            f.write(f"{host} ansible_user=admin ansible_password=cisco ansible_network_os=cisco.ios.ios\n")

        # รัน playbook ตั้งค่า MOTD
        os.system(
            f"ansible-playbook -i hosts motd_playbook.yml "
            f"--extra-vars \"message_from_command='{motd_message}'\" "
            f"--ssh-extra-args='-o HostKeyAlgorithms=+ssh-rsa -o KexAlgorithms=+diffie-hellman-group14-sha1'"
        )
        print("Ok: success")

    else:
        # --- MODE: SHOW MOTD ---
        device = {
            "device_type": "cisco_ios",
            "ip": host,
            "username": "admin",
            "password": "cisco"

        }

        try:
            net_connect = ConnectHandler(**device)
            output = net_connect.send_command("show running-config | include banner motd")
            net_connect.disconnect()

            # ใช้ TextFSM parse ข้อความ
            template_str = """Value MOTD (.+)
Start
  ^banner motd \^C${MOTD}\^C -> Record
"""
            fsm = textfsm.TextFSM(io.StringIO(template_str))
            parsed = fsm.ParseText(output)

            if parsed:
                print(parsed[0][0])
            else:
                print("Error: No MOTD Configured")

        except Exception as e:
            print(f"Error: {str(e)}")
