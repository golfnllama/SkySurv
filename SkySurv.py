import os
import re
import argparse
###################################################################
# AUTHOR: Eddie Romito
# DATE: 11/16/2015
#
# PURPOSE: Basic script to calculate how often a device issues probe 
#   	   requests for 802.11 access points. 
#
# NOTE: It is NOT required to put the wireless capture card into
#       monitor mode in order to use this script
####################################################################

# command line arguement definition, including optional arguements and default values
parser = argparse.ArgumentParser()
parser.add_argument("target_mac", help="MAC address traffic to capture")
parser.add_argument("-i", "--interface", default='wlan0', help="Capture interface")
parser.add_argument("-c", "--count", default=5, help="How many iterations of scanning to complete")
parser.add_argument("-t", "--duration", default=20, help="How long each capture will run in seconds")
args = parser.parse_args()

# ensure that a proper MAC address is entered
if re.match('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', args.target_mac):
	averages = []

	while (args.count > 0):
		# collect probe requests from user specified MAC addresses. User can also define the capture interface, and the duration of the capture
		# -t e changes the time stamp to epoch time, and the output file is overwritten every time the command is run
		# only the time stamp is written to the file
		os.system("sudo tshark -i %s -I -f 'subtype probereq and ether host %s' -a duration:%s 2>/dev/null -t e | awk '{print $2;}' > tshark-data.txt" % (args.interface, args.target_mac, args.duration))
	
		count = 0
		total = 0

		# read the file with tshark output
                file = open("tshark-data.txt","r")

		# begin by reading the first line of the file
                last_line = file.readline()

		# iterate through file subtracting the next time from the previous time to find an average time between probe requests
                for line in file:
                        dif = float(line) - float(last_line)
                       if dif > 0.5:
                        	total = total + dif
                        	last_line = line
                        	count = count + 1
                file.close()
	
		# prevent division by zero and inform user that no data was collected
		if count > 0:
			average = total/count
			print "\tSub Average (in seconds): ", average
			averages.append(average)
		else:
			print "\tERROR: No data present in the %s second scan" % args.duration

		args.count = int(args.count) - 1

	# calculate the final average 
	finals = 0
	for value in averages:
		finals = finals + value
	final_avg = finals/len(averages)

	print "\n\tFinal Average (in seconds): ", final_avg
	
else:
    print "ERROR: Please check that the MAC address was entered correctly"


