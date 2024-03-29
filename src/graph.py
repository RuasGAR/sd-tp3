import os
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')  # Set the backend to TkAgg 
import matplotlib.pyplot as plt

LOGS_ROOT_DIR = "src/logs"
TIME_FORMAT = "%H:%M:%S.%f"

def read_time_data(r_times,k_secs):
    
    data = {}

    fdir = f"r={r_times}_k={k_secs}"
    
    full_path = os.path.join(LOGS_ROOT_DIR,fdir)

    for n_dir in os.listdir(full_path):
          
        n = int(n_dir.split("=")[1])

        with open(os.path.join(full_path,n_dir,"info.txt"), 'r') as f:

            for index in range(1,3):
                
                if (index == 1):
                    line = f.readline().split("-")[-1].split(" ")[1].rstrip("\n") 
                    start_t = datetime.strptime(line, TIME_FORMAT)
            
                elif(index == 2):
                    line = f.readline().split("-")[-1].split(" ")[1].rstrip("\n") 
                    end_t = datetime.strptime(line, TIME_FORMAT)
                else:
                    break

            diff_t = end_t - start_t

            data[n] = diff_t

    return data


def plot_graph(r_times,k_secs):
    
    data = read_time_data(r_times,k_secs)
    
    x_vals = []
    y_vals = []
    
    for n in sorted(data.keys()):
        y_vals.append(n)
        x_vals.append(data[n].total_seconds())

    for i in range(len(x_vals)):
        print(f"r = {r_times}, k = {k_secs}, n = {y_vals[i]} --> t = {x_vals[i]}")

    plt.yticks(y_vals)
    plt.ylabel('Number of Threads')
    plt.xlabel('Execution Time (sec)')
    plt.title(f"Number of Threads x Time Execution ({r_times} repetitions, {k_secs} sec interval)")
    plt.plot(x_vals, y_vals, marker='o')
    plt.show()


if __name__ == "__main__":

    combs = [(10,2),(5,1),(3,0)]

    for test_case in combs:
        r_times, k_secs = test_case
        plot_graph(r_times, k_secs)