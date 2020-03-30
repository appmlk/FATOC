# coding=utf-8
from __future__ import division

import math

import Tool_localization
import Tool_optimization

def get_single_CC_distance(covMatrix, item1, item2):
    temp = 0
    for index in range(len(covMatrix[0])):
        if covMatrix[item1][index] != covMatrix[item2][index]:
            temp +=1
    temp = math.sqrt(temp)
    return temp

def get_single_CC_distance_weight(covMatrix, item1, item2, sus_tu):
    temp = 0
    for index in range(len(covMatrix[0])):
        if covMatrix[item1][index] != covMatrix[item2][index]:
            if sus_tu[index]>0:
                temp = temp + math.pow(sus_tu[index],2)
    temp = math.sqrt(temp)
    return temp

def get_distance_CC(covMatrix, fail_test, pass_test):
    cc_pro = {}
    distance = {}
    tf = len(fail_test)
    tp = len(pass_test)
    for pass_item_index in range(len(pass_test)):
        # print(str(pass_item_index)+"/"+str(len(pass_test)))
        pass_item = pass_test[pass_item_index]
        distance_temp = {}
        for pass_item2 in pass_test:
            if pass_item == pass_item2:
                continue
            elif pass_item2 in distance and pass_item in distance[pass_item2]:
                distance_temp[pass_item2] = distance[pass_item2][pass_item]
            else:
                temp = get_single_CC_distance(covMatrix, pass_item, pass_item2)
                distance_temp[pass_item2] = temp
        for fail_item in fail_test:
            if fail_item in distance and pass_item in distance[fail_item]:
                distance_temp[fail_item] = distance[fail_item][pass_item]
            else:
                temp = get_single_CC_distance(covMatrix, pass_item, fail_item)
                distance_temp[fail_item] = temp
        distance[pass_item] = distance_temp
        distance_temp_list = sorted(distance_temp.items(), key=lambda d: d[1], reverse=False)

        in_num = 0
        for item_index in range(len(distance_temp_list)):
            if item_index + 1 > tf:
                cc_pro[pass_item] = in_num / tf
                break
            # print(item)
            item = distance_temp_list[item_index][0]
            if item in fail_test:
                in_num += 1

    cc_pro_sum = 0
    for item in cc_pro:
        cc_pro_sum += cc_pro[item]

    ochiai_cc = {}
    dstar_cc = {}
    turantula_cc = {}
    op2_cc = {}
    crosstab_cc = {}
    ochiai_cc_new = {}

    ochiai_cc[1] = {}
    ochiai_cc[2] = {}
    ochiai_cc[3] = {}

    ochiai_cc_new[1] = {}
    ochiai_cc_new[2] = {}
    ochiai_cc_new[3] = {}

    dstar_cc[1] = {}
    dstar_cc[2] = {}
    dstar_cc[3] = {}

    turantula_cc[1] = {}
    turantula_cc[2] = {}
    turantula_cc[3] = {}

    op2_cc[1] = {}
    op2_cc[2] = {}
    op2_cc[3] = {}

    crosstab_cc[1] = {}
    crosstab_cc[2] = {}
    crosstab_cc[3] = {}
    for index in range(len(covMatrix[0])):
        fail_s = 0
        pass_s = 0
        cc_s = 0
        for pass_item in pass_test:
            if covMatrix[pass_item][index] == 1:
                pass_s += 1
                if pass_item in cc_pro:
                    cc_s += cc_pro[pass_item]
        for fail_item in fail_test:
            if covMatrix[fail_item][index] == 1:
                fail_s += 1
        a1, b1, c1 = Tool_localization.cal_ochiai_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)
        a2, b2, c2 = Tool_localization.cal_dstar_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)
        a3, b3, c3 = Tool_localization.cal_turantula_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)
        a4, b4, c4 = Tool_localization.cal_op2_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)
        a5, b5, c5 = Tool_localization.cal_crosstab_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)
        a6, b6, c6 = Tool_localization.cal_ochiai_cc_new(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)

        ochiai_cc[1][index] = a1
        ochiai_cc[2][index] = b1
        ochiai_cc[3][index] = c1

        ochiai_cc_new[1][index] = a6
        ochiai_cc_new[2][index] = b6
        ochiai_cc_new[3][index] = c6

        dstar_cc[1][index] = a2
        dstar_cc[2][index] = b2
        dstar_cc[3][index] = c2

        turantula_cc[1][index] = a3
        turantula_cc[2][index] = b3
        turantula_cc[3][index] = c3

        op2_cc[1][index] = a4
        op2_cc[2][index] = b4
        op2_cc[3][index] = c4

        crosstab_cc[1][index] = a5
        crosstab_cc[2][index] = b5
        crosstab_cc[3][index] = c5

    return cc_pro, ochiai_cc, dstar_cc, turantula_cc, op2_cc, crosstab_cc, ochiai_cc_new


