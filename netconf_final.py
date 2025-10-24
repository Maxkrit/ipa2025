from ncclient import manager
import xmltodict

import sendtexttowebex

def create(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN):

    
    netconf_config = f"""
    <config>
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <interface>
                <Loopback>
                    <name>{student_id}</name>
                    <description>Created via NETCONF</description>
                </Loopback>
            </interface>
        </native>
    </config>
    """


    try:
        # ใช้ router_ip ที่ส่งเข้ามา
        with manager.connect(
            host=router_ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
        ) as m:
            netconf_reply = m.edit_config(target='running', config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, "Loopback created successfully by netconf")
    except Exception as e:
        sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, f"Error: {e}")



def delete(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN):
    netconf_config = f"""
    <config>
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <interface>
                <Loopback operation="delete">
                    <name>{student_id}</name>
                </Loopback>
            </interface>
        </native>
    </config>
    """


    try:
        # ใช้ router_ip ที่ส่งเข้ามา
        with manager.connect(
            host=router_ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
        ) as m:
            netconf_reply = m.edit_config(target='running', config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, "Loopback delete successfully by netconf")
    except Exception as e:
        sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, f"Error: {e}")


def enable(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN):
    # ลบ shutdown เพื่อ enable interface
    netconf_config = f"""
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback{student_id}</name>
                <enabled>true</enabled>
            </interface>
        </interfaces>
    </config>
    """

    try:
        # ใช้ router_ip ที่ส่งเข้ามา
        with manager.connect(
            host=router_ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
        ) as m:
            netconf_reply = m.edit_config(target='running', config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, "Loopback enabled successfully by netconf")
    except Exception as e:
        sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, f"Error: {e}")

def disable(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN):
    netconf_config = f"""
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback{student_id}</name>
                <enabled>false</enabled>
            </interface>
        </interfaces>
    </config>
    """

    try:
        # ใช้ router_ip ที่ส่งเข้ามา
        with manager.connect(
            host=router_ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
        ) as m:
            netconf_reply = m.edit_config(target='running', config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, "Loopback disable successfully by netconf")
    except Exception as e:
        sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, f"Error: {e}")

def netconf_edit_config(router_ip, netconf_config):
    try:
        with manager.connect(
            host=router_ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
        ) as m:  # m ถูกสร้างที่นี่
            netconf_reply = m.edit_config(target="running", config=netconf_config)
            return netconf_reply.xml
    except Exception as e:
        return f"Error: {e}"



def status(student_id, router_ip, roomIdToGetMessages, ACCESS_TOKEN):
    interface_name = f"Loopback{student_id}"
    netconf_filter = f"""
    <filter>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>{interface_name}</name>
            </interface>
        </interfaces>
    </filter>
    """

    try:
        with manager.connect(
            host=router_ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
        ) as m:
            netconf_reply = m.get(netconf_filter)
            netconf_dict = xmltodict.parse(netconf_reply.xml)

            interface_data = (
                netconf_dict.get('rpc-reply', {})
                .get('data', {})
                .get('interfaces', {})
                .get('interface')
            )
            print(interface_data)
            if interface_data:
                aenabled_status = interface_data.get('enabled', 'false')

                print(aenabled_status)
                if aenabled_status == 'true':
                    status_text = "up"
                elif aenabled_status == 'false':
                    status_text = "administratively down"
                else:
                    status_text = "down"

                sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, f"Interface {interface_name} is {status_text}")
            else:
                sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, f"No interface {interface_name}")

    except Exception as e:
        sendtexttowebex.send_message_webex(roomIdToGetMessages, ACCESS_TOKEN, f"Error: {e}")
