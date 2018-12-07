import psutil as ps
import numpy as np
import csv
import sys
import time
import datetime
import requests
import shlex
import subprocess
class sysParam:
	Timestamp=[]
	power_values = []
	def __init__(self,sample):
		self.X=np.zeros((sample,23))

	no_values = 0
	def gatherData(self,i):
		info=[]
		now=datetime.datetime.now()
		self.Timestamp.append("{}:{}:{}".format(now.hour,now.minute,now.second))
		ps.cpu_percent()
		cpuT=ps.cpu_times()
		cpuStats=ps.cpu_stats()
		info.append(ps.cpu_freq()[0]) #cpu current frequency
		vmem=ps.virtual_memory()
		swapmem=ps.swap_memory()
		diskUsage=ps.disk_usage('/')
		diskIO=ps.disk_io_counters()
		nwIO=ps.net_io_counters()
		info.append(len(ps.net_connections())) #no. of network connections 
		time.sleep(0.7)
		
		ccpuT=ps.cpu_times()
		info.append(ccpuT[0]-cpuT[0]) # time spent for user in 1 sec
		info.append(ccpuT[2]-cpuT[2]) # time spent for system in 1 sec
		info.append(ccpuT[3]-cpuT[3]) # time spent doing nothing IDLE in 1 sec
		info.append(ccpuT[4]-cpuT[4]) # time spent io wait in 1 sec

		info.append(ps.cpu_percent())#cpu percentage
		currentStats=ps.cpu_stats()
		info.append(currentStats[0]-cpuStats[0]) #ctx switches
		info.append(currentStats[1]-cpuStats[1])#interrupts
		info.append(currentStats[2]-cpuStats[2]) # sw interrupts
		info.append(currentStats[3]-cpuStats[3]) #System calls
		cvmem=ps.virtual_memory()
		info.append(abs(cvmem[2]-vmem[2]))#percent virtual memory
		info.append(abs(cvmem[8]-vmem[8]))#cached memory changed
		info.append(abs(cvmem[9]-vmem[9]))#shared memory changed

		cswapmem=ps.swap_memory()
		info.append(abs(cswapmem[3]-swapmem[3])) # Swap % usage includes total,used swap
		info.append(abs(cswapmem[4]-swapmem[4])) # Swap in bytes- reprsentation of page fault 			
		info.append(abs(cswapmem[5]-swapmem[5])) #Swap out bytes- representation of page fault
				
		info.append(abs(ps.disk_usage('/')[1]-diskUsage[1]))
		cdiskIO=ps.disk_io_counters()
		info.append(cdiskIO[2]-diskIO[2]) # number of bytes read
		info.append(cdiskIO[3]-diskIO[3]) #number of bytes write
		
		cnwIO=ps.net_io_counters()
		info.append(cnwIO[0]-nwIO[0]) #number of bytes sent
		info.append(cnwIO[1]-nwIO[1]) #number of bytes receive
		
		info.append(len(ps.pids())) # number of processes
	        #print(info)
		r = requests.post('http://130.65.159.84:5000/api/predict',json = [{'cpu_frequency' : info[0], \
								        'no_network_connections' : info[1], \
								        'time_spent_user' : info[2],\
								        'time_spent_system' : info[3], 'time_spent_idle': info[4], 'time_spent_io' : info[5],\
									'cpu_percentage' : info[6],\
									'ctx_switches' : info[7],\
									'interrupts' : info[8],\
									'software_interrupts' : info[9],\
									'system_calls' : info[10],\
									'percent_virtual_memory' : info[11],\
									'cached_memory_changed' : info[12],\
									'shared_memory_changed' : info[13],\
									'swap_percentage' : info[14],\
									'swap_in_bytes' : info[15],\
									'swap_out_bytes' : info[16],\
									'bytes_read' : info[17],\
									'bytes_write' : info[18],\
									'bytes_sent' : info[19],\
									'bytes_received' : info[20],\
									'no_processes' : info[21],\
									'rapl_value' : info[22] }])

		
		#print(r.status_code)
		power_predicted = r.json()['power'][0][0]
		threshold_power = 115.7
		print(power_predicted)
		if len(self.power_values) > 10:
			median_power = sorted(self.power_values[:-12:-1])[-6]
			# print("median power", median_power)
			if median_power   > threshold_power:
				output = subprocess.call(shlex.split('./redis_script.sh redis2'))
				print(output)
		self.power_values.append(power_predicted)
	
	def saveData(self, filename):
		filen=open(filename,'wt')
		fw=csv.writer(filen)
		fw.writerow(self.power_values)
		# np.save(filename2,self.X)
		
		# print(self.X)
	
def main():
		
	sysObj=sysParam(int(sys.argv[1]))
	for i in range(int(sys.argv[1])):
		sysObj.gatherData(i)
	sysObj.saveData(sys.argv[2])


if __name__=="__main__":
	main()




########first arigv = duration in second , second - filename for timestamp .csv ,third - filename for system .npy