def get_distance_CC_weight(covMatrix, sus_tar, fail_test, pass_test):
    cc_pro = {}
    distance = {}
    tf = len(fail_test)
    tp = len(pass_test)
    for pass_item_index in range(len(pass_test)):
        # print(str(pass_item_index)+"/"+str(len(pass_test)))
        pass_item = pass_test[pass_item_index]
        distance_temp = {}
        for pass_item2 in pass_test:
            if pass_item == pass_item2:
                continue
            elif pass_item2 in distance and pass_item in distance[pass_item2]:
                distance_temp[pass_item2] = distance[pass_item2][pass_item]
            else:
                temp = get_single_CC_distance(covMatrix, pass_item, pass_item2, sus_tar)
                distance_temp[pass_item2] = temp
        for fail_item in fail_test:
            if fail_item in distance and pass_item in distance[fail_item]:
                distance_temp[fail_item] = distance[fail_item][pass_item]
            else:
                temp = get_single_CC_distance(covMatrix, pass_item, fail_item, sus_tar)
                distance_temp[fail_item] = temp
        distance[pass_item] = distance_temp
        distance_temp_list = sorted(distance_temp.items(), key=lambda d: d[1], reverse=False)

        distance_max=-1
        for item_index in range(len(distance_temp_list)):
            value = distance_temp_list[item_index][1]
            if distance_max<value:
                distance_max=value

        fenzi = 0
        fenmu = 0
        for item_index in range(len(distance_temp_list)):
            if item_index + 1 > tf:
                cc_pro[pass_item] = fenzi / fenmu
                break
            # print(item)
            item = distance_temp_list[item_index][0]
            value = distance_temp_list[item_index][1]
            cha=distance_max-value
            fenmu += cha
            if item in fail_test:
                fenzi+=cha

        #传统距离非加权
        # in_num = 0
        # for item_index in range(len(distance_temp_list)):
        #     if item_index + 1 > tf:
        #         cc_pro[pass_item] = in_num / tf
        #         break
        #     # print(item)
        #     item = distance_temp_list[item_index][0]
        #     if item in fail_test:
        #         in_num += 1

    cc_pro_sum = 0
    for item in cc_pro:
        cc_pro_sum += cc_pro[item]

    ochiai_cc = {}
    dstar_cc = {}
    turantula_cc = {}
    op2_cc = {}
    crosstab_cc = {}
    ochiai_cc_new = {}

    ochiai_cc[1] = {}
    ochiai_cc[2] = {}
    ochiai_cc[3] = {}

    ochiai_cc_new[1] = {}
    ochiai_cc_new[2] = {}
    ochiai_cc_new[3] = {}

    dstar_cc[1] = {}
    dstar_cc[2] = {}
    dstar_cc[3] = {}

    turantula_cc[1] = {}
    turantula_cc[2] = {}
    turantula_cc[3] = {}

    op2_cc[1] = {}
    op2_cc[2] = {}
    op2_cc[3] = {}

    crosstab_cc[1] = {}
    crosstab_cc[2] = {}
    crosstab_cc[3] = {}
    for index in range(len(covMatrix[0])):
        fail_s = 0
        pass_s = 0
        cc_s = 0
        for pass_item in pass_test:
            if covMatrix[pass_item][index] == 1:
                pass_s += 1
                if pass_item in cc_pro:
                    cc_s += cc_pro[pass_item]
        for fail_item in fail_test:
            if covMatrix[fail_item][index] == 1:
                fail_s += 1
        a1, b1, c1 = Tool_localization.cal_ochiai_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)
        a2, b2, c2 = Tool_localization.cal_dstar_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)
        a3, b3, c3 = Tool_localization.cal_turantula_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)
        a4, b4, c4 = Tool_localization.cal_op2_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)
        a5, b5, c5 = Tool_localization.cal_crosstab_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)
        a6, b6, c6 = Tool_localization.cal_ochiai_cc_new(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s)

        ochiai_cc[1][index] = a1
        ochiai_cc[2][index] = b1
        ochiai_cc[3][index] = c1

        ochiai_cc_new[1][index] = a6
        ochiai_cc_new[2][index] = b6
        ochiai_cc_new[3][index] = c6

        dstar_cc[1][index] = a2
        dstar_cc[2][index] = b2
        dstar_cc[3][index] = c2

        turantula_cc[1][index] = a3
        turantula_cc[2][index] = b3
        turantula_cc[3][index] = c3

        op2_cc[1][index] = a4
        op2_cc[2][index] = b4
        op2_cc[3][index] = c4

        crosstab_cc[1][index] = a5
        crosstab_cc[2][index] = b5
        crosstab_cc[3][index] = c5

    return cc_pro, ochiai_cc, dstar_cc, turantula_cc, op2_cc, crosstab_cc, ochiai_cc_new

