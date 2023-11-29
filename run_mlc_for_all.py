#!/usr/bin/python3
#!/usr/bin/python
########################################################################
#                                                                      #
#                                                                      #
# PURPOSE: A script for Genoa&SPR Platform MLC test                    #
#                                                                      #
# Please install python3 and pip3 before the test                      #
#                                                                      #
#                                                                      #
# VERSION: 2.0                                                         #
# Added Intel 4 & 8 sockets system support                             #
# Added MLC v3.10                                                      #
#                                                                      #
# Author: Peter Xu                                                     #
#                                                                      #
########################################################################

import subprocess
import sys
import importlib

# Check and install required module
def install(package):
   # subprocess.check_call([sys.executable, "-m", "ensurepip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade","pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_python_module():
    packages = ['numpy','matplotlib','urllib','shutil','os','datetime']
    for package in packages:
        try:
            package = importlib.import_module(package)
        except ModuleNotFoundError as e:
            install(package)

check_python_module()

#refresh sys.path
import site
from importlib import reload
reload(site)


import shutil
import os
from urllib import request
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

print("This script works for multiple numa setting configurations listed below")
supported_configs='''
1: For 1 Socket with NPS4/SNC4
2: For 2 Sockets with NPS1/SNC Disabled
3: For 2 Sockets with NPS2/SNC2
4: For 2 Sockets with NPS4/SNC4
5: For 4 Sockets with NPS1/SNC Disabled
6: For 4 Sockets with NPS2/SNC2
7: For 4 Sockets with NPS4/SNC4
8: For 8 Sockets with NPS1/SNC Disabled
9: For 8 Sockets with NPS2/SNC2
10: For 8 Sockets with NPS4/SNC4
'''
print(supported_configs)
numa_type=input("Please choose a number base on your configuration:")

print("\n")

if int(numa_type) not in range(1,11):
   print("The configure you choose is not in the support list, please doublecheck the input number and rerun the script.")
   sys.exit()

def is_numactl_installed(a_print_result=True):
    try:
        numa_node_count = int(subprocess.check_output("numactl --hardware | grep 'available:' | awk '{print $2}'", shell=True))
        if a_print_result:
            print('numactl is installed.')
        return True
    except:
        if a_print_result:
            print('numactl is NOT installed.')
        return False

def get_numa_node_count():
    if is_numactl_installed(False):
        return int(subprocess.check_output("numactl --hardware | grep 'available:' | awk '{print $2}'", shell=True))
    else:
        print('numactl must be installed for get_numa_node_count.')
        sys.exit(1)

def get_socket_count():
    return int(subprocess.check_output("lscpu | grep 'Socket(s):' | awk '{print $2}'", shell=True))



def check_mlc_file():
     if not os.path.exists('mlc'):
        print("Can't find mlc in the current direcotry")
        return False
     else:
        return True 

def check_root_privileges():
    if os.geteuid()!=0:
        return False
    else:
        return True

def install_mlc():
    print("Two MLC version are avalible")
    support_mlc_versions='''
    1: mlc_v3.9a
    2: mlc_v3.10
    '''
    print(support_mlc_versions)
    MLC_VERSION=input("Please choose the version you want to use, 1 for v3.9a, 2 for v3.10: ")
    print("\n")

    if MLC_VERSION == "1":
        #URL="https://www.intel.com/content/dam/develop/external/us/en/documents/mlc_v3.9a.tgz"
        URL="https://downloadmirror.intel.com/736634/mlc_v3.9a.tgz"
        Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')

        try:
            response = request.urlretrieve(URL,"mlc.tgz")
            print(response)
            print("File download")
            if os.path.isdir("mlcv3.9a"):
                target = str(os.getcwd()) + '/' + 'mlcv3.9a' + '_' + str(Current_Time)
                os.rename("mlcv3.9a",target)
            os.mkdir("mlcv3.9a")
            shutil.move("mlc.tgz","mlcv3.9a")
            os.chdir("./mlcv3.9a")
            subprocess.check_output("tar -xzvf mlc.tgz", shell=True)
            os.chdir("Linux")
            print("mlc installation is done")    
            return True
        except:
            print("Something wrong, please check network and install mlc manually")
            return False
    elif MLC_VERSION == "2":
        URL="https://downloadmirror.intel.com/763324/mlc_v3.10.tgz"
        Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')

        try:
            response = request.urlretrieve(URL,"mlc.tgz")
            print(response)
            print("File download")
            if os.path.isdir("mlcv3.10"):
                target = str(os.getcwd()) + '/' + 'mlcv3.10' + '_' + str(Current_Time)
                os.rename("mlcv3.10",target)
            os.mkdir("mlcv3.10")
            shutil.move("mlc.tgz","mlcv3.10")
            os.chdir("./mlcv3.10")
            subprocess.check_output("tar -xzvf mlc.tgz", shell=True)
            os.chdir("Linux")
            print("mlc installation is done")    
            return True
        except:
            print("Something wrong, please check network and install mlc manually")
            return False
    else:
        print("Please choose the correct number to download the MLC")

def check_for_requirements():
        if not is_numactl_installed():
            sys.exit("numactl is required but not found! Exiting.\n")
        if not check_root_privileges():
            sys.exit("Root privileages is required, please switch to root user")
        if not check_mlc_file():
            print("Try to install mlc")
            install_mlc()  

     

#check_for_requirements()

#print out the output immediately 
def run_shell(shell):
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=sys.stdout, universal_newlines=True, shell=True, bufsize=1)

    cmd.communicate()
    return cmd.returncode

def run_mlc():
    Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    if check_mlc_file():
        subprocess.check_output("echo 8000 > /proc/sys/vm/nr_hugepages", shell=True)
        subprocess.check_output("modprobe msr", shell=True)
        if os.path.exists('mlc_data'):
            target = str(os.getcwd()) + '/' + 'mlc_data' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_data",target)
        vendor=str(subprocess.check_output("lscpu | grep ^Vendor",shell=True))
        if "AMD" in vendor:
            print(run_shell("./mlc | tee mlc_data"))
        elif "Intel" in vendor:
            def generate_go_mlc_sh():
                result = '''#!/bin/bash
            date 
            echo 
            echo Executing Intel Memory Latency Checker...
            ./mlc --latency_matrix 
            ./mlc --peak_injection_bandwidth 
            ./mlc --bandwidth_matrix 
            ./mlc --loaded_latency 
            ./mlc --latency_matrix -X -Y
            ./mlc --peak_injection_bandwidth -X -Y
            ./mlc --bandwidth_matrix -X -Y
            ./mlc --latency_matrix -X -Z
            ./mlc --peak_injection_bandwidth -X -Z
            ./mlc --bandwidth_matrix -X -Z
            echo 
            echo 
            numactl -H 
            echo 
            echo 
            dmidecode --type 17
                
                '''
                return result
            if not os.path.exists('go_mlc.sh'):
                file = open('go_mlc.sh','w')
                go_mlc_txt = generate_go_mlc_sh()
                file.write(go_mlc_txt)
                file.close()
            subprocess.check_output("chmod u+x go_mlc.sh", shell=True)
            print(run_shell("./go_mlc.sh | tee mlc_data"))
        else:
            print("The CPU is not supported")
        print("mlc test is done, checking the result now")

#run_mlc()

