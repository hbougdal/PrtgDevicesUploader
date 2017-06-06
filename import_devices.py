
# -*- coding: utf-8 -*-

 
import sys
import json
import csv
import re
import xlsxwriter
#import urllib.request
import urllib2
import urllib

#PRTG API FUNCTIONS
API_DUPLICATE_FCT = "/api/duplicateobject.htm"
API_RESUME_FCT   = "/api/pause.htm"
API_GET_DEVICES_OF_A_GROUP_FCT = "/api/table.json"


def addDevices(csv_path, url_coreserver, username, passhash,id_of_target_group, id_of_device_to_clone):

	if (("http" not in url_coreserver) and ("https" not in url_coreserver)):
		url_coreserver = "https://"+url_coreserver

	auth_data = "&username="+username+"&passhash="+passhash
	
	
	#Get the list of devices which are already member of the group 
	resp = get_group_devices(id_of_target_group, url_coreserver, auth_data)
	#print (resp.__dict__)
	res = json.loads(resp.read().decode('utf8'))
	existing_hosts = []
	for item in res["devices"]: 
		existing_hosts.append(item["host"])
	
	#print(existing_hosts[1])
	

	#Query 
	url= url_coreserver + API_DUPLICATE_FCT 
	
	devices = csv_reader(csv_path)

	if(devices is None) : 
		write_logs ("Error while trying top open/read the CSV file.")
	else : 
		result = []
		
		for host in devices : 
			if(host in existing_hosts): 
				result.append([host, "no", "", "Device exist already in PRTG"])
				write_logs("Skipped : device "+host+" exist already in PRTG.")
				
			else : 
				write_logs("Trying to add device "+host+" to PRTG....")
				parameters = "id="+id_of_device_to_clone+"&name="+host+"&host="+host+"&targetid="+id_of_target_group
				api_call = url + "?" + parameters + auth_data

				try:

					response = urllib2.urlopen(api_call, timeout=15)
					#print(response.__dict__)

					res = urllib.unquote(response.url).decode('utf8')

					if (response.code == 200) : 
						m = re.search('(?<=device.htm.id=)\d+', res)
						deviceID = m.group(0)
						
						if(deviceID != ""): 
							res = resumeObject(deviceID, url, auth_data, host)
							result.append([host, "yes", res, ""])
							write_logs("Device "+host+" has been added in PRTG.")

						else : 
							result.append([host, "no", "no", ""])
							write_logs("Could not add device "+host+" to PRTG.")
								
					else : 

						result.append([host, "no", "no", ""])
						write_logs("Error while trying to add device : "+host)

				except urllib2.URLError, e: 
					
					print(e.__dict__)
					write_logs("HTTP Error while trying to add device "+host + " : "+e.reason)
					result.append([host, "no", "no", ""])

		printSummary(result) #print a summary to the console
		write_to_xls(result) #generate an XL file


def resumeObject(objectid, url, auth_data, host): 

	api_fct = API_RESUME_FCT + "?" +"id="+objectid+"&action=1"+auth_data
	req = url + api_fct
	try:
		response = urllib2.urlopen(req, timeout=15)

		if(response.code == 200) : 
			write_logs("Monitoring has been resumed for " + host)
			return "yes"
		else : 
			write_logs("Monitoring could not be resumed for " + host)
			return "no"
	except: 
		write_logs("Monitoring could not be resumed for " + host)
		return "no"


def write_to_xls(result): 
	# Create a workbook and add a worksheet.
	workbook = xlsxwriter.Workbook('result.xlsx')
	worksheet = workbook.add_worksheet()

	# Start from the first cell. Rows and columns are zero indexed.
	row = 0
	col = 0

	#Write headers
	worksheet.write(row, 0, "Device")
	worksheet.write(row, 1, "Added ?")
	worksheet.write(row, 2, "Being monitored ?")
	worksheet.write(row, 3, "Comment")
	row += 1

	# Iterate over the data and write it out row by row.
	for item in result:
		worksheet.write(row, 0, item[0])
		worksheet.write(row, 1, item[1])
		worksheet.write(row, 2, item[2])
		worksheet.write(row, 3, item[3])
		row += 1

def write_logs(msg):
	print("---------> "+msg+"\n")

def get_group_devices(groupID, url, auth_data):

	api_fct = API_GET_DEVICES_OF_A_GROUP_FCT + "?" +"content=devices&output=json&columns=objid,group,device,host&count=100000&id="+groupID+""+auth_data
	req = url + api_fct

	#try:
	response = urllib2.urlopen(req, timeout=15)

	if(response.code == 200) : 
		return response
	else : 
		return None
	#except: 
		#return None
def printSummary(result):

	added_count     = 0
	monitored_count = 0
	skipped_count = 0
	for item in result: 
		if (item[1] == "yes"): 
			added_count += 1
			if(item[2] == "yes"): 
				monitored_count += 1
				
		if(item[3] != ""): 
			skipped_count +=1

	print("----------------------------------Summary--------------------------------")
	print("Number of devices added to PRTG              : "+str(added_count))    
	print("Number of devices added and being monitored  : "+str(monitored_count))
	print("Number of devices skipped (exist already)    : "+str(skipped_count))
	print("-------------------------------------------------------------------------")
	


def csv_reader(csv_path):

	try :  
		file_obj = open(csv_path, "rb")
		reader = csv.reader(file_obj)
		devices = []
		for row in reader : 
			for item in row :
				devices.append(item)

		return devices
	except : 
		return None

if __name__ == "__main__":
   
    if(len(sys.argv) < 7):
    	print ("-------------------------This script takes 6 arguments ------------------------"+"\n")
    	print (" csv_path              --- path of a csv file, which contains IPs or Hostnames devices you want to add to PRTG."+"\n")
    	print (" url_coreserver        --- IP address or hostname of the Core server of your PRTG installation."+"\n")
    	print (" username              --- username of your PRTG account."+"\n")
    	print (" passhash              --- passhash of your PRTG account."+"\n")
    	print (" id_of_target_group    --- ID of the PRTG parent group, in which the devices will be added."+"\n")
    	print (" id_of_device_to_clone --- ID of the PRTG template device, which will be used a template for the devices which will be added."+"\n")

    else : 

    	csv_path       = sys.argv[1]
    	url_coreserver = sys.argv[2] 
    	username       = sys.argv[3]
    	passhash       = sys.argv[4]
    	id_of_target_group    = sys.argv[5]
    	id_of_device_to_clone = sys.argv[6]

    	addDevices(csv_path, url_coreserver, username, passhash,id_of_target_group, id_of_device_to_clone)


    	



    