def get_single_normal_distance(list1, list2):
    temp = 0
    for index in range(len(list1)):
        if list1[index] != list2[index]:
            temp += 1
    temp2 = math.sqrt(temp)
    return temp2
    pass

def get_single_fuzzy_distance(list1, list2, sus_tar):
    temp = 0
    for index in range(len(list1)):
        if list1[index] != list2[index]:
            a = list1[index] * sus_tar[index]
            b = list2[index] * sus_tar[index]
            c = a - b
            temp += pow(c, 2)
    temp2 = math.sqrt(temp)
    return temp2
    pass

def get_distance_normal(covMatrix_int, in_vector):
    cov_limit = []
    for index in range(len(in_vector)):
        if in_vector[index] == 1:
            cov_limit.append(covMatrix_int[index])

    dict_location, big_to_little = Tool_optimization.getCF(cov_limit)
    little_to_index = {}

    flag1 = 0
    distance = []
    for x_index in dict_location:
        x = dict_location[x_index][0]
        little_to_index[x] = flag1
        distance_temp = []
        flag2 = 0
        # print("normal distance " + str(flag1) + "/" + str(len(dict_location)))
        for y_index in dict_location:
            y = dict_location[y_index][0]
            if flag1 == flag2:
                distance_temp.append(0)
            elif flag1 > flag2:
                distance_temp.append(distance[flag2][flag1])
            else:
                temp = get_single_normal_distance(cov_limit[x], cov_limit[y])
                distance_temp.append(temp)
            flag2 += 1
        flag1 += 1
        distance.append(distance_temp)

    distance_full = []
    for x in range(len(cov_limit)):
        distance_temp = []
        for y in range(len(cov_limit)):
            distance_temp.append(
                distance[little_to_index[big_to_little[x]]][little_to_index[big_to_little[y]]])
        distance_full.append(distance_temp)
    return distance_full
    pass

def get_distance_fuzzy(covMatrix_int, in_vector, gongshi):
    sus_oc, sus_tu, sus_op, tf, tp, sus_ds, sus_cr, sus_oc_new = Tool_localization.CBFL_location([], covMatrix_int, in_vector)
    gongshi_target_list = [sus_ds, sus_oc, sus_tu, sus_op, sus_cr, sus_oc_new]
    sus_tar = gongshi_target_list[gongshi]

    cov_limit = []
    for index in range(len(in_vector)):
        if in_vector[index] == 1:
            cov_limit.append(covMatrix_int[index])

    dict_location, big_to_little = Tool_optimization.getCF(cov_limit)
    little_to_index = {}

    flag1 = 0
    distance = []
    for x_index in dict_location:
        x = dict_location[x_index][0]
        little_to_index[x] = flag1
        distance_temp = []
        flag2 = 0
        # print("fuzzy distance " + str(flag1) + "/" + str(len(dict_location)))
        for y_index in dict_location:
            y = dict_location[y_index][0]
            if flag1 == flag2:
                distance_temp.append(0)
            elif flag1 > flag2:
                distance_temp.append(distance[flag2][flag1])
            else:
                temp = get_single_fuzzy_distance(cov_limit[x], cov_limit[y], sus_tar)
                distance_temp.append(temp)
            flag2 += 1
        flag1 += 1
        distance.append(distance_temp)

    distance_full = []
    for x in range(len(cov_limit)):
        distance_temp = []
        for y in range(len(cov_limit)):
            distance_temp.append(
                distance[little_to_index[big_to_little[x]]][little_to_index[big_to_little[y]]])
        distance_full.append(distance_temp)
    return distance_full
