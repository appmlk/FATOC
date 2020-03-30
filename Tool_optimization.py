# coding=utf-8
from __future__ import division

def Sus2Rank_addOne(sus):
    sus_sort = vaule_sort(sus)
    keys = []
    for item in sus_sort:
        keys.append(item[0] + 1)
    return keys

def clean_cov(covMatrix_int, fault_location):
    code_num = len(covMatrix_int[0])
    test_num = len(covMatrix_int)
    code_to_complete = {}
    rm_list = []
    temp = 0
    for index1 in range(code_num):
        if covMatrix_int[0][index1] == 2:
            rm_list.append(index1)
        else:
            code_to_complete[temp] = index1
            temp += 1

    rm_list.sort(reverse=True)
    for index in rm_list:
        for index3 in range(len(fault_location)):
            if index <= fault_location[index3]:
                fault_location[index3] -= 1

    for index1 in reversed(range(test_num)):
        for item in rm_list:
            del covMatrix_int[index1][item]

    return covMatrix_int, fault_location, code_to_complete,rm_list

def clean_cov_ready(covMatrix_int, fault_location,rm_list):
    code_num = len(covMatrix_int[0])
    test_num = len(covMatrix_int)
    code_to_complete = {}
    temp = 0
    for index1 in range(code_num):
        if index1 not in rm_list:
            code_to_complete[temp] = index1
            temp += 1

    for index in rm_list:
        for index3 in range(len(fault_location)):
            if index <= fault_location[index3]:
                fault_location[index3] -= 1

    for index1 in reversed(range(test_num)):
        for item in rm_list:
            del covMatrix_int[index1][item]

    return covMatrix_int, fault_location, code_to_complete

def vaule_sort(sus_oc):
    dict = sorted(sus_oc.items(), key=lambda d: d[1], reverse=True)
    return dict

#把数组中重复的内容合并
def getCF(a):
    list_position_name = [str(i) for i in a]
    list_price_positoin_address = []
    for i in list_position_name:
        address_index = [x for x in range(len(list_position_name)) if list_position_name[x] == i]
        list_price_positoin_address.append([i, address_index])
    dict_address = dict(list_price_positoin_address)
    dict_location = {}
    big_to_little = {}
    for key in dict_address:
        dict_location[list_position_name.index(key)] = dict_address[key]
    for key in dict_location:
        for item in dict_location[key]:
            big_to_little[item] = key
    return dict_location, big_to_little