import os
import sys
from netmiko import ConnectHandler
import textfsm
import io

if len(sys.argv) < 2:
    print("Error: No command provided")
    sys.exit(1)

parts = sys.argv[1].split()
if len(parts) < 3:
    print("Error: Invalid command format")
    sys.exit(1)

student_id = parts[0]
host = parts[1]
command_type = parts[2]

# --- SET MOTD ---
if command_type == "motd" and len(parts) > 3:
    motd_message = " ".join(parts[3:])
    with open("hosts", "w") as f:
        f.write(f"{host} ansible_user=admin ansible_password=cisco ansible_network_os=cisco.ios.ios\n")
    ret = os.system(
        f"ansible-playbook -i hosts motd_playbook.yml "
        f"--extra-vars \"message_from_command='{motd_message}'\" "
        f"--ssh-extra-args='-o HostKeyAlgorithms=+ssh-rsa -o KexAlgorithms=+diffie-hellman-group14-sha1'"
    )
    if ret == 0:
        print("Ok! Success")
    else:
        print("Error: Failed to set MOTD")

# --- GET MOTD ---
elif command_type == "motd" and len(parts) == 3:
    device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": "admin",
        "password": "cisco",
        "secret": "cisco",
    }

    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()
        output = net_connect.send_command("show running-config | include banner motd")
        net_connect.disconnect()

        template_str = """
Value MOTD
Start
  ^banner motd \^C${MOTD}\^C -> Record
"""
        template = io.StringIO(template_str)
        fsm = textfsm.TextFSM(template)
        parsed = fsm.ParseText(output)

        if parsed:
            print(parsed[0][0])
        else:
            print("No MOTD Configured")

    except Exception as e:
        print(f"Error: {str(e)}")

else:
    print("Error: Unknown command format")
