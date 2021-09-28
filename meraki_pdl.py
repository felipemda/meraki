"""
This is a Python 3 script to fix a problem with conversion from cotermination licensing to per device licensing for
more than 500 devices

Don't use this script in an organization with mix of licenses, for example: some access-points with enterprise license
and others with advanced license
Don't use this script after adding more licenses after covert from cotermination to per device license
"""

import requests, json

### SECTION: GLOBAL VARIABLES: MODIFY TO CHANGE SCRIPT BEHAVIOUR

api_path = "https://api.meraki.com/api/v1/organizations"
orgId = "INSERT ORGANIZATION ID HERE" ### INSERT ORGANIZATION ID HERE
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Cisco-Meraki-API-Key": "INSERT API KEY HERE" ### INSERT API KEY HERE
}

### SECTION: PRODUCT EDITION: MODIFY TO CHANGE SCRIPT BEHAVIOUR

mr_level = "INSERT LICENSE LEVEL HERE 'ENT' OR 'MR-ADV'"
ms_390_level = "INSERT LICENSE LEVEL HERE 'ENT' OR 'ADV'"
mx_level = "INSERT LICENSE LEVEL HERE 'ENT' OR 'SEC'"

def findUnusedLicenses(deviceType):

    resp = requests.request("GET", url=f"{api_path}/{orgId}/licenses", headers=headers)
    licenses = json.loads(resp.text)

    for license in licenses:
        if license["licenseType"] == deviceType:
            if license["deviceSerial"] == None:
                id = license["id"]

    return id


def findUnlicensedDevices():

    r = requests.request("GET", url=f"{api_path}/{orgId}/inventoryDevices", headers=headers)
    devices = json.loads(r.text)
    unlicensedDevices = {}

    for device in devices:
        if device["licenseExpirationDate"] == None:
            if "MR" in device["model"]:
                unlicensedDevices[device["serial"]] = mr_level
            elif "MX" in device["model"]:
                unlicensedDevices[device["serial"]] = (f"{device['model']}-{mx_level}")
            elif "MS390" in device["model"]:
                unlicensedDevices[device["serial"]] = (f"{device['model']}-{ms_390_level}")
            else:
                unlicensedDevices[device["serial"]] = device["model"]

    return unlicensedDevices

def addLicense(licenseId, deviceSerial):

    payload = json.dumps({
      "deviceSerial": deviceSerial
    })

    response = requests.request("PUT", url=f"{api_path}/{orgId}/licenses/{licenseId}", headers=headers, data=payload)

    return response

def main():

    devices = findUnlicensedDevices()

    for key, value in devices.items():
        license = findUnusedLicenses(value)
        print(f"Assinging license {license} to device {value} with SN {key} - {addLicense(license, str(key))}")

    return


if __name__ == "__main__":
    main()
