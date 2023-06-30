#!/usr/bin/python3

########################################################################
#                                                                      #
#                                                                      #
# PURPOSE: A script for 1 Sockets 4 NUMA nodes MLC test                #
#                                                                      #
# VERSION: 1.0.0                                                       #
#                                                                      #
# Author: Peter Xu  
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

def check_nps():
    if int(get_numa_node_count()/get_socket_count())!= 4:
        print("Please set NPS=4 in the UEFI")
        return False
    else:
        return True


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
    print("Downloading mlc from Intel website")
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

def check_for_requirements():
    if not is_numactl_installed():
        sys.exit("numactl is required but not found! Exiting.\n")
    if not check_nps():
       sys.exit("NPS=2 is required, please change the setting in the UEFI")
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
        subprocess.check_output("echo 4000 > /proc/sys/vm/nr_hugepages", shell=True)
        subprocess.check_output("modprobe msr", shell=True)
        if os.path.exists("mlc_test_nps4.log"):
            target = str(os.getcwd()) + '/' + 'mlc_test_nps4' + '_' + str(Current_Time) + '.log'
            os.rename("mlc_test_nps4.log",target)
        print(run_shell("./mlc | tee mlc_test_nps4.log"))
        print("mlc test is done, checking the result now")

#run_mlc()

#data treatment
def data_treatment():
    lat = []
    count = 0
    with open("mlc_test_nps4.log","r") as f:
        for line in f.readlines():
            #locate latency data
            if line.strip().startswith("0"):
                break
            count +=1


    with open("mlc_test_nps4.log","r") as x:
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
    with open("mlc_test_nps4.log","r") as f:
        for line in f.readlines():
            #locate bandwith data
            if line.strip().startswith("0") and count_2 > 10:
                break
            count_2 +=1


    with open("mlc_test_nps4.log","r") as x:
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

    

    with open("mlc_test_nps4.log","r") as f:
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

    if os.path.exists("mlc_spv_data_nps4.log"):
        Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        target = str(os.getcwd()) + '/' + 'mlc_spv_data_nps4' + '_' + str(Current_Time) + '.log'
        os.rename("mlc_spv_data_nps4.log",target) 

    #redirect 'print' output to a file
    sys.stdout=open("mlc_spv_data_nps4.log","w")
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

    #print(matrix)
    '''
    #Latency 2d array visualization
    #set up grid
    nx, ny = 8, 8
    x = range(nx)
    y = range(ny)

    hf = plt.figure()
    ha = hf.add_subplot(111, projection='3d')

    X,Y = np.meshgrid(x, y)
    ha.plot_surface(X, Y, matrix)
    ha.set(xlim=[8,0],ylim=[0,8],title='Numa Node Latency(ns)',ylabel='Node',xlabel='Node')
    #hf.suptitle("Numa Node Latency")
    plt.show()
    '''
    #Generate chart 

    x1 = list(range(4))
    x2 = list(range(12))
    y = list(range(0,400,20))
    near_local_node_1 = list(np.array(near_local_node).flatten())
    plt.plot(x1,local_node,marker='*',color='green',label=u'local node')
    plt.plot(x2,near_local_node_1,marker='o',color='blue',label=u'near local node')
    plt.ylabel(u'Latency(ns)')
    plt.xlim(0,12)
    plt.ylim(0,400)
    plt.title('MLC Latencies(in ns)')
    plt.legend()
    plt.show(block=False)
    plt.pause(3)
    if os.path.exists("mlc_nps4.jpg"):
        Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        target = str(os.getcwd()) + '/' + 'mlc_nps4' + '_' + str(Current_Time) + '.jpg'
        os.rename("mlc_nps4.jpg",target)
    plt.savefig('mlc_nps4.jpg')
    plt.close()



    x1 = list(range(4))
    x2 = list(range(12))
    y = list(range(0,400,10))

    near_local_node_1_bw = list(np.array(near_local_node_bw).flatten()/1000)
    local_node_1_bw = local_node_bw/1000
    plt.plot(x1,local_node_1_bw,marker='*',color='green',label=u'local node')
    plt.plot(x2,near_local_node_1_bw,marker='o',color='blue',label=u'near local node')
    plt.ylabel(u'Bandwidth(GB/s)')
    plt.xlim(0,12)
    plt.ylim(0,400)
    plt.title('MLC Bandwidth(in GB/s)')
    plt.legend()
    plt.show(block=False)
    plt.pause(3)
    if os.path.exists("mlc_bw_nps4.jpg"):
        Current_Time=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        target = str(os.getcwd()) + '/' + 'mlc_bw_nps4' + '_' + str(Current_Time) + '.jpg'
        os.rename("mlc_bw_nps4.jpg",target)
    plt.savefig('mlc_bw_nps4.jpg')
    plt.close()

# main program ###
def main():
    check_python_module()
    check_for_requirements()
    run_mlc()
    data_treatment()
    

                    
if __name__ == "__main__":
    
    main()    

 
