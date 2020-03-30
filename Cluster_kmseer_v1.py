# -*- coding: utf-8 -*-
from __future__ import division

import operator
import math
import numpy
import Tool_optimization

def get_single_mseer_distance(list1, list2):
    code_num = len(list1)
    temp = 0
    for i in range(code_num):
        for j in range(code_num):
            if j <= i:
                continue
            A = list1[i] - list1[j]
            b = list2[i] - list2[j]
            if A * b < 0:
                # temp+=1
                temp += 1 / list1[i] + 1 / list1[j] \
                        + 1 / list2[i] + 1 / list2[j]
            else:
                continue
    return temp

def get_distance_mseer(rank_limit):
    # print("正在优化聚类")
    dict_location, big_to_little = Tool_optimization.getCF(rank_limit)
    little_to_index = {}
    # print("优化聚类结束")
    # print(dict_location)

    flag1 = 0
    distance = []
    for x_index in dict_location:
        # print(x_index)
        x = dict_location[x_index][0]
        little_to_index[x] = flag1
        distance_temp = []
        flag2 = 0
        # print("mseer distance " + str(flag1) + "/" + str(len(dict_location)))
        for y_index in dict_location:
            # print(y_index)
            y = dict_location[y_index][0]
            #记录
            # print(str(flag1) + " " + str(flag2) + "/" + str(len(dict_location)))
            if flag1 == flag2:
                distance_temp.append(0)
            elif flag1 > flag2:
                distance_temp.append(distance[flag2][flag1])
            else:
                temp = get_single_mseer_distance(rank_limit[x], rank_limit[y])
                distance_temp.append(temp)
            flag2 += 1
        flag1 += 1
        distance.append(distance_temp)

    distance_full = []
    for x in range(len(rank_limit)):
        distance_temp = []
        for y in range(len(rank_limit)):
            distance_temp.append(
                distance[little_to_index[big_to_little[x]]][little_to_index[big_to_little[y]]])
        distance_full.append(distance_temp)
    return distance_full

def winsorize(list, baifenbi, up):
    list.sort()
    if up:
        cut = int(math.ceil(len(list) * baifenbi / 100))
    else:
        cut = int(math.floor(len(list) * baifenbi / 100))
    min_v = list[cut]
    max_v = list[len(list) - 1 - cut]
    for i in range(cut):
        list[i] = min_v
        list[len(list) - 1 - i] = max_v
    sum = 0
    for i in list:
        sum = sum + i
    ave = sum / len(list)
    return ave

def iteration(cluster, distance, in_vector):
    cluster_content = []
    for index in range(len(cluster)):
        cluster_content.append([cluster[index]])
    for test_index in range(len(in_vector)):
        if test_index not in cluster and in_vector[test_index] == 1:
            temp = []
            for cluster_index in range(len(cluster)):
                temp.append(distance[test_index][cluster[cluster_index]])
            belong = temp.index(min(temp))
            cluster_content[belong].append(test_index)

    cluster_new = []
    for cluster_index in range(len(cluster)):
        cluster_inner_sum = []
        for cluster_inner_index1 in range(len(cluster_content[cluster_index])):
            cluster_inner_temp = 0
            for cluster_inner_index2 in range(len(cluster_content[cluster_index])):
                cluster_inner_temp += distance[cluster_content[cluster_index][cluster_inner_index1]][
                    cluster_content[cluster_index][cluster_inner_index2]]
            cluster_inner_sum.append(cluster_inner_temp)
        cluster_new.append(
            cluster_content[cluster_index][cluster_inner_sum.index(min(cluster_inner_sum))])

    cmp_result = operator.eq(cluster, cluster_new)
    return cluster_content, cluster_new, cmp_result

def deal_mseer(faultTest_num,distance,in_vector_limit):
    cluster = []  # 聚类中心在fail_test_index中的index
    cluster_content = []
    if faultTest_num < 1:
        return None, None
    elif faultTest_num == 1:
        # print("Warn faultTest_num=1")
        cluster.append(0)
        cluster_content.append([])
    else:
        temp = []
        for i in range(faultTest_num):
            for j in range(faultTest_num):
                if j < i:
                    temp.append(distance[i][j])
        mean = winsorize(temp, 5, False)  # 向下取整
        W = mean / 2
        if W == 0:
            # print("Warn W=0")
            cluster.append(0)
            cluster_content.append([])
        else:
            A = 4 / (W * W)

            potential = []
            for i in range(faultTest_num):
                P = 0
                for j in range(faultTest_num):
                    if i != j or True:
                        P_single = math.exp(
                            -1 * A * numpy.square(distance[i][j]))
                        # P_single=round(P_single,3)
                        P += P_single
                potential.append(round(P, 4))
                # potential.append(P)

            M = max(potential)
            M0 = M
            R = potential.index(M)
            cluster.append(R)
            cluster_content.append([])

            C = 1.5 * W
            B = 4 / (C * C)

            flag_step4 = True
            while flag_step4:
                for index in range(len(potential)):
                    temp1 = potential[index]
                    temp2 = M
                    temp3 = math.exp(
                        -1 * B * numpy.square(distance[index][R]))
                    potential[index] = temp1 - temp2 * temp3

                M = max(potential)
                R = potential.index(M)

                flag_stopping_criterion = True
                while flag_stopping_criterion:
                    if M > 0.5 * M0:
                        cluster.append(R)
                        cluster_content.append([])
                        break
                    elif M < 0.15 * M0:
                        flag_step4 = False
                        break
                    else:
                        temp = []
                        for index in range(len(cluster)):
                            temp1 = cluster[index]
                            temp.append(distance[R][temp1])
                        D_min = min(temp)

                        temp1 = D_min / W
                        temp2 = M / M0
                        temp3 = temp1 + temp2
                        if temp3 >= 1:
                            cluster.append(R)
                            cluster_content.append([])
                            continue
                        else:
                            potential[R] = 0
                            M = max(potential)
                            R = potential.index(M)
                            continue
    for index in range(len(cluster)):
        cluster[index] = cluster[index]
        cluster_content[index].append(cluster[index])

    # 开始聚类
    cluster_content, cluster_new, cmp_result = iteration(cluster, distance, in_vector_limit)

    while not cmp_result:
        cluster = cluster_new
        cluster_content, cluster_new, cmp_result = iteration(cluster, distance, in_vector_limit)

    return cluster,cluster_content

if __name__ == "__main__":
    pass