import requests
import json

def send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, status_text):
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

    if response.status_code == 200 or response.status_code == 201:
        print("Status sent to Webex!")
    else:
        print("Failed to send message:", response.text)
