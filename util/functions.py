import open3d as o3d
import os
import numpy as np
import bisect
import cv2

def extract_timestamp(file_name):
    # 提取文件名中的时间戳部分（假设格式如 "file_<秒数>_<纳秒数>.txt"）
    # 先移除前缀 "file_" 和后缀 ".txt"
    timestamp, _ = os.path.splitext(file_name)
    sec, nsec = map(int, timestamp.split('_'))
    return sec, nsec

def read_odom(path_odom):
    odom_lists = []
    with open(path_odom) as file:
        for line in file:
            line = line.strip()
            data = list(map(float, line.split()))
            odom_lists.append(data)

    return odom_lists

def odom_to_T_r(odom_lists, i):
    """
        将第i行对应的位姿信息转换成旋转矩阵T和平移向量t
    """
    odom = odom_lists[i]

    R = np.zeros((3, 3))
    t = np.zeros((3, 1))

    R[0, :3] = odom[0:3]
    R[1, :3] = odom[4:7]
    R[2, :3] = odom[8:11]

    t[0] = odom[3]
    t[1] = odom[7]
    t[2] = odom[11]
    t = t.flatten()

    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t

    return T, R, t

def parse_timestamp(timestamp_str):
    seconds, nanoseconds = timestamp_str.split('_')
    return int(seconds), int(nanoseconds)

def find_closest_timestamp(timestamps, timestamp):
    """
        从时间戳组中找到最接近时间戳的时间戳。
    """
    # 使用bisect模块的bisect_left函数查找插入点
    idx = bisect.bisect_left(timestamps, timestamp, key=parse_timestamp)
    
    # 边界条件处理
    if idx == 0:
        return timestamps[0]
    elif idx == len(timestamps):
        return timestamps[-1]
    
    # 找到最接近的时间戳
    before = timestamps[idx - 1]
    after = timestamps[idx]
    
    # 比较哪个时间戳更接近雷达时间戳
    if timestamp - before < after - timestamp:
        return before, idx - 1
    else:
        return after, idx
    
def path_to_timestamp(file_path):
    """
        单个路径转为整数时间戳
    """
    filename = os.path.basename(file_path)      # 去除父文件
    timestamp, _ = os.path.splitext(filename)   # 去除后缀
    timestamp = timestamp.replace('_', '.')     # 下划线转为点.
    timestamp = float(timestamp)
    return timestamp

def T_to_r_t(T):
    R = T[:3, :3]
    r, _ = cv2.Rodrigues(R)

    t = T[:3, 3]

    return r, t

def read_pcd_lists(directory_pcd):
    pcd_lists = []

    for file_name in sorted(os.listdir(directory_pcd), key=lambda f: extract_timestamp(f)):
        if file_name.endswith(".pcd"):
            file_path = os.path.join(directory_pcd, file_name)
            pcd_lists.append(file_path)
    return pcd_lists

def read_image_lists(directory_image):
    image_lists = []

    for file_name in sorted(os.listdir(directory_image), key=lambda f: extract_timestamp(f)):
        if file_name.endswith(".png"):
            file_path = os.path.join(directory_image, file_name)
            image_lists.append(file_path)
    return image_lists