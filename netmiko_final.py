from netmiko import ConnectHandler
from pprint import pprint

device_ip = "10.0.15.63"
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",  # IOS XE ใช้ cisco_ios
    "ip": device_ip,
    "username": username,
    "password": password,
    "conn_timeout": 30,
    "banner_timeout": 30,
    "auth_timeout": 30,
    "global_delay_factor": 2,
    "fast_cli": False
}

def gigabit_status():
    try:
        print(f"🔌 Connecting to router {device_ip} ...")
        with ConnectHandler(**device_params) as ssh:
            ssh.send_command("terminal length 0", expect_string=r"#")

            output = ssh.send_command("show ip interface brief", use_textfsm=True)
            print(type(output))  # debug
            print(output)        # debug

            up = down = admin_down = 0
            ans_list = []

            # ถ้า TextFSM ใช้ไม่ได้ → แปลงแบบ manual
            if isinstance(output, str):
                lines = output.splitlines()
                for line in lines:
                    if "GigabitEthernet" in line:
                        cols = line.split()
                        iface, status = cols[0], cols[-1]
                        ans_list.append(f"{iface} {status}")
                        if status == "up":
                            up += 1
                        elif status == "down":
                            down += 1
                        elif "administratively down" in line:
                            admin_down += 1
            else:
                for intf in output:
                    if "GigabitEthernet" in intf['interface']:
                        ans_list.append(f"{intf['interface']} {intf['status']}")
                        if intf['status'] == "up":
                            up += 1
                        elif intf['status'] == "down":
                            down += 1
                        elif intf['status'] == "administratively down":
                            admin_down += 1

            summary = f"-> {up} up, {down} down, {admin_down} administratively down"
            return ", ".join(ans_list) + " " + summary

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return str(e)
