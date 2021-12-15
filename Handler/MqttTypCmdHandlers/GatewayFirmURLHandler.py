from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db


class GatewayFirmURLHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        mqttReceiveCommandResponse = {
            "RQI": data.get("RQI"),
            "Rsp": 0
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))
        self.__handler_cmd_update_firmware()

    def __handler_cmd_update_firmware(self, data):
        import subprocess
        import os
        import time

        print("Start update firmware ...")
        try:
            os.system('opkg update')
            os.system('pip3 install packaging')
            os.system('opkg update')
            os.system('opkg upgrade tar')
            file = open("/etc/version.txt", "r")
            current_ver = file.read().strip()
            print(f"Current version: {current_ver}")
            file.close()
            from packaging import version

            lastest_ver = data[-1]
            print(lastest_ver)
            lastest_ver_name = lastest_ver.get('NAME')
            print(lastest_ver_name)

            if version.parse(lastest_ver_name) > version.parse(current_ver):
                link = lastest_ver.get('URL')
                file_name = link[link.rfind('/')+1:]
                link_dl = "wget " + link
                os.system(link_dl)

                process = subprocess.Popen(['sha256sum', f'{file_name}'],
                                            stdout=subprocess.PIPE,
                                            universal_newlines=True)
                output = process.stdout.readline()
                src = output.strip()
                check_sum = lastest_ver.get('CHECK_SUM') + "  " + file_name
                if src == check_sum:
                    os.system(f'tar -xf {file_name}')

                    # move old file to dir /etc/RECOVERY
                    os.system('mv HcStreetLight/ /etc/RECOVERY')
                    os.system('mv *.so /etc/RECOVERY')
                    os.system('mv version.txt /etc/RECOVERY')
                    os.system(f'rm {file_name}')

                    # move new file to dir root
                    os.system(f'mv /root/{lastest_ver_name}/* /root/')
                    os.system(f'rm -r {lastest_ver_name}/')

                    # handle condition version required

                    file = open("version.txt", "r")
                    str_ver = file.read().strip()
                    list_vers = str_ver.split('-')
                    print(list_vers)
                    file.close()

                    # required list version
                    req_list_vers = [] 
                    for ver in list_vers:
                        if version.parse(ver) > version.parse(current_ver):
                            req_list_vers.append(ver)
                    print(req_list_vers)

                    for req_ver in req_list_vers:
                        for d in data:
                            if req_ver == d.get('NAME'):
                                # if req_ver == lastest_ver_name:
                                #     print("Pass")
                                # else:
                                link_sub = d.get('URL')
                                file_sub_name = link_sub[link_sub.rfind('/')+1:]
                                link_sub_dl = "wget " + link_sub
                                os.system(link_sub_dl)

                                process = subprocess.Popen(['sha256sum', f'{file_sub_name}'],
                                                            stdout=subprocess.PIPE,
                                                            universal_newlines=True)
                                output = process.stdout.readline()
                                src = output.strip()
                                print(src)
                                check_sum = d.get('CHECK_SUM') + "  " + file_sub_name
                                print(check_sum)
                                if src == check_sum:
                                    print("Start install sub-version")
                                    os.system(f'tar -xf {file_sub_name}')

                                    # move old file to dir /etc/RECOVERY
                                    os.system('rm -r /etc/RECOVERY/*')
                                    os.system('mv HcStreetLight/ /etc/RECOVERY')
                                    os.system('mv *.so /etc/RECOVERY')
                                    os.system('mv version.txt /etc/RECOVERY')
                                    os.system(f'rm {file_sub_name}')

                                    # move new file to dir root
                                    os.system(f'mv /root/{req_ver}/* /root/')
                                    os.system(f'rm -r {req_ver}/')

                                    # delete /etc/RECOVERY
                                    os.system('rm -r /etc/RECOVERY/*')

                                    file = open("/etc/version.txt", "w")
                                    file.write(req_ver)
                                    file.close()

                    time.sleep(4)
                    os.system('reboot -f')
        except:
            print("Update firmware error !")
