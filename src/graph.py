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
        x_vals.append(n)
        y_vals.append(data[n].total_seconds())


    plt.xticks(x_vals)
    plt.xlabel('Number of Threads')
    plt.ylabel('Execution Time (sec)')
    plt.title(f"Time Execution x Number of Threads ({r_times} repetitions, {k_secs} sec interval)")
    plt.plot(x_vals, y_vals, marker='o')
    plt.show()


if __name__ == "__main__":

    combs = [(10,2),(5,1),(3,0)]

    for test_case in combs:
        r_times, k_secs = test_case
        plot_graph(r_times, k_secs)