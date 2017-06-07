
# USE IT ON YOUR OWN RISK 
This script takes a list of IPs/hostame in a CSV file and create corresponding devices in PRTG.The script checks first if the device exists in PRTG before adding it. It also starts monitoring on each added device. The script generates an Excel file wwith a summary of devices which have been added into PRTG.

# REQUIREMENTS
This script is developed and test in Python 2.7.13. 
The python package "xlsxwriter" (https://pypi.python.org/pypi/XlsxWriter) shall be installed.
# HOW TO USE IT

Here is an example : 

--> python import_devices.py test.csv http://10.49.88.248 prtgadmin 2076032290 3229 3264

- test.csv : the file wich contains comma sperated IPs/Hostnames to add
- http://10.49.88.248 : The URL of your PRTG Core server
- prtgadmin : your PRTG's account username
- 2076032290: your PRTG's account passhash
- 3229 : the ID of the group to which you would like to add devices
- 3264 : the ID of the device which will be used as a template for new devices




