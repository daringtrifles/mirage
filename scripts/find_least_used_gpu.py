import pynvml
import numpy as np
import subprocess

def get_gpu_utilization():
    """Get GPU memory and utilization information for all GPUs"""
    pynvml.nvmlInit()
    device_count = pynvml.nvmlDeviceGetCount()
    
    gpu_info = []
    for i in range(device_count):
        #if i == 0: continue
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
        
        gpu_info.append({
            'gpu_id': i,
            'memory_used': info.used,
            'memory_total': info.total,
            'memory_percent': (info.used / info.total) * 100,
            'gpu_utilization': utilization.gpu,
            'memory_utilization': utilization.memory
        })
    
    pynvml.nvmlShutdown()
    return gpu_info

def find_least_used_gpu():
    """Find the least utilized GPU based on memory usage and GPU utilization"""
    gpu_info = get_gpu_utilization()
    
    # Calculate a combined score for each GPU
    for gpu in gpu_info:
        # Weight memory usage more heavily (70%) than GPU utilization (30%)
        gpu['score'] = (gpu['gpu_utilization'] * 0.8)
    
    # Sort by score to find least used GPU
    gpu_info.sort(key=lambda x: x['score'])
    least_used = gpu_info[0]
    
    print("\nGPU Utilization Summary (from pynvml):")
    print("-" * 50)
    for gpu in gpu_info:
        print(f"GPU {gpu['gpu_id']}:")
        print(f"  Memory Usage: {gpu['memory_percent']:.1f}%")
        print(f"  GPU Utilization: {gpu['gpu_utilization']}%")
        print(f"  Memory Utilization: {gpu['memory_utilization']}%")
        print(f"  Combined Score: {gpu['score']:.1f}")
        print("-" * 50)
    
    print("\nCurrent nvidia-smi output:")
    print("-" * 50)
    subprocess.run(['nvidia-smi'], check=True)
    print("-" * 50)
    
    print(f"\nLeast used GPU: {least_used['gpu_id']}")
    print(f"Memory Usage: {least_used['memory_percent']:.1f}%")
    print(f"GPU Utilization: {least_used['gpu_utilization']}%")
    print(f"Memory Utilization: {least_used['memory_utilization']}%")
    
    return {
        'gpu_id': least_used['gpu_id'],
        'memory_percent': least_used['memory_percent'],
        'gpu_utilization': least_used['gpu_utilization'],
        'memory_utilization': least_used['memory_utilization']
    }

if __name__ == "__main__":
    try:
        gpu_info = find_least_used_gpu()
        print(f"\nReturned GPU info: {gpu_info}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure you have NVIDIA drivers installed and nvidia-smi is working.") 