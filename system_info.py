import psutil
from datetime import datetime
import pandas as pd
import time
import os
import threading
import time
import GPUtil

interval=0.05
def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


class SystemInfo(object):
    def __init__(
        self, cpu_usage=0, memory_usage=0, disk_usage=0, network_usage=0, gpu_usage=0
    ):
        self.cpu_usage = cpu_usage
        self.memory_usage = memory_usage
        self.disk_usage = disk_usage
        self.network_usage = network_usage
        self.gpu_usage = gpu_usage

    # def __add__(self, other):
    #     cpu_usage = self.cpu_usage + other.cpu_usage
    #     memory_usage = self.memory_usage + other.memory_usage
    #     disk_usage = self.disk_usage + other.disk_usage
    #     network_usage = self.network_usage + other.network_usage
    #     gpu_usage = self.gpu_usage + other.gpu_usage
    #     return SystemInfo(cpu_usage, memory_usage, disk_usage, network_usage, gpu_usage)

    @threaded
    def get_cpu_usage(self):
        self.cpu_usage = psutil.cpu_percent(interval)

    @threaded
    def get_memory_usage(self):
        self.memory_usage = psutil.virtual_memory().percent

    @threaded
    def get_disk_usage(self):
        io_counters = psutil.disk_io_counters()
        read_bytes = io_counters.read_bytes
        write_bytes = io_counters.write_bytes
        before = read_bytes + write_bytes
        time.sleep(interval)
        io_counters = psutil.disk_io_counters()
        read_bytes = io_counters.read_bytes
        write_bytes = io_counters.write_bytes
        after = read_bytes + write_bytes
        self.disk_usage = after - before

    @threaded
    def get_gpu_usage(self):
        GPUs = GPUtil.getGPUs()
        gpu_usage = GPUs[0].load
        self.gpu_usage = gpu_usage

    @threaded
    def get_network_usage(self):
        before = (
            psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        )
        time.sleep(interval)
        after = (
            psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        )
        self.network_usage = after - before

    def get_data(self):
        handle1 = self.get_cpu_usage()
        handle2 = self.get_memory_usage()
        handle3 = self.get_disk_usage()
        handle4 = self.get_gpu_usage()
        handle5 = self.get_network_usage()
        handle1.join()
        handle2.join()
        handle3.join()
        handle4.join()
        handle5.join()

    def get_params(self):
        return [
            self.cpu_usage/100,
            self.memory_usage/100,
            self.disk_usage/(1024*1024),
            self.network_usage/(1024*1024),
            self.gpu_usage/100,
        ]

    def __str__(self) -> str:
        return (
            str(self.cpu_usage)
            + " "
            + str(self.memory_usage)
            + " "
            + str(self.disk_usage)
            + " "
            + str(self.network_usage)
            + " "
            + str(self.gpu_usage)
            + " "
        )


# class myThread(threading.Thread):
#     def __init__(self, threadID, processes, outputs):
#         threading.Thread.__init__(self)
#         self.threadID = threadID
#         self.processes = processes
#         self.outputs = outputs

#     def run(self):
#         out = get_processes_info(self.processes, self.exclude_pid)
#         self.outputs[self.threadID] = out


# def chunks(lst, n):
#     for i in range(0, len(lst), n):
#         yield lst[i : i + n]


# process_list = list(psutil.process_iter())

# threads = 20


# def measure(n_threads):
#     threads: list[myThread] = []

#     length_chunk = len(process_list) / n_threads +1
#     length_chunk = int(length_chunk)
#     list_chunks = list(chunks(process_list, length_chunk))

#     pid = psutil.Process().pid
#     n_threads=len(list_chunks)
#     outputs = [None] * n_threads
#     for i in range(n_threads):
#         t = myThread(i, list_chunks[i], outputs, pid)
#         threads.append(t)
#         t.start()

#     for t in threads:
#         t.join()

#     system_info = SystemInfo()
#     for out in outputs:
#         system_info += out


#     GPUs = GPUtil.getGPUs()
#     gpu_usage=GPUs[0].load
#     system_info.gpu_usage=gpu_usage
#     system_info.network_usage=psutil.net_io_counters().bytes_sent+psutil.net_io_counters().bytes_recv
#     print(system_info)

# measure(threads)
