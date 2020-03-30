# -*- coding: utf-8 -*-
from __future__ import division

import time

import math
import sys
from pyclustering.cluster import cluster_visualizer
from pyclustering.cluster.optics import optics, ordering_analyser, ordering_visualizer
from pyclustering.samples.definitions import FCPS_SAMPLES
from pyclustering.utils import read_sample
import numpy as np
import scipy.signal as signal


def vaule_sort(dict):
    dict = sorted(dict.items(), key=lambda d: d[1], reverse=True)
    return dict

def deal_sample_optics(sample_path, show_pic1, show_pic2):
    sample = read_sample(sample_path)
    radius = sys.maxsize
    neighbors = 1
    optics_instance = optics(sample, radius, neighbors)
    # 进行聚类
    optics_instance.process()
    # 获得聚类结果
    clusters = optics_instance.get_clusters()
    noise = optics_instance.get_noise()
    ordering = optics_instance.get_ordering()
    # 可视化聚类内部结构信息
    analyser = ordering_analyser(ordering)

    x = np.array(analyser.cluster_ordering)
    max_index = signal.argrelextrema(x, np.greater)[0].tolist()
    max_value = x[signal.argrelextrema(x, np.greater)].tolist()
    max_value.sort(reverse=True)

    dict = {}
    point_x = []
    point_y = []
    for index in range(len(max_value)):
        if index == len(max_value) - 1:
            point_x.append(index + 1)
            point_y.append(max_value[index])
            dict[index + 1] = max_value[index]
        else:
            point_x.append(index + 1)
            point_y.append(max_value[index] - max_value[index + 1])
            dict[index + 1] = max_value[index] - max_value[index + 1]

    dict = vaule_sort(dict)

    clusters_num = dict[0][0] + 1
    optics_instance = optics(sample, radius, neighbors, clusters_num)
    # 进行聚类
    optics_instance.process()
    # 获得聚类结果
    clusters = optics_instance.get_clusters()
    noise = optics_instance.get_noise()
    ordering = optics_instance.get_ordering()
    analyser = ordering_analyser(ordering)

    # 可视化聚类内部结构信息
    if show_pic1:
        try:
            if len(clusters) == 1:
                ordering_visualizer.show_ordering_diagram(analyser)
            else:
                ordering_visualizer.show_ordering_diagram(analyser, len(clusters))
        except:
            pass

    # 可视化聚类结果
    if show_pic2:
        visualizer = cluster_visualizer()
        visualizer.append_clusters(clusters, sample)
        visualizer.show()


def deal_optics(sample, radius=sys.maxsize, neighbors=1):
    # print(len(sample))
    # print(radius)
    # print(neighbors)
    optics_instance = optics(sample, radius, neighbors)
    # 进行聚类
    optics_instance.process()
    # 获得聚类结果
    ordering = optics_instance.get_ordering()

    # 可视化聚类内部结构信息
    analyser = ordering_analyser(ordering)
    x = np.array(analyser.cluster_ordering)
    max_value = x[signal.argrelextrema(x, np.greater)].tolist()
    max_value.sort(reverse=True)

    dict = {}
    point_x = []
    point_y = []
    for index in range(len(max_value)):
        if index == len(max_value) - 1:
            point_x.append(index + 1)
            point_y.append(max_value[index])
            dict[index + 1] = max_value[index]
        else:
            point_x.append(index + 1)
            point_y.append(max_value[index] - max_value[index + 1])
            dict[index + 1] = max_value[index] - max_value[index + 1]

    if len(dict)!=0:
        dict = vaule_sort(dict)
        clusters_num = dict[0][0] + 1
        # print("开始指定聚类数量:"+str(clusters_num))
        optics_instance = optics(sample, radius, neighbors, clusters_num)
        # 进行聚类
        optics_instance.process()
        radius = optics_instance.get_radius()
        optics_instance = optics(sample, radius, neighbors)
        optics_instance.process()
    else:
        clusters_num=1

    # 获得聚类结果
    clusters = optics_instance.get_clusters()
    noise = optics_instance.get_noise()
    ordering = optics_instance.get_ordering()
    analyser = ordering_analyser(ordering)
    optics_objects = optics_instance.get_optics_objects()

    # if clusters_num!=1:
    #     print("类簇数:"+str(clusters_num))
    #     print("聚类结果:" + str(len(clusters)))

    return clusters, noise, ordering, analyser,optics_objects


def pick_best(clusters, optics_objects):
    min_sum = -1
    min_sum_average = -1
    find_flag = -1#最好类簇标记

    if len(clusters)!=1:
        for index1 in range(len(clusters)):
            min_sum_temp = 0
            tempdic={}

            for index2 in range(len(clusters[index1])):
                value = optics_objects[clusters[index1][index2]].reachability_distance
                if value != None:
                    tempdic[index2]=value
                    min_sum_temp += value
            min_sum_average_temp = min_sum_temp / len(clusters[index1])

            if find_flag==-1 or min_sum_average>min_sum_average_temp:
                find_flag=index1
                min_sum_average=min_sum_average_temp
                min_sum=min_sum_temp
    else:
        min_sum=0
        min_sum_average=0
        find_flag=0
    return find_flag,clusters[find_flag],min_sum,min_sum_average


def dealAll(sample):
    # print(sample)
    cluster = [0]
    cluster_content=[[0]]
    if len(sample)>1:
        clusters, noise, ordering, analyser,optics_objects = deal_optics(sample)
        clusters_flag, cluster_content, min_sum, min_sum_average = pick_best(clusters, optics_objects)
        cluster = [clusters_flag]
        cluster_content = [cluster_content]
    return cluster, cluster_content


if __name__ == "__main__":

    # deal_sample(FCPS_SAMPLES.SAMPLE_LSUN,False,True)  # 三个方块
    # deal_sample(FCPS_SAMPLES.SAMPLE_CHAINLINK,False,True)  # 两个圈
    # deal_sample(FCPS_SAMPLES.SAMPLE_TWO_DIAMONDS,False,True)  # 两个菱形
    time_start = time.time()
    sample = read_sample(FCPS_SAMPLES.SAMPLE_LSUN)
    cluster, cluster_content = dealAll(sample)

    # sample = read_sample(FCPS_SAMPLES.SAMPLE_CHAINLINK)
    # clusters, noise, ordering, analyser = deal(sample)
    # sample = read_sample(FCPS_SAMPLES.SAMPLE_TWO_DIAMONDS)
    # clusters, noise, ordering, analyser = deal(sample)
    time_end = time.time()
    print('time cost', time_end - time_start, 's')
    print(cluster)