#data treatment
def data_treatment():

    def run_1s4numa():
        lat = []
        count = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate latency data
                if line.strip().startswith("0"):
                    break
                count +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count,count+4):
                lat_line=lines[i].strip().split()[1:]
                lat_line=list(map(float,lat_line))
                lat.append(lat_line)
            #print(lat)

        #calculate local node
        local_node = np.diagonal(lat)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_latency="Local Node Memory Latency (Low-Avg-High) is " + str(local_low) + "-" + str(local_mean) + "-" + str(local_high)+" ns"
        print(local_node_latency)

        #calculate near local node
        matrix = np.array(lat)
        #remove diagonal items
        near_local_node = matrix[~np.eye(matrix.shape[0],dtype=bool)].reshape(matrix.shape[0],-1)
        #print(near_local_node)
        near_local_high = np.max(near_local_node)
        near_local_low = np.min(near_local_node)
        near_local_mean = round(np.mean(near_local_node),1)
        near_local_node_latency="Near Local Node Memory Latency (Low-Avg-High) is " + str(near_local_low) + "-" + str(near_local_mean) + "-" + str(near_local_high)+" ns"
        print(near_local_node_latency)


        bw = []
        count_2 = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate bandwith data
                if line.strip().startswith("0") and count_2 > 10:
                    break
                count_2 +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count_2,count_2+4):
                bw_line=lines[i].strip().split()[1:]
                bw_line=list(map(float,bw_line))
                bw.append(bw_line)


        #calculate local node
        local_node_bw = np.diagonal(bw)
        #print(local_node)
        local_high_bw =  max(local_node_bw)
        local_low_bw = min(local_node_bw)
        local_mean_bw = round(sum(local_node_bw)/len(local_node_bw),1)
        local_node_bandwith="Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(local_low_bw/1000,1)) + "-" + str(round(local_mean_bw/1000,1)) + "-" + str(round(local_high_bw/1000,1))+" GB/s"
        print(local_node_bandwith)

        #calculate near local node
        #remove diagonal items

        matrix_bw = np.array(bw)
        near_local_node_bw = matrix_bw[~np.eye(matrix_bw.shape[0],dtype=bool)].reshape(matrix_bw.shape[0],-1)
        #print(near_local_node)
        near_local_high_bw = np.max(near_local_node_bw)
        near_local_low_bw = np.min(near_local_node_bw)
        near_local_mean_bw = round(np.mean(near_local_node_bw),1)
        near_local_node_bandwith="Near Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(near_local_low_bw/1000,1)) + "-" + str(round(near_local_mean_bw/1000,1)) + "-" + str(round(near_local_high_bw/1000,1))+" GB/s"
        print(near_local_node_bandwith)

        

        with open("mlc_data","r") as f:
            for line in f.readlines():
                if line.startswith("ALL Reads"):
                    value=float(line.strip().split(":")[1])/1000
                    all_reads_speed="ALL Reads speed is " + str(round(value,2))+" GB/s"
                    print(all_reads_speed)
                if line.startswith("3:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_3_1="3:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_3_1)
                if line.startswith("2:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_2_1="2:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_2_1)
                if line.startswith("1:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_1_1="1:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_1_1)   
                if line.startswith("Stream-triad like"):
                    value=float(line.strip().split(":")[1])/1000
                    stream_triade_like_speed="Stream_triad like speed is " + str(round(value,2))+" GB/s"
                    print(stream_triade_like_speed)
        
        if os.path.exists("mlc_spv_data_1s4numa.log"):
            Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            target = str(os.getcwd()) + '/' + 'mlc_spv_data_1s4numa' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_spv_data_1s4numa.log",target) 
        #redirect 'print' output to a file
        sys.stdout=open("mlc_spv_data_1s4numa.log","w")
        print(local_node_latency)
        print(near_local_node_latency)
        print(local_node_bandwith)
        print(near_local_node_bandwith)
        print(all_reads_speed)
        print(r_w_3_1)
        print(r_w_2_1)
        print(r_w_1_1)
        print(stream_triade_like_speed)
        sys.stdout.close()
        subprocess.call("cp mlc_data mlc_data_1s4numa", shell=True)

    def run_2s2numa():
        lat = []
        count = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate latency data
                if line.strip().startswith("0"):
                    break
                count +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count,count+2):
                lat_line=lines[i].strip().split()[1:]
                lat_line=list(map(float,lat_line))
                lat.append(lat_line)
            #print(lat)

        #calculate local node
        local_node = np.diagonal(lat)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_latency="Local Node Memory Latency (Low-Avg-High) is " + str(local_low) + "-" + str(local_mean) + "-" + str(local_high)+" ns"
        print(local_node_latency)

        #calculate near local node
        matrix = np.array(lat)

        #calculate remote node
        remote_node_1 = matrix[1:2,0:1]
        #print(remote_node_1)
        remote_node_2 = matrix[0:1,1:2]
        #print(remote_node_2)
        remote_node = np.vstack((remote_node_1,remote_node_2))
        #print(remote_node)
        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = round(np.mean(remote_node),1)
        remote_node_latency="Remote Node Memory Latency (Low-Avg-High) is " + str(remote_low) + "-" + str(remote_mean) + "-" + str(remote_high)+" ns"
        print(remote_node_latency)

        bw = []
        count_2 = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate bandwith data
                if line.strip().startswith("0") and count_2 > 10:
                    break
                count_2 +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count_2,count_2+2):
                bw_line=lines[i].strip().split()[1:]
                bw_line=list(map(float,bw_line))
                bw.append(bw_line)


        #calculate local node
        local_node_bw = np.diagonal(bw)
        #print(local_node)
        local_high_bw =  max(local_node_bw)
        local_low_bw = min(local_node_bw)
        local_mean_bw = round(sum(local_node_bw)/len(local_node_bw),1)
        local_node_bandwith="Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(local_low_bw/1000,1)) + "-" + str(round(local_mean_bw/1000,1)) + "-" + str(round(local_high_bw/1000,1))+" GB/s"
        print(local_node_bandwith)

        matrix_bw = np.array(bw)
        #calculate remote node
        remote_node_1_bw = matrix_bw[1:2,0:1]
        #print(remote_node_1)
        remote_node_2_bw = matrix_bw[0:1,1:2]
        #print(remote_node_2)
        remote_node_bw = np.vstack((remote_node_1_bw,remote_node_2_bw))
        #print(remote_node)
        remote_high_bw = np.max(remote_node_bw)
        remote_low_bw = np.min(remote_node_bw)
        remote_mean_bw = round(np.mean(remote_node_bw),1)
        remote_node_bandwith="Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(remote_low_bw/1000,1)) + "-" + str(round(remote_mean_bw/1000,1)) + "-" + str(round(remote_high_bw/1000,1))+" GB/s"
        print(remote_node_bandwith)

        with open("mlc_data","r") as f:
            for line in f.readlines():
                if line.startswith("ALL Reads"):
                    value=float(line.strip().split(":")[1])/1000
                    all_reads_speed="ALL Reads speed is " + str(round(value,2))+" GB/s"
                    print(all_reads_speed)
                if line.startswith("3:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_3_1="3:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_3_1)
                if line.startswith("2:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_2_1="2:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_2_1)
                if line.startswith("1:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_1_1="1:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_1_1)   
                if line.startswith("Stream-triad like"):
                    value=float(line.strip().split(":")[1])/1000
                    stream_triade_like_speed="Stream_triad like speed is " + str(round(value,2))+" GB/s"
                    print(stream_triade_like_speed)


        if os.path.exists("mlc_spv_data_2s2numa.log"):
            Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            target = str(os.getcwd()) + '/' + 'mlc_spv_data_2s2numa' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_spv_data_2s2numa.log",target) 
        #redirect 'print' output to a file
        sys.stdout=open("mlc_spv_data_2s2numa.log","w")
        print(local_node_latency)
        print(remote_node_latency)
        print(local_node_bandwith)
        print(remote_node_bandwith)
        print(all_reads_speed)
        print(r_w_3_1)
        print(r_w_2_1)
        print(r_w_1_1)
        print(stream_triade_like_speed)
        sys.stdout.close()
        subprocess.call("cp mlc_data mlc_data_2s2numa", shell=True)

    def run_2s4numa():
        lat = []
        count = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate latency data
                if line.strip().startswith("0"):
                    break
                count +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count,count+4):
                lat_line=lines[i].strip().split()[1:]
                lat_line=list(map(float,lat_line))
                lat.append(lat_line)
            #print(lat)

        #calculate local node
        local_node = np.diagonal(lat)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_latency="Local Node Memory Latency (Low-Avg-High) is " + str(local_low) + "-" + str(local_mean) + "-" + str(local_high)+" ns"
        print(local_node_latency)

        #calculate near local node
        matrix = np.array(lat)

        near_local_node_1 = matrix[0:2,0:2]
        #print(near_local_node_1)
        near_local_node_2 = matrix[2:4,2:4]
        #print(near_local_node_2)

        #remove local node from list
        m = near_local_node_1.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out1 = near_local_node_1.ravel()[idx]
        #print(out1)

        m = near_local_node_2.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out2 = near_local_node_2.ravel()[idx]
        #print(out2)

        near_local_node = np.vstack((out1,out2))
        #print(near_local_node)
        near_local_high = np.max(near_local_node)
        near_local_low = np.min(near_local_node)
        near_local_mean = round(np.mean(near_local_node),1)
        near_local_node_latency="Near Local Node Memory Latency (Low-Avg-High) is " + str(near_local_low) + "-" + str(near_local_mean) + "-" + str(near_local_high)+" ns"
        print(near_local_node_latency)


        #calculate remote node
        remote_node_1 = matrix[2:4,0:2]
        #print(remote_node_1)
        remote_node_2 = matrix[0:2,2:4]
        #print(remote_node_2)
        remote_node = np.vstack((remote_node_1,remote_node_2))
        #print(remote_node)
        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = round(np.mean(remote_node),1)
        remote_node_latency="Remote Node Memory Latency (Low-Avg-High) is " + str(remote_low) + "-" + str(remote_mean) + "-" + str(remote_high)+" ns"
        print(remote_node_latency)

        bw = []
        count_2 = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate bandwith data
                if line.strip().startswith("0") and count_2 > 10:
                    break
                count_2 +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count_2,count_2+4):
                bw_line=lines[i].strip().split()[1:]
                bw_line=list(map(float,bw_line))
                bw.append(bw_line)


        #calculate local node
        local_node_bw = np.diagonal(bw)
        #print(local_node)
        local_high_bw =  max(local_node_bw)
        local_low_bw = min(local_node_bw)
        local_mean_bw = round(sum(local_node_bw)/len(local_node_bw),1)
        local_node_bandwith="Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(local_low_bw/1000,1)) + "-" + str(round(local_mean_bw/1000,1)) + "-" + str(round(local_high_bw/1000,1))+" GB/s"
        print(local_node_bandwith)

        #calculate near local node
        matrix_bw = np.array(bw)

        near_local_node_1_bw = matrix_bw[0:2,0:2]
        #print(near_local_node_1)
        near_local_node_2_bw = matrix_bw[2:4,2:4]
        #print(near_local_node_2)

        #remove local node from list
        m = near_local_node_1_bw.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out1 = near_local_node_1_bw.ravel()[idx]
        #print(out1)

        m = near_local_node_2_bw.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out2 = near_local_node_2_bw.ravel()[idx]
        #print(out2)

        near_local_node_bw = np.vstack((out1,out2))
        #print(near_local_node)
        near_local_high_bw = np.max(near_local_node_bw)
        near_local_low_bw = np.min(near_local_node_bw)
        near_local_mean_bw = round(np.mean(near_local_node_bw),1)
        near_local_node_bandwith="Near Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(near_local_low_bw/1000,1)) + "-" + str(round(near_local_mean_bw/1000,1)) + "-" + str(round(near_local_high_bw/1000,1))+" GB/s"
        print(near_local_node_bandwith)

        #calculate remote node
        remote_node_1_bw = matrix_bw[2:4,0:2]
        #print(remote_node_1)
        remote_node_2_bw = matrix_bw[0:2,2:4]
        #print(remote_node_2)
        remote_node_bw = np.vstack((remote_node_1_bw,remote_node_2_bw))
        #print(remote_node)
        remote_high_bw = np.max(remote_node_bw)
        remote_low_bw = np.min(remote_node_bw)
        remote_mean_bw = round(np.mean(remote_node_bw),1)
        remote_node_bandwith="Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(remote_low_bw/1000,1)) + "-" + str(round(remote_mean_bw/1000,1)) + "-" + str(round(remote_high_bw/1000,1))+" GB/s"
        print(remote_node_bandwith)

        with open("mlc_data","r") as f:
            for line in f.readlines():
                if line.startswith("ALL Reads"):
                    value=float(line.strip().split(":")[1])/1000
                    all_reads_speed="ALL Reads speed is " + str(round(value,2))+" GB/s"
                    print(all_reads_speed)
                if line.startswith("3:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_3_1="3:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_3_1)
                if line.startswith("2:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_2_1="2:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_2_1)
                if line.startswith("1:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_1_1="1:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_1_1)   
                if line.startswith("Stream-triad like"):
                    value=float(line.strip().split(":")[1])/1000
                    stream_triade_like_speed="Stream_triad like speed is " + str(round(value,2))+" GB/s"
                    print(stream_triade_like_speed)

        if os.path.exists("mlc_spv_data_2s4numa.log"):
            Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            target = str(os.getcwd()) + '/' + 'mlc_spv_data_2s4numa' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_spv_data_2s4numa.log",target) 
        #redirect 'print' output to a file
        sys.stdout=open("mlc_spv_data_2s4numa.log","w")
        print(local_node_latency)
        print(near_local_node_latency)
        print(remote_node_latency)
        print(local_node_bandwith)
        print(near_local_node_bandwith)
        print(remote_node_bandwith)
        print(all_reads_speed)
        print(r_w_3_1)
        print(r_w_2_1)
        print(r_w_1_1)
        print(stream_triade_like_speed)
        sys.stdout.close()
        subprocess.call("cp mlc_data mlc_data_2s4numa", shell=True)

    def run_2s8numa():
        lat = []
        count = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate latency data
                if line.strip().startswith("0"):
                    break
                count +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count,count+8):
                lat_line=lines[i].strip().split()[1:]
                lat_line=list(map(float,lat_line))
                lat.append(lat_line)
            #print(lat)

        #calculate local node
        local_node = np.diagonal(lat)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_latency="Local Node Memory Latency (Low-Avg-High) is " + str(local_low) + "-" + str(local_mean) + "-" + str(local_high)+" ns"
        print(local_node_latency)

        #calculate near local node
        matrix = np.array(lat)

        near_local_node_1 = matrix[0:4,0:4]
        #print(near_local_node_1)
        near_local_node_2 = matrix[4:8,4:8]
        #print(near_local_node_2)

        #remove local node from list
        m = near_local_node_1.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out1 = near_local_node_1.ravel()[idx]
        #print(out1)

        m = near_local_node_2.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out2 = near_local_node_2.ravel()[idx]
        #print(out2)

        near_local_node = np.vstack((out1,out2))
        #print(near_local_node)
        near_local_high = np.max(near_local_node)
        near_local_low = np.min(near_local_node)
        near_local_mean = round(np.mean(near_local_node),1)
        near_local_node_latency="Near Local Node Memory Latency (Low-Avg-High) is " + str(near_local_low) + "-" + str(near_local_mean) + "-" + str(near_local_high)+" ns"
        print(near_local_node_latency)


        #calculate remote node
        remote_node_1 = matrix[4:8,0:4]
        #print(remote_node_1)
        remote_node_2 = matrix[0:4,4:8]
        #print(remote_node_2)
        remote_node = np.vstack((remote_node_1,remote_node_2))
        #print(remote_node)
        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = round(np.mean(remote_node),1)
        remote_node_latency="Remote Node Memory Latency (Low-Avg-High) is " + str(remote_low) + "-" + str(remote_mean) + "-" + str(remote_high)+" ns"
        print(remote_node_latency)

        bw = []
        count_2 = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate bandwith data
                if line.strip().startswith("0") and count_2 > 10:
                    break
                count_2 +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count_2,count_2+8):
                bw_line=lines[i].strip().split()[1:]
                bw_line=list(map(float,bw_line))
                bw.append(bw_line)


        #calculate local node
        local_node_bw = np.diagonal(bw)
        #print(local_node)
        local_high_bw =  max(local_node_bw)
        local_low_bw = min(local_node_bw)
        local_mean_bw = round(sum(local_node_bw)/len(local_node_bw),1)
        local_node_bandwith="Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(local_low_bw/1000,1)) + "-" + str(round(local_mean_bw/1000,1)) + "-" + str(round(local_high_bw/1000,1))+" GB/s"
        print(local_node_bandwith)

        #calculate near local node
        matrix_bw = np.array(bw)

        near_local_node_1_bw = matrix_bw[0:4,0:4]
        #print(near_local_node_1)
        near_local_node_2_bw = matrix_bw[4:8,4:8]
        #print(near_local_node_2)

        #remove local node from list
        m = near_local_node_1_bw.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out1 = near_local_node_1_bw.ravel()[idx]
        #print(out1)

        m = near_local_node_2_bw.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out2 = near_local_node_2_bw.ravel()[idx]
        #print(out2)

        near_local_node_bw = np.vstack((out1,out2))
        #print(near_local_node)
        near_local_high_bw = np.max(near_local_node_bw)
        near_local_low_bw = np.min(near_local_node_bw)
        near_local_mean_bw = round(np.mean(near_local_node_bw),1)
        near_local_node_bandwith="Near Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(near_local_low_bw/1000,1)) + "-" + str(round(near_local_mean_bw/1000,1)) + "-" + str(round(near_local_high_bw/1000,1))+" GB/s"
        print(near_local_node_bandwith)

        #calculate remote node
        remote_node_1_bw = matrix_bw[4:8,0:4]
        #print(remote_node_1)
        remote_node_2_bw = matrix_bw[0:4,4:8]
        #print(remote_node_2)
        remote_node_bw = np.vstack((remote_node_1_bw,remote_node_2_bw))
        #print(remote_node)
        remote_high_bw = np.max(remote_node_bw)
        remote_low_bw = np.min(remote_node_bw)
        remote_mean_bw = round(np.mean(remote_node_bw),1)
        remote_node_bandwith="Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(remote_low_bw/1000,1)) + "-" + str(round(remote_mean_bw/1000,1)) + "-" + str(round(remote_high_bw/1000,1))+" GB/s"
        print(remote_node_bandwith)

        with open("mlc_data","r") as f:
            for line in f.readlines():
                if line.startswith("ALL Reads"):
                    value=float(line.strip().split(":")[1])/1000
                    all_reads_speed="ALL Reads speed is " + str(round(value,2))+" GB/s"
                    print(all_reads_speed)
                if line.startswith("3:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_3_1="3:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_3_1)
                if line.startswith("2:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_2_1="2:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_2_1)
                if line.startswith("1:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_1_1="1:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_1_1)   
                if line.startswith("Stream-triad like"):
                    value=float(line.strip().split(":")[1])/1000
                    stream_triade_like_speed="Stream_triad like speed is " + str(round(value,2))+" GB/s"
                    print(stream_triade_like_speed)

        if os.path.exists("mlc_spv_data_2s8numa.log"):
            Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            target = str(os.getcwd()) + '/' + 'mlc_spv_data_2s8numa' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_spv_data",target) 
        #redirect 'print' output to a file
        sys.stdout=open("mlc_spv_data_2s8numa.log","w")
        print(local_node_latency)
        print(near_local_node_latency)
        print(remote_node_latency)
        print(local_node_bandwith)
        print(near_local_node_bandwith)
        print(remote_node_bandwith)
        print(all_reads_speed)
        print(r_w_3_1)
        print(r_w_2_1)
        print(r_w_1_1)
        print(stream_triade_like_speed)
        sys.stdout.close()
        subprocess.call("cp mlc_data mlc_data_2s8numa", shell=True)


    def run_4s4numa():
        lat = []
        count = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate latency data
                if line.strip().startswith("0"):
                    break
                count +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count,count+4):
                lat_line=lines[i].strip().split()[1:]
                lat_line=list(map(float,lat_line))
                lat.append(lat_line)
            #print(lat)

        #calculate local node
        local_node = np.diagonal(lat)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_latency="Local Node Memory Latency (Low-Avg-High) is " + str(local_low) + "-" + str(local_mean) + "-" + str(local_high)+" ns"
        print(local_node_latency)

        #calculate near local node
        matrix = np.array(lat)
        #remove diagonal items
        remote_node = matrix[~np.eye(matrix.shape[0],dtype=bool)].reshape(matrix.shape[0],-1)
        
        remote_node_high = np.max(remote_node)
        remote_node_low = np.min(remote_node)
        remote_node_mean = round(np.mean(remote_node),1)
        remote_node_latency="Remote Node Memory Latency (Low-Avg-High) is " + str(remote_node_low) + "-" + str(remote_node_mean) + "-" + str(remote_node_high)+" ns"
        print(remote_node_latency)


        bw = []
        count_2 = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate bandwith data
                if line.strip().startswith("0") and count_2 > 10:
                    break
                count_2 +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count_2,count_2+4):
                bw_line=lines[i].strip().split()[1:]
                bw_line=list(map(float,bw_line))
                bw.append(bw_line)


        #calculate local node
        local_node_bw = np.diagonal(bw)
        #print(local_node)
        local_high_bw =  max(local_node_bw)
        local_low_bw = min(local_node_bw)
        local_mean_bw = round(sum(local_node_bw)/len(local_node_bw),1)
        local_node_bandwith="Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(local_low_bw/1000,1)) + "-" + str(round(local_mean_bw/1000,1)) + "-" + str(round(local_high_bw/1000,1))+" GB/s"
        print(local_node_bandwith)

        #calculate near local node
        #remove diagonal items

        matrix_bw = np.array(bw)
        remote_node_bw = matrix_bw[~np.eye(matrix_bw.shape[0],dtype=bool)].reshape(matrix_bw.shape[0],-1)
        
        remote_high_bw = np.max(remote_node_bw)
        remote_low_bw = np.min(remote_node_bw)
        remote_mean_bw = round(np.mean(remote_node_bw),1)
        remote_node_bandwith="Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(remote_low_bw/1000,1)) + "-" + str(round(remote_mean_bw/1000,1)) + "-" + str(round(remote_high_bw/1000,1))+" GB/s"
        print(remote_node_bandwith)

        

        with open("mlc_data","r") as f:
            for line in f.readlines():
                if line.startswith("ALL Reads"):
                    value=float(line.strip().split(":")[1])/1000
                    all_reads_speed="ALL Reads speed is " + str(round(value,2))+" GB/s"
                    print(all_reads_speed)
                if line.startswith("3:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_3_1="3:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_3_1)
                if line.startswith("2:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_2_1="2:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_2_1)
                if line.startswith("1:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_1_1="1:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_1_1)   
                if line.startswith("Stream-triad like"):
                    value=float(line.strip().split(":")[1])/1000
                    stream_triade_like_speed="Stream_triad like speed is " + str(round(value,2))+" GB/s"
                    print(stream_triade_like_speed)
        
        if os.path.exists("mlc_spv_data_4s4numa.log"):
            Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            target = str(os.getcwd()) + '/' + 'mlc_spv_data_4s4numa' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_spv_data_4s4numa.log",target) 
        #redirect 'print' output to a file
        sys.stdout=open("mlc_spv_data_4s4numa.log","w")
        print(local_node_latency)
        print(remote_node_latency)
        print(local_node_bandwith)
        print(remote_node_bandwith)
        print(all_reads_speed)
        print(r_w_3_1)
        print(r_w_2_1)
        print(r_w_1_1)
        print(stream_triade_like_speed)
        sys.stdout.close()
        subprocess.call("cp mlc_data mlc_data_4s4numa", shell=True)

    def run_4s8numa():
        lat = []
        count = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate latency data
                if line.strip().startswith("0"):
                    break
                count +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count,count+8):
                lat_line=lines[i].strip().split()[1:]
                lat_line=list(map(float,lat_line))
                lat.append(lat_line)
            #print(lat)

        #calculate local node
        local_node = np.diagonal(lat)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_latency="Local Node Memory Latency (Low-Avg-High) is " + str(local_low) + "-" + str(local_mean) + "-" + str(local_high)+" ns"
        print(local_node_latency)

        #calculate near local node
        matrix = np.array(lat)

        near_local_node_1 = matrix[0,1]
        near_local_node_2 = matrix[1,0]
        near_local_node_3 = matrix[2,3]
        near_local_node_4 = matrix[3,2]
        near_local_node_5 = matrix[4,5]
        near_local_node_6 = matrix[5,4]
        near_local_node_7 = matrix[6,7]
        near_local_node_8 = matrix[7,6]
        near_local_node = np.array([near_local_node_1,near_local_node_2,near_local_node_3,near_local_node_4,near_local_node_5,near_local_node_6,near_local_node_7,near_local_node_8],dtype=object)

        near_local_high = np.max(near_local_node)
        near_local_low = np.min(near_local_node)
        near_local_mean = round(np.mean(near_local_node),1)
        near_local_node_latency="Near Local Node Memory Latency (Low-Avg-High) is " + str(near_local_low) + "-" + str(near_local_mean) + "-" + str(near_local_high)+" ns"
        print(near_local_node_latency)


    
        #calculate remote node
        remote_node_1 = matrix[2:4,0:2]
        remote_node_2 = matrix[4:6,0:2]
        remote_node_3 = matrix[6:8,0:2]
        remote_node_4 = matrix[0:2,2:4]
        remote_node_5 = matrix[4:6,2:4]
        remote_node_6 = matrix[6:8,2:4]
        remote_node_7 = matrix[0:2,4:6]
        remote_node_8 = matrix[2:4,4:6]
        remote_node_9 = matrix[6:8,4:6]
        remote_node_10 = matrix[0:2,6:8]
        remote_node_11 = matrix[2:4,6:8]
        remote_node_12 = matrix[4:6,6:8]
        

        remote_node = np.vstack((remote_node_1,remote_node_2,remote_node_3,remote_node_4,remote_node_5,remote_node_6,remote_node_7,remote_node_8,remote_node_9,remote_node_10,remote_node_11,remote_node_12))


        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = round(np.mean(remote_node),1)
        remote_node_latency="Remote Node Memory Latency (Low-Avg-High) is " + str(remote_low) + "-" + str(remote_mean) + "-" + str(remote_high)+" ns"
        print(remote_node_latency)

        bw = []
        count_2 = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate bandwith data
                if line.strip().startswith("0") and count_2 > 20:
                    break
                count_2 +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count_2,count_2+8):
                bw_line=lines[i].strip().split()[1:]
                bw_line=list(map(float,bw_line))
                bw.append(bw_line)


        #calculate local node
        local_node_bw = np.diagonal(bw)
        #print(local_node)
        local_high_bw =  max(local_node_bw)
        local_low_bw = min(local_node_bw)
        local_mean_bw = round(sum(local_node_bw)/len(local_node_bw),1)
        local_node_bandwith="Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(local_low_bw/1000,1)) + "-" + str(round(local_mean_bw/1000,1)) + "-" + str(round(local_high_bw/1000,1))+" GB/s"
        print(local_node_bandwith)

        #calculate near local node
        matrix_bw = np.array(bw)


        near_local_node_1_bw = matrix_bw[0,1]
        near_local_node_2_bw = matrix_bw[1,0]
        near_local_node_3_bw = matrix_bw[2,3]
        near_local_node_4_bw = matrix_bw[3,2]
        near_local_node_5_bw = matrix_bw[4,5]
        near_local_node_6_bw = matrix_bw[5,4]
        near_local_node_7_bw = matrix_bw[6,7]
        near_local_node_8_bw = matrix_bw[7,6]
        near_local_node_bw = np.array([near_local_node_1_bw,near_local_node_2_bw,near_local_node_3_bw,near_local_node_4_bw,near_local_node_5_bw,near_local_node_6_bw,near_local_node_7_bw,near_local_node_8_bw],dtype=object)

        #print(near_local_node)
        near_local_high_bw = np.max(near_local_node_bw)
        near_local_low_bw = np.min(near_local_node_bw)
        near_local_mean_bw = round(np.mean(near_local_node_bw),1)
        near_local_node_bandwith="Near Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(near_local_low_bw/1000,1)) + "-" + str(round(near_local_mean_bw/1000,1)) + "-" + str(round(near_local_high_bw/1000,1))+" GB/s"
        print(near_local_node_bandwith)


        remote_node_1_bw = matrix_bw[2:4,0:2]
        remote_node_2_bw = matrix_bw[4:6,0:2]
        remote_node_3_bw = matrix_bw[6:8,0:2]
        remote_node_4_bw = matrix_bw[0:2,2:4]
        remote_node_5_bw = matrix_bw[4:6,2:4]
        remote_node_6_bw = matrix_bw[6:8,2:4]
        remote_node_7_bw = matrix_bw[0:2,4:6]
        remote_node_8_bw = matrix_bw[2:4,4:6]
        remote_node_9_bw = matrix_bw[6:8,4:6]
        remote_node_10_bw = matrix_bw[0:2,6:8]
        remote_node_11_bw = matrix_bw[2:4,6:8]
        remote_node_12_bw = matrix_bw[4:6,6:8]
        
        remote_node_bw = np.vstack((remote_node_1_bw,remote_node_2_bw,remote_node_3_bw,remote_node_4_bw,remote_node_5_bw,remote_node_6_bw,remote_node_7_bw,remote_node_8_bw,remote_node_9_bw,remote_node_10_bw,remote_node_11_bw,remote_node_12_bw))
        #print(remote_node)
        remote_high_bw = np.max(remote_node_bw)
        remote_low_bw = np.min(remote_node_bw)
        remote_mean_bw = round(np.mean(remote_node_bw),1)
        remote_node_bandwith="Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(remote_low_bw/1000,1)) + "-" + str(round(remote_mean_bw/1000,1)) + "-" + str(round(remote_high_bw/1000,1))+" GB/s"
        print(remote_node_bandwith)

        with open("mlc_data","r") as f:
            for line in f.readlines():
                if line.startswith("ALL Reads"):
                    value=float(line.strip().split(":")[1])/1000
                    all_reads_speed="ALL Reads speed is " + str(round(value,2))+" GB/s"
                    print(all_reads_speed)
                if line.startswith("3:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_3_1="3:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_3_1)
                if line.startswith("2:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_2_1="2:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_2_1)
                if line.startswith("1:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_1_1="1:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_1_1)   
                if line.startswith("Stream-triad like"):
                    value=float(line.strip().split(":")[1])/1000
                    stream_triade_like_speed="Stream_triad like speed is " + str(round(value,2))+" GB/s"
                    print(stream_triade_like_speed)

        if os.path.exists("mlc_spv_data_4s8numa.log"):
            Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            target = str(os.getcwd()) + '/' + 'mlc_spv_data_4s8numa' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_spv_data_4s8numa.log",target) 
        #redirect 'print' output to a file
        sys.stdout=open("mlc_spv_data_4s8numa.log","w")
        print(local_node_latency)
        print(near_local_node_latency)
        print(remote_node_latency)
        print(local_node_bandwith)
        print(near_local_node_bandwith)
        print(remote_node_bandwith)
        print(all_reads_speed)
        print(r_w_3_1)
        print(r_w_2_1)
        print(r_w_1_1)
        print(stream_triade_like_speed)
        sys.stdout.close()
        subprocess.call("cp mlc_data mlc_data_4s8numa", shell=True)

    def run_4s16numa():
        lat = []
        count = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate latency data
                if line.strip().startswith("0"):
                    break
                count +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count,count+16):
                lat_line=lines[i].strip().split()[1:]
                lat_line=list(map(float,lat_line))
                lat.append(lat_line)
            #print(lat)

        #calculate local node
        local_node = np.diagonal(lat)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_latency="Local Node Memory Latency (Low-Avg-High) is " + str(local_low) + "-" + str(local_mean) + "-" + str(local_high)+" ns"
        print(local_node_latency)

        #calculate near local node
        matrix = np.array(lat)
        #print(matrix)
        near_local_node_1 = matrix[0:4,0:4]
        #print(near_local_node_1)
        near_local_node_2 = matrix[4:8,4:8]
        #print(near_local_node_2)
        near_local_node_3 = matrix[8:12,8:12]
        #print(near_local_node_3)
        near_local_node_4 = matrix[12:16,12:16]
        #print(near_local_node_4)
    

        #remove local node from list
        m = near_local_node_1.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out1 = near_local_node_1.ravel()[idx]
        #print(out1)

        m = near_local_node_2.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out2 = near_local_node_2.ravel()[idx]
        #print(out2)

        m = near_local_node_3.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out3 = near_local_node_3.ravel()[idx]
        #print(out3)

        m = near_local_node_4.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out4 = near_local_node_4.ravel()[idx]
        #print(out4)


        near_local_node = np.vstack((out1,out2,out3,out4,))
        #print(near_local_node)
        near_local_high = np.max(near_local_node)
        near_local_low = np.min(near_local_node)
        near_local_mean = round(np.mean(near_local_node),1)
        near_local_node_latency="Near Local Node Memory Latency (Low-Avg-High) is " + str(near_local_low) + "-" + str(near_local_mean) + "-" + str(near_local_high)+" ns"
        print(near_local_node_latency)


        #calculate remote node
        remote_node_1 = matrix[4:8,0:4]
        remote_node_2 = matrix[8:12,0:4]
        remote_node_3 = matrix[12:16,0:4]
        remote_node_4 = matrix[0:4,4:8]
        remote_node_5 = matrix[8:12,4:8]
        remote_node_6 = matrix[12:16,4:8]
        remote_node_7 = matrix[0:4,8:12]
        remote_node_8 = matrix[4:8,8:12]
        remote_node_9 = matrix[12:16,8:12]
        remote_node_10 = matrix[0:4,12:16]
        remote_node_11 = matrix[4:8,12:16]
        remote_node_12 = matrix[8:12,12:16]
        
        remote_node = np.vstack((remote_node_1,remote_node_2,remote_node_3,remote_node_4,remote_node_5,remote_node_6,remote_node_7,remote_node_8,remote_node_9,remote_node_10,remote_node_11,remote_node_12))
        #print(remote_node)
        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = round(np.mean(remote_node),1)
        remote_node_latency="Remote Node Memory Latency (Low-Avg-High) is " + str(remote_low) + "-" + str(remote_mean) + "-" + str(remote_high)+" ns"
        print(remote_node_latency)


  

        bw = []
        count_2 = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate bandwith data
                if line.strip().startswith("0") and count_2 > 30:
                    break
                count_2 +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count_2,count_2+16):
                bw_line=lines[i].strip().split()[1:]
                bw_line=list(map(float,bw_line))
                bw.append(bw_line)


        #calculate local node
        local_node = np.diagonal(bw)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_bandwidth="Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(local_low/1000,1)) + "-" + str(round(local_mean/1000,1)) + "-" + str(round(local_high/1000,1))+" GB/sec"
        print(local_node_bandwidth)

        #calculate near local node
        matrix = np.array(bw)
        near_local_node_1 = matrix[0:4,0:4]
        #print(near_local_node_1)
        near_local_node_2 = matrix[4:8,4:8]
        #print(near_local_node_2)
        near_local_node_3 = matrix[8:12,8:12]
        #print(near_local_node_3)
        near_local_node_4 = matrix[12:16,12:16]
        #print(near_local_node_4)
    

        #remove local node from list
        m = near_local_node_1.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out1 = near_local_node_1.ravel()[idx]
        #print(out1)

        m = near_local_node_2.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out2 = near_local_node_2.ravel()[idx]
        #print(out2)

        m = near_local_node_3.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out3 = near_local_node_3.ravel()[idx]
        #print(out3)

        m = near_local_node_4.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out4 = near_local_node_4.ravel()[idx]
        #print(out4)


        near_local_node = np.vstack((out1,out2,out3,out4,))
        near_local_high = np.max(near_local_node)
        near_local_low = np.min(near_local_node)
        near_local_mean = round(np.mean(near_local_node),1)
        near_local_node_bandwidth="Near Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(near_local_low/1000,1)) + "-" + str(round(near_local_mean/1000,1)) + "-" + str(round(near_local_high/1000,1))+" GB/sec"
        print(near_local_node_bandwidth)


        #calculate remote node
        remote_node_1 = matrix[4:8,0:4]
        remote_node_2 = matrix[8:12,0:4]
        remote_node_3 = matrix[12:16,0:4]
        remote_node_4 = matrix[0:4,4:8]
        remote_node_5 = matrix[8:12,4:8]
        remote_node_6 = matrix[12:16,4:8]
        remote_node_7 = matrix[0:4,8:12]
        remote_node_8 = matrix[4:8,8:12]
        remote_node_9 = matrix[12:16,8:12]
        remote_node_10 = matrix[0:4,12:16]
        remote_node_11 = matrix[4:8,12:16]
        remote_node_12 = matrix[8:12,12:16]
        
        remote_node = np.vstack((remote_node_1,remote_node_2,remote_node_3,remote_node_4,remote_node_5,remote_node_6,remote_node_7,remote_node_8,remote_node_9,remote_node_10,remote_node_11,remote_node_12))
        #print(remote_node)
        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = round(np.mean(remote_node),1)
        remote_node_bandwidth="Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(remote_low/1000,1)) + "-" + str(round(remote_mean/1000,1)) + "-" + str(round(remote_high/1000,1))+" GB/sec"
        print(remote_node_bandwidth)

        
        with open("mlc_data","r") as f:
            for line in f.readlines():
                if line.startswith("ALL Reads"):
                    value=float(line.strip().split(":")[1])/1000
                    all_reads_speed="ALL Reads speed is " + str(round(value,2))+" GB/s"
                    print(all_reads_speed)
                if line.startswith("3:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_3_1="3:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_3_1)
                if line.startswith("2:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_2_1="2:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_2_1)
                if line.startswith("1:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_1_1="1:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_1_1)   
                if line.startswith("Stream-triad like"):
                    value=float(line.strip().split(":")[1])/1000
                    stream_triade_like_speed="Stream_triad like speed is " + str(round(value,2))+" GB/s"
                    print(stream_triade_like_speed)


        if os.path.exists("mlc_spv_data_4s16numa.log"):
            Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            target = str(os.getcwd()) + '/' + 'mlc_spv_data_4s16numa' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_spv_data",target) 
        #redirect 'print' output to a file
        sys.stdout=open("mlc_spv_data_4s16numa.log","w")
        print(local_node_latency)
        print(near_local_node_latency)
        print(remote_node_latency)
        print(local_node_bandwidth)
        print(near_local_node_bandwidth)
        print(remote_node_bandwidth)
        print(all_reads_speed)
        print(r_w_3_1)
        print(r_w_2_1)
        print(r_w_1_1)
        print(stream_triade_like_speed)
        sys.stdout.close() 
        subprocess.call("cp mlc_data mlc_data_4s16numa", shell=True)


    def run_8s8numa():
        lat = []
        count = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate latency data
                if line.strip().startswith("0"):
                    break
                count +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count,count+8):
                lat_line=lines[i].strip().split()[1:]
                lat_line=list(map(float,lat_line))
                lat.append(lat_line)
            #print(lat)

        #calculate local node
        local_node = np.diagonal(lat)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_latency="Local Node Memory Latency (Low-Avg-High) is " + str(local_low) + "-" + str(local_mean) + "-" + str(local_high)+" ns"
        print(local_node_latency)
        
        matrix = np.array(lat)
        #calculate remote node
        remote_node_1 = matrix[1,0]
        remote_node_2 = matrix[2,0]
        remote_node_3 = matrix[5,0]
        remote_node_4 = matrix[6,0]
        remote_node_5 = matrix[0,1]
        remote_node_6 = matrix[0,2]
        remote_node_7 = matrix[3,1]
        remote_node_8 = matrix[3,2]
        remote_node_9 = matrix[4,1]
        remote_node_10 = matrix[4,2]
        remote_node_11 = matrix[7,1]
        remote_node_12 = matrix[7,2]
        remote_node_13 = matrix[1,3]
        remote_node_14 = matrix[1,4]
        remote_node_15 = matrix[2,3]
        remote_node_16 = matrix[2,4]
        remote_node_17 = matrix[5,3]
        remote_node_18 = matrix[5,4]
        remote_node_19 = matrix[6,3]
        remote_node_20 = matrix[6,4]
        remote_node_21 = matrix[0,5]
        remote_node_22 = matrix[0,6]
        remote_node_23 = matrix[3,5]
        remote_node_24 = matrix[3,6]
        remote_node_25 = matrix[4,5]
        remote_node_26 = matrix[4,6]
        remote_node_27 = matrix[7,5]
        remote_node_28 = matrix[7,6]
        remote_node_29 = matrix[1,7]
        remote_node_30 = matrix[2,7]
        remote_node_31 = matrix[5,7]
        remote_node_32 = matrix[6,7]
    
        remote_node = np.array([remote_node_1,remote_node_2,remote_node_3,remote_node_4,remote_node_5,remote_node_6,remote_node_7,remote_node_8,remote_node_9,remote_node_10,remote_node_11,remote_node_12,remote_node_13,remote_node_14,remote_node_15,remote_node_16,remote_node_17,remote_node_18,remote_node_19,remote_node_20,remote_node_21,remote_node_22,remote_node_23,remote_node_24,remote_node_25,remote_node_26,remote_node_27,remote_node_28,remote_node_29,remote_node_30,remote_node_31,remote_node_32],dtype=object)
        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = np.round(np.mean(remote_node),1)
        remote_node_latency="Remote Node Memory Latency (Low-Avg-High) is " + str(remote_low) + "-" + str(remote_mean) + "-" + str(remote_high)+" ns"
        print(remote_node_latency)


        #calculate far_remote node
        far_remote_node_1 = matrix[3,0]
        far_remote_node_2 = matrix[4,0]
        far_remote_node_3 = matrix[7,0]
        far_remote_node_4 = matrix[2,1]
        far_remote_node_5 = matrix[1,2]
        far_remote_node_6 = matrix[5,1]
        far_remote_node_7 = matrix[5,2]
        far_remote_node_8 = matrix[6,1]
        far_remote_node_9 = matrix[6,2]
        far_remote_node_10 = matrix[0,3]
        far_remote_node_11 = matrix[0,4]
        far_remote_node_12 = matrix[4,3]
        far_remote_node_13 = matrix[3,4]
        far_remote_node_14 = matrix[7,3]
        far_remote_node_15 = matrix[7,4]
        far_remote_node_16 = matrix[1,5]
        far_remote_node_17 = matrix[1,6]
        far_remote_node_18 = matrix[2,5]
        far_remote_node_19 = matrix[2,6]
        far_remote_node_20 = matrix[6,5]
        far_remote_node_21 = matrix[5,6]
        far_remote_node_22 = matrix[1,7]
        far_remote_node_23 = matrix[3,7]
        far_remote_node_24 = matrix[4,7]

        far_remote_node = np.array([far_remote_node_1,far_remote_node_2,far_remote_node_3,far_remote_node_4,far_remote_node_5,far_remote_node_6,far_remote_node_7,far_remote_node_8,far_remote_node_9,far_remote_node_10,far_remote_node_11,far_remote_node_12,far_remote_node_13,far_remote_node_14,far_remote_node_15,far_remote_node_16,far_remote_node_17,far_remote_node_18,far_remote_node_19,far_remote_node_20,far_remote_node_21,far_remote_node_22,far_remote_node_23,far_remote_node_24],dtype=object)
        far_remote_high = np.max(far_remote_node)
        far_remote_low = np.min(far_remote_node)
        far_remote_mean = np.round(np.mean(far_remote_node),1)
        far_remote_node_latency="Far Remote Node Memory Latency (Low-Avg-High) is " + str(far_remote_low) + "-" + str(far_remote_mean) + "-" + str(far_remote_high)+" ns"
        print(far_remote_node_latency)

        bw = []
        count_2 = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate bandwith data
                if line.strip().startswith("0") and count_2 > 20:
                    break
                count_2 +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count_2,count_2+8):
                bw_line=lines[i].strip().split()[1:]
                bw_line=list(map(float,bw_line))
                bw.append(bw_line)


        #calculate local node
        local_node = np.diagonal(bw)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_bandwidth="Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(local_low/1000,1)) + "-" + str(round(local_mean/1000,1)) + "-" + str(round(local_high/1000,1))+" GB/sec"
        print(local_node_bandwidth)

        matrix = np.array(bw)
        #calculate remote node
        remote_node_1 = matrix[1,0]
        remote_node_2 = matrix[2,0]
        remote_node_3 = matrix[5,0]
        remote_node_4 = matrix[6,0]
        remote_node_5 = matrix[0,1]
        remote_node_6 = matrix[0,2]
        remote_node_7 = matrix[3,1]
        remote_node_8 = matrix[3,2]
        remote_node_9 = matrix[4,1]
        remote_node_10 = matrix[4,2]
        remote_node_11 = matrix[7,1]
        remote_node_12 = matrix[7,2]
        remote_node_13 = matrix[1,3]
        remote_node_14 = matrix[1,4]
        remote_node_15 = matrix[2,3]
        remote_node_16 = matrix[2,4]
        remote_node_17 = matrix[5,3]
        remote_node_18 = matrix[5,4]
        remote_node_19 = matrix[6,3]
        remote_node_20 = matrix[6,4]
        remote_node_21 = matrix[0,5]
        remote_node_22 = matrix[0,6]
        remote_node_23 = matrix[3,5]
        remote_node_24 = matrix[3,6]
        remote_node_25 = matrix[4,5]
        remote_node_26 = matrix[4,6]
        remote_node_27 = matrix[7,5]
        remote_node_28 = matrix[7,6]
        remote_node_29 = matrix[1,7]
        remote_node_30 = matrix[2,7]
        remote_node_31 = matrix[5,7]
        remote_node_32 = matrix[6,7]

        remote_node = np.array([remote_node_1,remote_node_2,remote_node_3,remote_node_4,remote_node_5,remote_node_6,remote_node_7,remote_node_8,remote_node_9,remote_node_10,remote_node_11,remote_node_12,remote_node_13,remote_node_14,remote_node_15,remote_node_16,remote_node_17,remote_node_18,remote_node_19,remote_node_20,remote_node_21,remote_node_22,remote_node_23,remote_node_24,remote_node_25,remote_node_26,remote_node_27,remote_node_28,remote_node_29,remote_node_30,remote_node_31,remote_node_32],dtype=object)
        #print(remote_node)
        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = np.round(np.mean(remote_node),1)
        remote_node_bandwidth="Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(remote_low/1000,1)) + "-" + str(round(remote_mean/1000,1)) + "-" + str(round(remote_high/1000,1))+" GB/sec"
        print(remote_node_bandwidth)


        #calculate far_remote node
        far_remote_node_1 = matrix[3,0]
        far_remote_node_2 = matrix[4,0]
        far_remote_node_3 = matrix[7,0]
        far_remote_node_4 = matrix[2,1]
        far_remote_node_5 = matrix[1,2]
        far_remote_node_6 = matrix[5,1]
        far_remote_node_7 = matrix[5,2]
        far_remote_node_8 = matrix[6,1]
        far_remote_node_9 = matrix[6,2]
        far_remote_node_10 = matrix[0,3]
        far_remote_node_11 = matrix[0,4]
        far_remote_node_12 = matrix[4,3]
        far_remote_node_13 = matrix[3,4]
        far_remote_node_14 = matrix[7,3]
        far_remote_node_15 = matrix[7,4]
        far_remote_node_16 = matrix[1,5]
        far_remote_node_17 = matrix[1,6]
        far_remote_node_18 = matrix[2,5]
        far_remote_node_19 = matrix[2,6]
        far_remote_node_20 = matrix[6,5]
        far_remote_node_21 = matrix[5,6]
        far_remote_node_22 = matrix[1,7]
        far_remote_node_23 = matrix[3,7]
        far_remote_node_24 = matrix[4,7]

        far_remote_node = np.array([far_remote_node_1,far_remote_node_2,far_remote_node_3,far_remote_node_4,far_remote_node_5,far_remote_node_6,far_remote_node_7,far_remote_node_8,far_remote_node_9,far_remote_node_10,far_remote_node_11,far_remote_node_12,far_remote_node_13,far_remote_node_14,far_remote_node_15,far_remote_node_16,far_remote_node_17,far_remote_node_18,far_remote_node_19,far_remote_node_20,far_remote_node_21,far_remote_node_22,far_remote_node_23,far_remote_node_24],dtype=object)
        #print(far_remote_node)
        far_remote_high = np.max(far_remote_node)
        far_remote_low = np.min(far_remote_node)
        far_remote_mean = np.round(np.mean(far_remote_node),1)
        far_remote_node_bandwidth="Far Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(far_remote_low/1000,1)) + "-" + str(round(far_remote_mean/1000,1)) + "-" + str(round(far_remote_high/1000,1))+" GB/sec"
        print(far_remote_node_bandwidth)
        
        with open("mlc_data","r") as f:
            for line in f.readlines():
                if line.startswith("ALL Reads"):
                    value=float(line.strip().split(":")[1])/1000
                    all_reads_speed="ALL Reads speed is " + str(round(value,2))+" GB/s"
                    print(all_reads_speed)
                if line.startswith("3:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_3_1="3:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_3_1)
                if line.startswith("2:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_2_1="2:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_2_1)
                if line.startswith("1:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_1_1="1:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_1_1)   
                if line.startswith("Stream-triad like"):
                    value=float(line.strip().split(":")[1])/1000
                    stream_triade_like_speed="Stream_triad like speed is " + str(round(value,2))+" GB/s"
                    print(stream_triade_like_speed)
        
        if os.path.exists("mlc_spv_data_8s8numa.log"):
            Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            target = str(os.getcwd()) + '/' + 'mlc_spv_data_8s8numa' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_spv_data_8s8numa.log",target) 
        #redirect 'print' output to a file
        sys.stdout=open("mlc_spv_data","w")
        print(local_node_latency)
        print(remote_node_latency)
        print(far_remote_node_latency)
        print(local_node_bandwidth)
        print(remote_node_bandwidth)
        print(far_remote_node_bandwidth)
        print(all_reads_speed)
        print(r_w_3_1)
        print(r_w_2_1)
        print(r_w_1_1)
        print(stream_triade_like_speed)
        sys.stdout.close()
        subprocess.call("cp mlc_data mlc_data_8s8numa", shell=True)



    def run_8s16numa():
        lat = []
        count = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate latency data
                if line.strip().startswith("0"):
                    break
                count +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count,count+16):
                lat_line=lines[i].strip().split()[1:]
                lat_line=list(map(float,lat_line))
                lat.append(lat_line)
            #print(lat)

        #calculate local node
        local_node = np.diagonal(lat)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_latency="Local Node Memory Latency (Low-Avg-High) is " + str(local_low) + "-" + str(local_mean) + "-" + str(local_high)+" ns"
        print(local_node_latency)

        #calculate near local node
        matrix = np.array(lat)
        #print(matrix)
        near_local_node_1 = matrix[0:2,0:2]
        #print(near_local_node_1)
        near_local_node_2 = matrix[2:4,2:4]
        #print(near_local_node_2)
        near_local_node_3 = matrix[4:6,4:6]
        #print(near_local_node_3)
        near_local_node_4 = matrix[6:8,6:8]
        #print(near_local_node_4)
        near_local_node_5 = matrix[8:10,8:10]
        #print(near_local_node_5)
        near_local_node_6 = matrix[10:12,10:12]
        #print(near_local_node_6)
        near_local_node_7 = matrix[12:14,12:14]
        #print(near_local_node_7)
        near_local_node_8 = matrix[14:16,14:16]
        #print(near_local_node_8)

        #remove local node from list
        m = near_local_node_1.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out1 = near_local_node_1.ravel()[idx]
        #print(out1)

        m = near_local_node_2.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out2 = near_local_node_2.ravel()[idx]
        #print(out2)

        m = near_local_node_3.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out3 = near_local_node_3.ravel()[idx]
        #print(out3)

        m = near_local_node_4.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out4 = near_local_node_4.ravel()[idx]
        #print(out4)

        m = near_local_node_5.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out5 = near_local_node_5.ravel()[idx]
        #print(out5)

        m = near_local_node_6.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out6 = near_local_node_6.ravel()[idx]
        #print(out6)

        m = near_local_node_7.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out7 = near_local_node_7.ravel()[idx]
        #print(out7)

        m = near_local_node_8.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out8 = near_local_node_8.ravel()[idx]
        #print(out8)


        near_local_node = np.vstack((out1,out2,out3,out4,out5,out6,out7,out8))
        #print(near_local_node)
        near_local_high = np.max(near_local_node)
        near_local_low = np.min(near_local_node)
        near_local_mean = round(np.mean(near_local_node),1)
        near_local_node_latency="Near Local Node Memory Latency (Low-Avg-High) is " + str(near_local_low) + "-" + str(near_local_mean) + "-" + str(near_local_high)+" ns"
        print(near_local_node_latency)


        #calculate remote node
        remote_node_1 = matrix[2:4,0:2]
        remote_node_2 = matrix[4:6,0:2]
        remote_node_3 = matrix[10:12,0:2]
        remote_node_4 = matrix[12:14,0:2]
        remote_node_5 = matrix[0:2,2:4]
        remote_node_6 = matrix[0:2,4:6]
        remote_node_7 = matrix[6:8,2:4]
        remote_node_8 = matrix[6:8,4:6]
        remote_node_9 = matrix[8:10,2:4]
        remote_node_10 = matrix[8:10,4:6]
        remote_node_11 = matrix[14:16,2:4]
        remote_node_12 = matrix[14:16,4:6]
        remote_node_13 = matrix[2:4,6:8]
        remote_node_14 = matrix[2:4,8:10]
        remote_node_15 = matrix[4:6,6:8]
        remote_node_16 = matrix[4:6,8:10]
        remote_node_17 = matrix[10:12,6:8]
        remote_node_18 = matrix[10:12,8:10]
        remote_node_19 = matrix[12:14,6:8]
        remote_node_20 = matrix[12:14,8:10]
        remote_node_21 = matrix[0:2,10:12]
        remote_node_22 = matrix[0:2,12:14]
        remote_node_23 = matrix[6:8,10:12]
        remote_node_24 = matrix[6:8,12:14]
        remote_node_25 = matrix[8:10,10:12]
        remote_node_26 = matrix[8:10,12:14]
        remote_node_27 = matrix[14:16,10:12]
        remote_node_28 = matrix[14:16,12:14]
        remote_node_29 = matrix[2:4,14:16]
        remote_node_30 = matrix[4:6,14:16]
        remote_node_31 = matrix[10:12,14:16]
        remote_node_32 = matrix[12:14,14:16]

        remote_node = np.vstack((remote_node_1,remote_node_2,remote_node_3,remote_node_4,remote_node_5,remote_node_6,remote_node_7,remote_node_8,remote_node_9,remote_node_10,remote_node_11,remote_node_12,remote_node_13,remote_node_14,remote_node_15,remote_node_16,remote_node_17,remote_node_18,remote_node_19,remote_node_20,remote_node_21,remote_node_22,remote_node_23,remote_node_24,remote_node_25,remote_node_26,remote_node_27,remote_node_28,remote_node_29,remote_node_30,remote_node_31,remote_node_32))
        #print(remote_node)
        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = round(np.mean(remote_node),1)
        remote_node_latency="Remote Node Memory Latency (Low-Avg-High) is " + str(remote_low) + "-" + str(remote_mean) + "-" + str(remote_high)+" ns"
        print(remote_node_latency)


        #calculate far_remote node
        far_remote_node_1 = matrix[6:8,0:2]
        far_remote_node_2 = matrix[8:10,0:2]
        far_remote_node_3 = matrix[14:16,0:2]
        far_remote_node_4 = matrix[4:6,2:4]
        far_remote_node_5 = matrix[2:4,4:6]
        far_remote_node_6 = matrix[10:12,2:4]
        far_remote_node_7 = matrix[10:12,4:6]
        far_remote_node_8 = matrix[12:14,2:4]
        far_remote_node_9 = matrix[12:14,4:6]
        far_remote_node_10 = matrix[0:2,6:8]
        far_remote_node_11 = matrix[0:2,8:10]
        far_remote_node_12 = matrix[8:10,6:8]
        far_remote_node_13 = matrix[6:8,8:10]
        far_remote_node_14 = matrix[14:16,6:8]
        far_remote_node_15 = matrix[14:16,8:10]
        far_remote_node_16 = matrix[2:4,10:12]
        far_remote_node_17 = matrix[2:4,12:14]
        far_remote_node_18 = matrix[4:6,10:12]
        far_remote_node_19 = matrix[4:6,12:14]
        far_remote_node_20 = matrix[12:14,10:12]
        far_remote_node_21 = matrix[10:12,12:14]
        far_remote_node_22 = matrix[0:2,14:16]
        far_remote_node_23 = matrix[6:8,14:16]
        far_remote_node_24 = matrix[8:10,14:16]

        far_remote_node = np.vstack((far_remote_node_1,far_remote_node_2,far_remote_node_3,far_remote_node_4,far_remote_node_5,far_remote_node_6,far_remote_node_7,far_remote_node_8,far_remote_node_9,far_remote_node_10,far_remote_node_11,far_remote_node_12,far_remote_node_13,far_remote_node_14,far_remote_node_15,far_remote_node_16,far_remote_node_17,far_remote_node_18,far_remote_node_19,far_remote_node_20,far_remote_node_21,far_remote_node_22,far_remote_node_23,far_remote_node_24))
        #print(far_remote_node)
        far_remote_high = np.max(far_remote_node)
        far_remote_low = np.min(far_remote_node)
        far_remote_mean = round(np.mean(far_remote_node),1)
        far_remote_node_latency="Far Remote Node Memory Latency (Low-Avg-High) is " + str(far_remote_low) + "-" + str(far_remote_mean) + "-" + str(far_remote_high)+" ns"
        print(far_remote_node_latency)

        bw = []
        count_2 = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate bandwith data
                if line.strip().startswith("0") and count_2 > 30:
                    break
                count_2 +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count_2,count_2+16):
                bw_line=lines[i].strip().split()[1:]
                bw_line=list(map(float,bw_line))
                bw.append(bw_line)


        #calculate local node
        local_node = np.diagonal(bw)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_bandwidth="Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(local_low/1000,1)) + "-" + str(round(local_mean/1000,1)) + "-" + str(round(local_high/1000,1))+" GB/sec"
        print(local_node_bandwidth)

        #calculate near local node
        matrix = np.array(bw)
        near_local_node_1 = matrix[0:2,0:2]
        #print(near_local_node_1)
        near_local_node_2 = matrix[2:4,2:4]
        #print(near_local_node_2)
        near_local_node_3 = matrix[4:6,4:6]
        #print(near_local_node_3)
        near_local_node_4 = matrix[6:8,6:8]
        #print(near_local_node_4)
        near_local_node_5 = matrix[8:10,8:10]
        #print(near_local_node_5)
        near_local_node_6 = matrix[10:12,10:12]
        #print(near_local_node_6)
        near_local_node_7 = matrix[12:14,12:14]
        #print(near_local_node_7)
        near_local_node_8 = matrix[14:16,14:16]
        #print(near_local_node_8)

        #remove local node from list
        m = near_local_node_1.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out1 = near_local_node_1.ravel()[idx]
        #print(out1)

        m = near_local_node_2.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out2 = near_local_node_2.ravel()[idx]
        #print(out2)

        m = near_local_node_3.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out3 = near_local_node_3.ravel()[idx]
        #print(out3)

        m = near_local_node_4.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out4 = near_local_node_4.ravel()[idx]
        #print(out4)

        m = near_local_node_5.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out5 = near_local_node_5.ravel()[idx]
        #print(out5)

        m = near_local_node_6.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out6 = near_local_node_6.ravel()[idx]
        #print(out6)

        m = near_local_node_7.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out7 = near_local_node_7.ravel()[idx]
        #print(out7)

        m = near_local_node_8.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out8 = near_local_node_8.ravel()[idx]
        #print(out8)


        near_local_node = np.vstack((out1,out2,out3,out4,out5,out6,out7,out8))
        #print(near_local_node)
        near_local_high = np.max(near_local_node)
        near_local_low = np.min(near_local_node)
        near_local_mean = round(np.mean(near_local_node),1)
        near_local_node_bandwidth="Near Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(near_local_low/1000,1)) + "-" + str(round(near_local_mean/1000,1)) + "-" + str(round(near_local_high/1000,1))+" GB/sec"
        print(near_local_node_bandwidth)


        #calculate remote node
        remote_node_1 = matrix[2:4,0:2]
        remote_node_2 = matrix[4:6,0:2]
        remote_node_3 = matrix[10:12,0:2]
        remote_node_4 = matrix[12:14,0:2]
        remote_node_5 = matrix[0:2,2:4]
        remote_node_6 = matrix[0:2,4:6]
        remote_node_7 = matrix[6:8,2:4]
        remote_node_8 = matrix[6:8,4:6]
        remote_node_9 = matrix[8:10,2:4]
        remote_node_10 = matrix[8:10,4:6]
        remote_node_11 = matrix[14:16,2:4]
        remote_node_12 = matrix[14:16,4:6]
        remote_node_13 = matrix[2:4,6:8]
        remote_node_14 = matrix[2:4,8:10]
        remote_node_15 = matrix[4:6,6:8]
        remote_node_16 = matrix[4:6,8:10]
        remote_node_17 = matrix[10:12,6:8]
        remote_node_18 = matrix[10:12,8:10]
        remote_node_19 = matrix[12:14,6:8]
        remote_node_20 = matrix[12:14,8:10]
        remote_node_21 = matrix[0:2,10:12]
        remote_node_22 = matrix[0:2,12:14]
        remote_node_23 = matrix[6:8,10:12]
        remote_node_24 = matrix[6:8,12:14]
        remote_node_25 = matrix[8:10,10:12]
        remote_node_26 = matrix[8:10,12:14]
        remote_node_27 = matrix[14:16,10:12]
        remote_node_28 = matrix[14:16,12:14]
        remote_node_29 = matrix[2:4,14:16]
        remote_node_30 = matrix[4:6,14:16]
        remote_node_31 = matrix[10:12,14:16]
        remote_node_32 = matrix[12:14,14:16]

        remote_node = np.vstack((remote_node_1,remote_node_2,remote_node_3,remote_node_4,remote_node_5,remote_node_6,remote_node_7,remote_node_8,remote_node_9,remote_node_10,remote_node_11,remote_node_12,remote_node_13,remote_node_14,remote_node_15,remote_node_16,remote_node_17,remote_node_18,remote_node_19,remote_node_20,remote_node_21,remote_node_22,remote_node_23,remote_node_24,remote_node_25,remote_node_26,remote_node_27,remote_node_28,remote_node_29,remote_node_30,remote_node_31,remote_node_32))
        #print(remote_node)
        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = round(np.mean(remote_node),1)
        remote_node_bandwidth="Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(remote_low/1000,1)) + "-" + str(round(remote_mean/1000,1)) + "-" + str(round(remote_high/1000,1))+" GB/sec"
        print(remote_node_bandwidth)


        #calculate far_remote node
        far_remote_node_1 = matrix[6:8,0:2]
        far_remote_node_2 = matrix[8:10,0:2]
        far_remote_node_3 = matrix[14:16,0:2]
        far_remote_node_4 = matrix[4:6,2:4]
        far_remote_node_5 = matrix[2:4,4:6]
        far_remote_node_6 = matrix[10:12,2:4]
        far_remote_node_7 = matrix[10:12,4:6]
        far_remote_node_8 = matrix[12:14,2:4]
        far_remote_node_9 = matrix[12:14,4:6]
        far_remote_node_10 = matrix[0:2,6:8]
        far_remote_node_11 = matrix[0:2,8:10]
        far_remote_node_12 = matrix[8:10,6:8]
        far_remote_node_13 = matrix[6:8,8:10]
        far_remote_node_14 = matrix[14:16,6:8]
        far_remote_node_15 = matrix[14:16,8:10]
        far_remote_node_16 = matrix[2:4,10:12]
        far_remote_node_17 = matrix[2:4,12:14]
        far_remote_node_18 = matrix[4:6,10:12]
        far_remote_node_19 = matrix[4:6,12:14]
        far_remote_node_20 = matrix[12:14,10:12]
        far_remote_node_21 = matrix[10:12,12:14]
        far_remote_node_22 = matrix[0:2,14:16]
        far_remote_node_23 = matrix[6:8,14:16]
        far_remote_node_24 = matrix[8:10,14:16]

        far_remote_node = np.vstack((far_remote_node_1,far_remote_node_2,far_remote_node_3,far_remote_node_4,far_remote_node_5,far_remote_node_6,far_remote_node_7,far_remote_node_8,far_remote_node_9,far_remote_node_10,far_remote_node_11,far_remote_node_12,far_remote_node_13,far_remote_node_14,far_remote_node_15,far_remote_node_16,far_remote_node_17,far_remote_node_18,far_remote_node_19,far_remote_node_20,far_remote_node_21,far_remote_node_22,far_remote_node_23,far_remote_node_24))
        #print(far_remote_node)
        far_remote_high = np.max(far_remote_node)
        far_remote_low = np.min(far_remote_node)
        far_remote_mean = round(np.mean(far_remote_node),1)
        far_remote_node_bandwidth="Far Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(far_remote_low/1000,1)) + "-" + str(round(far_remote_mean/1000,1)) + "-" + str(round(far_remote_high/1000,1))+" GB/sec"
        print(far_remote_node_bandwidth)
        
        with open("mlc_data","r") as f:
            for line in f.readlines():
                if line.startswith("ALL Reads"):
                    value=float(line.strip().split(":")[1])/1000
                    all_reads_speed="ALL Reads speed is " + str(round(value,2))+" GB/s"
                    print(all_reads_speed)
                if line.startswith("3:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_3_1="3:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_3_1)
                if line.startswith("2:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_2_1="2:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_2_1)
                if line.startswith("1:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_1_1="1:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_1_1)   
                if line.startswith("Stream-triad like"):
                    value=float(line.strip().split(":")[1])/1000
                    stream_triade_like_speed="Stream_triad like speed is " + str(round(value,2))+" GB/s"
                    print(stream_triade_like_speed)


        if os.path.exists("mlc_spv_data_8s16numa.log"):
            Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            target = str(os.getcwd()) + '/' + 'mlc_spv_data_8s16numa' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_spv_data_8s16numa.log",target) 
        #redirect 'print' output to a file
        sys.stdout=open("mlc_spv_data_8s_16numa.log","w")
        print(local_node_latency)
        print(near_local_node_latency)
        print(remote_node_latency)
        print(far_remote_node_latency)
        print(local_node_bandwidth)
        print(near_local_node_bandwidth)
        print(remote_node_bandwidth)
        print(far_remote_node_bandwidth)
        print(all_reads_speed)
        print(r_w_3_1)
        print(r_w_2_1)
        print(r_w_1_1)
        print(stream_triade_like_speed)
        sys.stdout.close() 
        subprocess.call("cp mlc_data mlc_data_8s16numa", shell=True)


    def run_8s32numa():
        lat = []
        count = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate latency data
                if line.strip().startswith("0"):
                    break
                count +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count,count+32):
                lat_line=lines[i].strip().split()[1:]
                lat_line=list(map(float,lat_line))
                lat.append(lat_line)
            #print(lat)

        #calculate local node
        local_node = np.diagonal(lat)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_latency="Local Node Memory Latency (Low-Avg-High) is " + str(local_low) + "-" + str(local_mean) + "-" + str(local_high)+" ns"
        print(local_node_latency)

        #calculate near local node
        matrix = np.array(lat)
        #print(matrix)
        near_local_node_1 = matrix[0:4,0:4]
        #print(near_local_node_1)
        near_local_node_2 = matrix[4:8,4:8]
        #print(near_local_node_2)
        near_local_node_3 = matrix[8:12,8:12]
        #print(near_local_node_3)
        near_local_node_4 = matrix[12:16,12:16]
        #print(near_local_node_4)
        near_local_node_5 = matrix[16:20,16:20]
        #print(near_local_node_5)
        near_local_node_6 = matrix[20:24,20:24]
        #print(near_local_node_6)
        near_local_node_7 = matrix[24:28,24:28]
        #print(near_local_node_7)
        near_local_node_8 = matrix[28:32,28:32]
        #print(near_local_node_8)

        #remove local node from list
        m = near_local_node_1.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out1 = near_local_node_1.ravel()[idx]
        #print(out1)

        m = near_local_node_2.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out2 = near_local_node_2.ravel()[idx]
        #print(out2)

        m = near_local_node_3.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out3 = near_local_node_3.ravel()[idx]
        #print(out3)

        m = near_local_node_4.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out4 = near_local_node_4.ravel()[idx]
        #print(out4)

        m = near_local_node_5.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out5 = near_local_node_5.ravel()[idx]
        #print(out5)

        m = near_local_node_6.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out6 = near_local_node_6.ravel()[idx]
        #print(out6)

        m = near_local_node_7.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out7 = near_local_node_7.ravel()[idx]
        #print(out7)

        m = near_local_node_8.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out8 = near_local_node_8.ravel()[idx]
        #print(out8)


        near_local_node = np.vstack((out1,out2,out3,out4,out5,out6,out7,out8))
        #print(near_local_node)
        near_local_high = np.max(near_local_node)
        near_local_low = np.min(near_local_node)
        near_local_mean = round(np.mean(near_local_node),1)
        near_local_node_latency="Near Local Node Memory Latency (Low-Avg-High) is " + str(near_local_low) + "-" + str(near_local_mean) + "-" + str(near_local_high)+" ns"
        print(near_local_node_latency)


        #calculate remote node
        remote_node_1 = matrix[4:8,0:4]
        remote_node_2 = matrix[8:12,0:4]
        remote_node_3 = matrix[20:24,0:4]
        remote_node_4 = matrix[24:28,0:4]
        remote_node_5 = matrix[0:4,4:8]
        remote_node_6 = matrix[0:4,8:12]
        remote_node_7 = matrix[12:16,4:8]
        remote_node_8 = matrix[12:16,8:12]
        remote_node_9 = matrix[16:20,4:8]
        remote_node_10 = matrix[16:20,8:12]
        remote_node_11 = matrix[28:32,4:8]
        remote_node_12 = matrix[28:32,8:12]
        remote_node_13 = matrix[4:8,12:16]
        remote_node_14 = matrix[4:8,16:20]
        remote_node_15 = matrix[8:12,12:16]
        remote_node_16 = matrix[8:12,16:20]
        remote_node_17 = matrix[20:24,12:16]
        remote_node_18 = matrix[20:24,16:20]
        remote_node_19 = matrix[24:28,12:16]
        remote_node_20 = matrix[24:28,16:20]
        remote_node_21 = matrix[0:4,20:24]
        remote_node_22 = matrix[0:4,24:28]
        remote_node_23 = matrix[12:16,20:24]
        remote_node_24 = matrix[12:16,24:28]
        remote_node_25 = matrix[16:20,20:24]
        remote_node_26 = matrix[16:20,24:28]
        remote_node_27 = matrix[28:32,20:24]
        remote_node_28 = matrix[28:32,24:28]
        remote_node_29 = matrix[4:8,28:32]
        remote_node_30 = matrix[8:12,28:32]
        remote_node_31 = matrix[20:24,28:32]
        remote_node_32 = matrix[24:28,28:32]

        remote_node = np.vstack((remote_node_1,remote_node_2,remote_node_3,remote_node_4,remote_node_5,remote_node_6,remote_node_7,remote_node_8,remote_node_9,remote_node_10,remote_node_11,remote_node_12,remote_node_13,remote_node_14,remote_node_15,remote_node_16,remote_node_17,remote_node_18,remote_node_19,remote_node_20,remote_node_21,remote_node_22,remote_node_23,remote_node_24,remote_node_25,remote_node_26,remote_node_27,remote_node_28,remote_node_29,remote_node_30,remote_node_31,remote_node_32))
        #print(remote_node)
        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = round(np.mean(remote_node),1)
        remote_node_latency="Remote Node Memory Latency (Low-Avg-High) is " + str(remote_low) + "-" + str(remote_mean) + "-" + str(remote_high)+" ns"
        print(remote_node_latency)


        #calculate far_remote node
        far_remote_node_1 = matrix[12:16,0:4]
        far_remote_node_2 = matrix[16:20,0:4]
        far_remote_node_3 = matrix[28:32,0:4]
        far_remote_node_4 = matrix[8:12,4:8]
        far_remote_node_5 = matrix[4:8,8:12]
        far_remote_node_6 = matrix[20:24,4:8]
        far_remote_node_7 = matrix[20:24,8:12]
        far_remote_node_8 = matrix[24:28,4:8]
        far_remote_node_9 = matrix[24:28,8:12]
        far_remote_node_10 = matrix[0:4,12:16]
        far_remote_node_11 = matrix[0:4,16:20]
        far_remote_node_12 = matrix[16:20,12:16]
        far_remote_node_13 = matrix[12:16,16:20]
        far_remote_node_14 = matrix[28:32,12:16]
        far_remote_node_15 = matrix[28:32,16:20]
        far_remote_node_16 = matrix[4:8,20:24]
        far_remote_node_17 = matrix[4:8,24:28]
        far_remote_node_18 = matrix[8:12,20:24]
        far_remote_node_19 = matrix[8:12,24:28]
        far_remote_node_20 = matrix[24:28,20:24]
        far_remote_node_21 = matrix[20:24,24:28]
        far_remote_node_22 = matrix[0:4,28:32]
        far_remote_node_23 = matrix[12:16,28:32]
        far_remote_node_24 = matrix[16:20,28:32]
        #print(far_remote_node_1)
        far_remote_node = np.vstack((far_remote_node_1,far_remote_node_2,far_remote_node_3,far_remote_node_4,far_remote_node_5,far_remote_node_6,far_remote_node_7,far_remote_node_8,far_remote_node_9,far_remote_node_10,far_remote_node_11,far_remote_node_12,far_remote_node_13,far_remote_node_14,far_remote_node_15,far_remote_node_16,far_remote_node_17,far_remote_node_18,far_remote_node_19,far_remote_node_20,far_remote_node_21,far_remote_node_22,far_remote_node_23,far_remote_node_24))
        #print(far_remote_node)
        far_remote_high = np.max(far_remote_node)
        far_remote_low = np.min(far_remote_node)
        far_remote_mean = round(np.mean(far_remote_node),1)
        far_remote_node_latency="Far Remote Node Memory Latency (Low-Avg-High) is " + str(far_remote_low) + "-" + str(far_remote_mean) + "-" + str(far_remote_high)+" ns"
        print(far_remote_node_latency)

        bw = []
        count_2 = 0
        with open("mlc_data","r") as f:
            for line in f.readlines():
                #locate bandwith data
                if line.strip().startswith("0") and count_2 > 50:
                    break
                count_2 +=1


        with open("mlc_data","r") as x:
            lines = x.readlines()
            for i in range(count_2,count_2+32):
                bw_line=lines[i].strip().split()[1:]
                bw_line=list(map(float,bw_line))
                bw.append(bw_line)


        #calculate local node
        local_node = np.diagonal(bw)
        #print(local_node)
        local_high =  max(local_node)
        local_low = min(local_node)
        local_mean = round(sum(local_node)/len(local_node),1)
        local_node_bandwidth="Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(local_low/1000,1)) + "-" + str(round(local_mean/1000,1)) + "-" + str(round(local_high/1000,1))+" GB/sec"
        print(local_node_bandwidth)

        #calculate near local node
        matrix = np.array(bw)
        #print(matrix)
        near_local_node_1 = matrix[0:4,0:4]
        #print(near_local_node_1)
        near_local_node_2 = matrix[4:8,4:8]
        #print(near_local_node_2)
        near_local_node_3 = matrix[8:12,8:12]
        #print(near_local_node_3)
        near_local_node_4 = matrix[12:16,12:16]
        #print(near_local_node_4)
        near_local_node_5 = matrix[16:20,16:20]
        #print(near_local_node_5)
        near_local_node_6 = matrix[20:24,20:24]
        #print(near_local_node_6)
        near_local_node_7 = matrix[24:28,24:28]
        #print(near_local_node_7)
        near_local_node_8 = matrix[28:32,28:32]
        #print(near_local_node_8)

        #remove local node from list
        m = near_local_node_1.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out1 = near_local_node_1.ravel()[idx]
        #print(out1)

        m = near_local_node_2.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out2 = near_local_node_2.ravel()[idx]
        #print(out2)

        m = near_local_node_3.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out3 = near_local_node_3.ravel()[idx]
        #print(out3)

        m = near_local_node_4.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out4 = near_local_node_4.ravel()[idx]
        #print(out4)

        m = near_local_node_5.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out5 = near_local_node_5.ravel()[idx]
        #print(out5)

        m = near_local_node_6.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out6 = near_local_node_6.ravel()[idx]
        #print(out6)

        m = near_local_node_7.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out7 = near_local_node_7.ravel()[idx]
        #print(out7)

        m = near_local_node_8.shape[0]
        idx = (np.arange(1,m+1) + (m+1)*np.arange(m-1)[:,None]).reshape(m,-1)
        out8 = near_local_node_8.ravel()[idx]
        #print(out8)


        near_local_node = np.vstack((out1,out2,out3,out4,out5,out6,out7,out8))
        #print(near_local_node)
        near_local_high = np.max(near_local_node)
        near_local_low = np.min(near_local_node)
        near_local_mean = round(np.mean(near_local_node),1)
        near_local_node_bandwidth="Near Local Node Memory Bandwidth (Low-Avg-High) is " + str(round(near_local_low/1000,1)) + "-" + str(round(near_local_mean/1000,1)) + "-" + str(round(near_local_high/1000,1))+" GB/sec"
        print(near_local_node_bandwidth)


        #calculate remote node
        remote_node_1 = matrix[4:8,0:4]
        remote_node_2 = matrix[8:12,0:4]
        remote_node_3 = matrix[20:24,0:4]
        remote_node_4 = matrix[24:28,0:4]
        remote_node_5 = matrix[0:4,4:8]
        remote_node_6 = matrix[0:4,8:12]
        remote_node_7 = matrix[12:16,4:8]
        remote_node_8 = matrix[12:16,8:12]
        remote_node_9 = matrix[16:20,4:8]
        remote_node_10 = matrix[16:20,8:12]
        remote_node_11 = matrix[28:32,4:8]
        remote_node_12 = matrix[28:32,8:12]
        remote_node_13 = matrix[4:8,12:16]
        remote_node_14 = matrix[4:8,16:20]
        remote_node_15 = matrix[8:12,12:16]
        remote_node_16 = matrix[8:12,16:20]
        remote_node_17 = matrix[20:24,12:16]
        remote_node_18 = matrix[20:24,16:20]
        remote_node_19 = matrix[24:28,12:16]
        remote_node_20 = matrix[24:28,16:20]
        remote_node_21 = matrix[0:4,20:24]
        remote_node_22 = matrix[0:4,24:28]
        remote_node_23 = matrix[12:16,20:24]
        remote_node_24 = matrix[12:16,24:28]
        remote_node_25 = matrix[16:20,20:24]
        remote_node_26 = matrix[16:20,24:28]
        remote_node_27 = matrix[28:32,20:24]
        remote_node_28 = matrix[28:32,24:28]
        remote_node_29 = matrix[4:8,28:32]
        remote_node_30 = matrix[8:12,28:32]
        remote_node_31 = matrix[20:24,28:32]
        remote_node_32 = matrix[24:28,28:32]

        remote_node = np.vstack((remote_node_1,remote_node_2,remote_node_3,remote_node_4,remote_node_5,remote_node_6,remote_node_7,remote_node_8,remote_node_9,remote_node_10,remote_node_11,remote_node_12,remote_node_13,remote_node_14,remote_node_15,remote_node_16,remote_node_17,remote_node_18,remote_node_19,remote_node_20,remote_node_21,remote_node_22,remote_node_23,remote_node_24,remote_node_25,remote_node_26,remote_node_27,remote_node_28,remote_node_29,remote_node_30,remote_node_31,remote_node_32))
        #print(remote_node)
        remote_high = np.max(remote_node)
        remote_low = np.min(remote_node)
        remote_mean = round(np.mean(remote_node),1)
        remote_node_bandwidth="Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(remote_low/1000,1)) + "-" + str(round(remote_mean/1000,1)) + "-" + str(round(remote_high/1000,1))+" GB/sec"
        print(remote_node_bandwidth)


        #calculate far_remote node
        far_remote_node_1 = matrix[12:16,0:4]
        far_remote_node_2 = matrix[16:20,0:4]
        far_remote_node_3 = matrix[28:32,0:4]
        far_remote_node_4 = matrix[8:12,4:8]
        far_remote_node_5 = matrix[4:8,8:12]
        far_remote_node_6 = matrix[20:24,4:8]
        far_remote_node_7 = matrix[20:24,8:12]
        far_remote_node_8 = matrix[24:28,4:8]
        far_remote_node_9 = matrix[24:28,8:12]
        far_remote_node_10 = matrix[0:4,12:16]
        far_remote_node_11 = matrix[0:4,16:20]
        far_remote_node_12 = matrix[16:20,12:16]
        far_remote_node_13 = matrix[12:16,16:20]
        far_remote_node_14 = matrix[28:32,12:16]
        far_remote_node_15 = matrix[28:32,16:20]
        far_remote_node_16 = matrix[4:8,20:24]
        far_remote_node_17 = matrix[4:8,24:28]
        far_remote_node_18 = matrix[8:12,20:24]
        far_remote_node_19 = matrix[8:12,24:28]
        far_remote_node_20 = matrix[24:28,20:24]
        far_remote_node_21 = matrix[20:24,24:28]
        far_remote_node_22 = matrix[0:4,28:32]
        far_remote_node_23 = matrix[12:16,28:32]
        far_remote_node_24 = matrix[16:20,28:32]

        far_remote_node = np.vstack((far_remote_node_1,far_remote_node_2,far_remote_node_3,far_remote_node_4,far_remote_node_5,far_remote_node_6,far_remote_node_7,far_remote_node_8,far_remote_node_9,far_remote_node_10,far_remote_node_11,far_remote_node_12,far_remote_node_13,far_remote_node_14,far_remote_node_15,far_remote_node_16,far_remote_node_17,far_remote_node_18,far_remote_node_19,far_remote_node_20,far_remote_node_21,far_remote_node_22,far_remote_node_23,far_remote_node_24))
        #print(far_remote_node)
        far_remote_high = np.max(far_remote_node)
        far_remote_low = np.min(far_remote_node)
        far_remote_mean = round(np.mean(far_remote_node),1)
        far_remote_node_bandwidth="Far Remote Node Memory Bandwidth (Low-Avg-High) is " + str(round(far_remote_low/1000,1)) + "-" + str(round(far_remote_mean/1000,1)) + "-" + str(round(far_remote_high/1000,1))+" GB/sec"
        print(far_remote_node_bandwidth)
        
        with open("mlc_data","r") as f:
            for line in f.readlines():
                if line.startswith("ALL Reads"):
                    value=float(line.strip().split(":")[1])/1000
                    all_reads_speed="ALL Reads speed is " + str(round(value,2))+" GB/s"
                    print(all_reads_speed)
                if line.startswith("3:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_3_1="3:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_3_1)
                if line.startswith("2:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_2_1="2:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_2_1)
                if line.startswith("1:1 Reads-Writes"):
                    value=float(line.strip().split(":")[2])/1000
                    r_w_1_1="1:1 Reads-Writes is " + str(round(value,2))+" GB/s"
                    print(r_w_1_1)   
                if line.startswith("Stream-triad like"):
                    value=float(line.strip().split(":")[1])/1000
                    stream_triade_like_speed="Stream_triad like speed is " + str(round(value,2))+" GB/s"
                    print(stream_triade_like_speed)

        if os.path.exists("mlc_spv_data_8s32numa.log"):
            Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            target = str(os.getcwd()) + '/' + 'mlc_spv_data_8s32numa' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_spv_data_8s32numa.log",target) 
        #redirect 'print' output to a file
        sys.stdout=open("mlc_spv_data_8s32numa","w")
        print(local_node_latency)
        print(near_local_node_latency)
        print(remote_node_latency)
        print(far_remote_node_latency)
        print(local_node_bandwidth)
        print(near_local_node_bandwidth)
        print(remote_node_bandwidth)
        print(far_remote_node_bandwidth)
        print(all_reads_speed)
        print(r_w_3_1)
        print(r_w_2_1)
        print(r_w_1_1)
        print(stream_triade_like_speed)
        sys.stdout.close() 
        subprocess.call("cp mlc_data mlc_data_8s32numa", shell=True)


    if numa_type == "1":
        run_1s4numa()
    elif numa_type == "2":
        run_2s2numa()
    elif numa_type == "3":
        run_2s4numa()
    elif numa_type == "4":
        run_2s8numa()
    elif numa_type == "5":
        run_4s4numa()
    elif numa_type == "6":
        run_4s8numa()
    elif numa_type == "7":
        run_4s16numa() 
    elif numa_type == "8":
        run_8s8numa()
    elif numa_type == "9":
        run_8s16numa()
    elif numa_type == "10":
        run_8s32numa()
    else:
        print("Your input configutation is not in the support list, please double check.")
# main program ###
def main():
    check_python_module()
    check_for_requirements()
    run_mlc()
    data_treatment()
    

                    
if __name__ == "__main__":
    
    main()    

 
