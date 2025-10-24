#######################################################################################
# Yourname:
# Your student ID:
# Your GitHub Repo: 

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder

import ansible_final
import restconf_final
import netconf_final
import netmiko_final
import sendtexttowebex

#######################################################################################
# 2. Assign the Webex accesssetx WEBEX_TOKEN "OGFmNzY3MjMtMzM5OS00MTYwLThkM2QtYTBmN2EzZGQ4YmQ1YTA1YWFkNzktMDRh_PS65_e37c9b35-5d15-4275-8997-b5c6f91a842d"

ACCESS_TOKEN = os.environ["token"]

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = (
    "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vYmQwODczMTAtNmMyNi0xMWYwLWE1MWMtNzkzZDM2ZjZjM2Zm"
)

last_message_id = None  # เก็บ ID ของข้อความล่าสุดที่เราอ่านแล้ว
student_system = {}     # เก็บ system ของแต่ละ student_id

while True:
    time.sleep(1)

    getParameters = {"roomId": roomIdToGetMessages, "max": 1}
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )

    if r.status_code != 200:
        raise Exception(f"Incorrect reply from Webex Teams API. Status code: {r.status_code}")

    messages = r.json().get("items", [])
    if not messages:
        continue

    message = messages[0]
    message_id = message["id"]
    message_text = message["text"].strip()

    if not message_text.startswith("/66070007"):
        continue

    if message_id == last_message_id:
        continue

    print("Received message:", message_text)
    last_message_id = message_id

    # แยกข้อความ
    parts = message_text.lstrip("/").split()
    student_id = parts[0]
    output = parts[1]

    if output in ["restconf", "netconf", "showrun", "gigabit_status"]:
        # แบบที่ 1: /student_id restconf หรือ netconf
        if len(parts) == 2 and parts[1].lower() in ["restconf", "netconf"]:
            system = parts[1].lower()
            student_system[student_id] = system
            print(student_system)
            sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, f"OK: {system.capitalize()}")
            continue
            # กรณี 3: /student_id showrun|gigabit_status
        elif len(parts) == 2 and parts[1].lower() in ["showrun", "gigabit_status"]:
            command = parts[1].lower()
            router_ip = None
            # เรียกฟังก์ชันตาม command
            if command == "showrun":
                responseMessage, ansible_output = ansible_final.showrun(router_ip, student_id)
                if responseMessage == "fuck":
                    # ถ้า responseMessage เป็น "fuck" จะไม่ทำอะไร (หรือจะแสดงข้อความเฉพาะก็ได้)
                    print("Response is 'fuck' — ไม่ส่งไฟล์ไป Webex")
                    
                else:
                    # เขียนผลลัพธ์ลงไฟล์ใหม่
                    filename = f"{student_id}_running_config.txt"
                    myfile = f"{student_id}_runningconfig_router.txt"
                    with open(filename, "w") as f:
                        f.write(ansible_output)

                    # เปิดไฟล์เพื่อแนบส่งไป Webex
                    with open(myfile, "rb") as f:
                        fileobject = f.read()

                    # เตรียม multipart form สำหรับส่งไฟล์ไป Webex

                    myfile = f"{student_id}_runningconfig_router.txt"
                    postData = MultipartEncoder(
                        fields={
                            "roomId": roomIdToGetMessages,
                            "text": f"show running config",
                            "files": (myfile, fileobject, "text/plain")
                        }
                    )

                    HTTPHeaders = {
                        "Authorization": f"Bearer {ACCESS_TOKEN}",
                        "Content-Type": postData.content_type
                    }

                    #ส่งไฟล์ไป Webex
                    response = requests.post(
                        "https://webexapis.com/v1/messages",
                        data=postData,
                        headers=HTTPHeaders
                    )

                    print(f"ส่งไฟล์ {filename} ไปยัง Webex เรียบร้อยแล้ว ")
            elif command == "gigabit_status":
                status_text = netmiko_final.gigabit_status()  # ดึงสถานะ interfaces

                # ส่งข้อความกลับ Webex
                postData = json.dumps({
                    "roomId": roomIdToGetMessages,
                    "text": f"{status_text}"
                })

                HTTPHeaders = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                }

                response = requests.post(
                    "https://webexapis.com/v1/messages",
                    data=postData,
                    headers=HTTPHeaders
                )

                if response.status_code == 200:
                    print("Status sent to Webex!")
                else:
                    print("Failed to send message:", response.text)
                continue
    if len(parts) == 2:
        system = student_system.get(student_id)
        if system == "restconf" or system == "netconf":
            if parts[1] not in ["10.0.15.61", "10.0.15.62", "10.0.15.63", "10.0.15.64", "10.0.15.65"]:
                sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, "Error: No IP specified")
            elif parts[1] not in ["create", "delete", "enable", "disable", "status"]:
                sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, "Error: No command found. ")
        else:
            sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, "Error: No method specified")
    # แบบที่ 2: /student_id router_ip command
    if len(parts) >= 3:
        router_ip = parts[1]
        command = parts[2].lower()

        # ดึง system ที่เก็บไว้
        system = student_system.get(student_id)
        if not system:
            sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, 
                "Error: system not set. Please send /student_id restconf or /student_id netconf first."
            )
            continue
        
        if system == "restconf":
            if command == "create":
                restconf_final.create(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN)
            elif command == "delete":
                restconf_final.delete(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN)
            elif command == "enable":
                restconf_final.enable(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN)
            elif command == "disable":
                restconf_final.disable(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN)
            elif command == "status":
                restconf_final.status(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN)

        elif system == "netconf":
            if command == "create":
                netconf_final.create(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN)
            elif command == "delete":
                netconf_final.delete(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN)
            elif command == "enable":
                netconf_final.enable(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN)
            elif command == "disable":
                netconf_final.disable(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN)
            elif command == "status":
                netconf_final.status(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN)

        
        
        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail

    
