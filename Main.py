# coding=utf-8
from __future__ import division

import multiprocessing
import shutil
import sys
import time
import os
import Cluster_kmseer_v1
import Cluster_optics_v2
import Tool_optimization
import Tool_localization
import Tool_distance
import Tool_io


def dealCluster(covMatrix_int, in_vector, gongshi, vector_type, cluster_type):
    #当聚类类型为origin时，什么都不做
    if cluster_type==3 or cluster_type==4:
        cluster = []  # 聚类中心在fail_test_index中的index
        cluster_content = []
        cluster_content.append([])
        cluster.append(0)
        for index in range(len(covMatrix_int)):
            cluster_content[0].append(index)
        return cluster, cluster_content

    #整理出错误用例
    #开始矩阵压缩
    in_vector_limit = []
    faultTest_to_allTest = {}
    faultTest_num = 0
    for index in range(len(in_vector)):
        if in_vector[index] == 1:
            in_vector_limit.append(1)
            faultTest_to_allTest[faultTest_num] = index
            faultTest_num += 1

    rank_target = []
    # 选择特征向量方式
    if vector_type == 0 or cluster_type==5:
        test_index = range(len(in_vector))
        covMatrix_limit = []
        in_limit = []
        for in_item_index in range(len(in_vector)):
            if in_vector[in_item_index] == 0:
                covMatrix_limit.append(covMatrix_int[in_item_index])
                in_limit.append(0)
        in_limit.append(1)

        flag = 1
        dict_location, big_to_little = Tool_optimization.getCF(covMatrix_int)
        target_little = {}

        for index in test_index:
            flag += 1
            if in_vector[index] == 0:
                # print(str(flag) + " " + str(len(test_index))+" pass")
                rank_target.append(0)
                continue
            if big_to_little[index] not in target_little:
                # print("mseer initSus " + str(flag) + " " + str(len(test_index)))
                covMatrix_limit.append(covMatrix_int[index])
                sus_oc, sus_tu, sus_op, tf, tp, sus_ds, sus_cr, sus_oc_new = Tool_localization.CBFL_location([], covMatrix_limit,in_limit)

                gongshi_target_list = [sus_ds, sus_oc, sus_tu, sus_op, sus_cr, sus_oc_new]

                sus_tar = gongshi_target_list[gongshi]
                if cluster_type==5:
                    sus_tar = gongshi_target_list[2]

                rank_target.append(Tool_optimization.Sus2Rank_addOne(sus_tar))
                covMatrix_limit.pop()
                target_little[big_to_little[index]] = sus_tar
            else:
                # print(str(flag) + " " + str(len(test_index))+" quick")
                rank_target.append(Tool_optimization.Sus2Rank_addOne(target_little[big_to_little[index]]))
    #矩阵压缩完毕

    distance = []
    cluster=[]
    cluster_content=[]
    # 选择聚类方式
    if cluster_type == 0:
        target_covMatrix = []
        if vector_type == 0:
            # 计算失败测试用例之间的距离
            rank_target_limit = []
            for index in range(len(in_vector)):
                if in_vector[index] == 1:
                    rank_target_limit.append(rank_target[index])
            distance = Cluster_kmseer_v1.get_distance_mseer(rank_target_limit)
        elif vector_type == 1:
            for index in range(len(in_vector)):
                if in_vector[index] == 1:
                    target_covMatrix.append(covMatrix_int[index])
            distance =Tool_distance.get_distance_normal(target_covMatrix, in_vector_limit)
        elif vector_type == 2:
            for index in range(len(in_vector)):
                if in_vector[index] == 1:
                    target_covMatrix.append(covMatrix_int[index])
            distance = Tool_distance.get_distance_fuzzy(target_covMatrix, in_vector_limit, gongshi)

        cluster,cluster_content=Cluster_kmseer_v1.deal_mseer(faultTest_num, distance,in_vector_limit)
    elif cluster_type == 1:
        target_covMatrix = []
        if vector_type == 0:
            # 计算失败测试用例之间的距离
            rank_target_limit = []
            for index in range(len(in_vector)):
                if in_vector[index] == 1:
                    rank_target_limit.append(rank_target[index])
            distance = Cluster_kmseer_v1.get_distance_mseer(rank_target_limit)
        elif vector_type == 1:
            for index in range(len(in_vector)):
                if in_vector[index] == 1:
                    target_covMatrix.append(covMatrix_int[index])
            distance =Tool_distance.get_distance_normal(target_covMatrix, in_vector_limit)
        elif vector_type == 2:
            for index in range(len(in_vector)):
                if in_vector[index] == 1:
                    target_covMatrix.append(covMatrix_int[index])
            distance = Tool_distance.get_distance_fuzzy(target_covMatrix, in_vector_limit, gongshi)

        cluster,cluster_content=Cluster_kmseer_v1.deal_mseer(faultTest_num, distance,in_vector_limit)
    elif cluster_type == 2:
        target_covMatrix = []
        if vector_type == 0:
            rank_target_limit = []
            for index in range(len(in_vector)):
                if in_vector[index] == 1:
                    rank_target_limit.append(rank_target[index])
            target_covMatrix = rank_target_limit
        elif vector_type == 1:
            # 原始01特征向量
            for index in range(len(in_vector)):
                if in_vector[index] == 1:
                    target_covMatrix.append(covMatrix_int[index])
        elif vector_type == 2:
            # 加权模糊特征向量
            sus_oc, sus_tu, sus_op, tf, tp, sus_ds, sus_cr, sus_oc_new =Tool_localization.CBFL_location([], covMatrix_int, in_vector)
            gongshi_target_list = [sus_ds, sus_oc, sus_tu, sus_op, sus_cr, sus_oc_new]
            sus_tar = gongshi_target_list[gongshi]
            for index in range(len(in_vector)):
                if in_vector[index] == 1:
                    temp_list = covMatrix_int[index].copy()
                    for index2 in range(len(temp_list)):
                        temp_list[index2] = temp_list[index2] * sus_tar[index2]
                    target_covMatrix.append(temp_list)

        cluster, cluster_content = Cluster_optics_v2.dealAll(target_covMatrix)

    #复原矩阵压缩
    for index in range(len(cluster)):
        cluster[index] = faultTest_to_allTest[cluster[index]]
        for index2 in range(len(cluster_content[index])):
            cluster_content[index][index2] = faultTest_to_allTest[cluster_content[index][index2]]

    return cluster, cluster_content

def findMultiple(covMatrix, in_vector, cluster_content):
    for list_item_index in range(len(cluster_content)):
        list_item=cluster_content[list_item_index]
        for index_index in reversed(range(len(list_item))):
            index=list_item[index_index]
            if in_vector[index] == 0:
                cluster_content[list_item_index].remove(index)
    ochiai_sum = []
    dstar_sum = []
    turantula_sum = []
    op2_sum = []
    crosstab_sum = []
    ochiai_new_sum = []
    for fail_test_index in range(len(cluster_content)):
        # print("find multiple " + str(fail_test_index) +"/" + str(len(cluster_content)))
        fail_test = cluster_content[fail_test_index]
        all_test = list(range(len(in_vector)))
        for item_index in reversed(range(len(all_test))):
            item=all_test[item_index]
            if item in fail_test:
                all_test.remove(item)
        pass_test = all_test

        in_vector_temp = []
        covMatrix_temp = []

        for item in pass_test:
            in_vector_temp.append(0)
            covMatrix_temp.append(covMatrix[item])

        for item in fail_test:
            in_vector_temp.append(1)
            covMatrix_temp.append(covMatrix[item])

        sus_oc, sus_tu, sus_op, tf, tp, sus_ds, sus_cr, sus_oc_new = Tool_localization.CBFL_location(
            [], covMatrix_temp, in_vector_temp)

        ochiai_sum.append(sus_oc)
        dstar_sum.append(sus_ds)
        turantula_sum.append(sus_tu)
        op2_sum.append(sus_op)
        crosstab_sum.append(sus_cr)
        ochiai_new_sum.append(sus_oc_new)
    return ochiai_sum, dstar_sum, turantula_sum, op2_sum, crosstab_sum, ochiai_new_sum


def getCost(sum, fault, cost_sum,cluster_type):
    fault_of_cost = []
    cost = []
    sus_find = []
    findFault = []
    dict_record = []

    #每个类簇对应的错误
    fault_to_cluster=[]

    if cluster_type==4:
        for dic in sum:
            dict = sorted(dic.items(), key=lambda d: d[1], reverse=True)
            dict_record.append(dict)
            for index in range(len(dict)):
                if len(findFault) == len(fault):
                    break

                line_no = dict[index][0]
                if line_no in fault and line_no not in findFault:
                    cost_temp = {}
                    fault_to_cluster.append(line_no)
                    sus_find.append(dict[index][1])
                    cost_temp[4] = index + 1
                    # cost.append(index + 1)
                    fault_of_cost.append(line_no)
                    cost_sum[4] = cost_sum[4] + index + 1
                    if line_no not in findFault:
                        findFault.append(line_no)
                    # break
                    cost.append(cost_temp)
    else:
        for dic in sum:
            cost_temp = {}
            dict = sorted(dic.items(), key=lambda d: d[1], reverse=True)
            dict_record.append(dict)
            for index in range(len(dict)):
                if len(findFault)==len(fault):
                    break

                line_no = dict[index][0]
                if line_no in fault and line_no not in findFault:
                    fault_to_cluster.append(line_no)
                    sus_find.append(dict[index][1])
                    cost_temp[4] = index + 1
                    # cost.append(index + 1)
                    fault_of_cost.append(line_no)
                    cost_sum[4] = cost_sum[4] + index + 1
                    if line_no not in findFault:
                        findFault.append(line_no)
                    break
            cost.append(cost_temp)

    if cluster_type==4:
        for sus_index in range(len(sus_find)):
            first_index = -1
            end_index = -1
            average_index = -1
            sus_record = sus_find[sus_index]
            dict = dict_record[0]
            for sus_item in range(len(dict)):
                if dict[sus_item][1] == sus_record and first_index == -1:
                    first_index = sus_item + 1
                if first_index != -1 and dict[sus_item][1] != sus_record:
                    end_index = sus_item
                    break
            if end_index == -1:
                end_index = len(dict)
            average_index = (first_index + end_index) / 2
            cost[sus_index][1] = first_index
            cost[sus_index][2] = end_index
            cost[sus_index][3] = average_index
            cost_sum[1] += first_index
            cost_sum[2] += end_index
            cost_sum[3] += average_index
    else:
        for sus_index in range(len(sus_find)):
            first_index = -1
            end_index = -1
            average_index = -1
            sus_record = sus_find[sus_index]
            dict = dict_record[sus_index]
            for sus_item in range(len(dict)):
                if dict[sus_item][1] == sus_record and first_index == -1:
                    first_index = sus_item + 1
                if first_index != -1 and dict[sus_item][1] != sus_record:
                    end_index = sus_item
                    break
            if end_index == -1:
                end_index = len(dict)
            average_index = (first_index + end_index) / 2
            cost[sus_index][1] = first_index
            cost[sus_index][2] = end_index
            cost[sus_index][3] = average_index
            cost_sum[1] += first_index
            cost_sum[2] += end_index
            cost_sum[3] += average_index
    return cost, findFault, cost_sum, fault_of_cost,fault_to_cluster


def init_cost_sum(CC):
    cost_sum = {}
    if CC:
        for i in range(3):
            cost_sum[i + 1] = {}
            for j in range(4):
                cost_sum[i + 1][j + 1] = 0
    else:
        for j in range(4):
            cost_sum[j + 1] = 0
    return cost_sum

def deal_location(TCC, OCC, MFS_version_path, MFO_version_path, project_path, version_file, out_md5, gongshi,vector_type, cluster_type,root_path):
    faultStr = ""
    project_name = project_path.split("/")[len(project_path.split("/")) - 1]
    version_name = MFS_version_path.split("/")[len(MFS_version_path.split("/")) - 1]

    # try:
    # 保存结果的路径
    saveResult_path = MFO_version_path + "/outputs/"
    rateResult_path = root_path + "/ratesCC/"

    if not os.path.exists(saveResult_path):
        os.mkdir(saveResult_path)
    # 判断公式
    gongshi_list = ["dstar", "ochiai", "turantula", "op2", "crosstab", "jaccard"]
    gongshi_str = gongshi_list[gongshi]
    # 向量形式
    vector_type_list = ["rank", "normal", "fuzzy"]
    vector_type_str = vector_type_list[vector_type]
    # 聚类算法
    cluster_type_list = ["mseer", "mseersingle", "optics","origin","originf"]
    cluster_type_str = cluster_type_list[cluster_type]

    # print("start " + str(TCC) + " " + str(OCC) + " " + project_path + " " + version_file + " " + gongshi_str + " " + vector_type_str + " " + cluster_type_str)
    # 初始化
    i_time = 0  # 迭代次数
    find_fault = []  # 找到的错误序号
    str_add = ""
    if TCC:
        # 对应三种处理CC的方法
        if OCC:
            target_cost_sum = init_cost_sum(True)
            str_add = "_tcc_occ"
        else:
            target_cost_sum = init_cost_sum(False)
            str_add = "_tcc_only"
    else:
        if OCC:
            target_cost_sum = init_cost_sum(True)
            str_add = "_occ_only"
        else:
            target_cost_sum = init_cost_sum(False)
            str_add = "_no_cc"

    # 记录错误的语句
    faultStr = project_name + "\t" + version_name + "\t" + gongshi_str + "\t" + vector_type_str + "\t" + cluster_type_str + "\t" + str_add + "\n"

    # 检查是否已经完成了 gongshi_str+"_"+vector_type_str+"_cost_sum" + str_add
    check_path = saveResult_path + gongshi_str + "_" + vector_type_str + "_" + cluster_type_str + "_" + "cost_sum_end" + str_add
    # print("check path: " + check_path)
    if os.path.exists(check_path):
        # print("pass " + str(TCC) + " " + str(OCC) + " " + project_path + " " + version_file + " " + gongshi_str + " " + vector_type_str + " " + cluster_type_str)
        return True
    # 第0次迭代
    # 第0次读取文件 原始错误位置
    covMatrix, fault_old, in_vector, failN, passN = Tool_io.readFile(MFS_version_path, MFO_version_path)
    # 初始化需要被精简而删掉的语句
    rm_list=[]

    # 约简错误位置 覆盖信息
    fault_use = fault_old.copy()
    if len(rm_list)==0:
        covMatrix, fault, code_to_complete,rm_list = Tool_optimization.clean_cov(covMatrix, fault_use)
    else:
        covMatrix, fault, code_to_complete = Tool_optimization.clean_cov_ready(covMatrix, fault_use,rm_list)
    # 寻找真实的错误位置
    fault = list(set(fault))
    # print("开始时未清理的Fault:")
    # print(fault)
    for index in reversed(range(len(fault))):
        item = fault[index]
        if code_to_complete[item] in find_fault:
            del fault[index]
    # print("开始时清理后的Fault:")
    # print(fault)
    save_fault = []
    for item in fault:
        save_fault.append(code_to_complete[item])
    # print("开始时处理前的Fault:")
    # print(save_fault)
    # 保存每次迭代剩余的错误
    Tool_io.checkAndSaveResult("fault", save_fault, saveResult_path, gongshi_str, vector_type_str, cluster_type_str,
                       str_add, i_time)

    if i_time == 0:
        fault_old = save_fault
        Tool_io.checkAndSave(saveResult_path, "fault_old", fault_old)

    # print("所有的Fault:")
    # print(fault_old)
    # 寻找TCC
    tcc_list=[]

    # 开始聚类
    cluster, cluster_content = dealCluster(covMatrix, in_vector, gongshi, vector_type, cluster_type)
    Tool_io.checkAndSaveResult("cluster", cluster, saveResult_path, gongshi_str, vector_type_str, cluster_type_str, str_add,
                       i_time)
    Tool_io.checkAndSaveResult("cluster_content", cluster_content, saveResult_path, gongshi_str, vector_type_str,
                       cluster_type_str, str_add, i_time)

    # 使用类簇内的测试用例检查TCC
    tcc_inner_list=[]

    # cluster_b,cluster_content_b=get_the_best_cluster(cluster,cluster_content)
    # gongshi_list=["dstar","ochiai","turantula","op2"]
    cc_pro = [[]]
    ochiai_sum, dstar_sum, turantula_sum, op2_sum, crosstab_sum, ochiai_new_sum = findMultiple(covMatrix,in_vector,cluster_content)

    # 将要使用的怀疑度排行
    gongshi_target_list = [dstar_sum, ochiai_sum, turantula_sum, op2_sum, crosstab_sum, ochiai_new_sum]
    target_sum = gongshi_target_list[gongshi]
    Tool_io.checkAndSaveResult("target_sum", target_sum, saveResult_path, gongshi_str, vector_type_str, cluster_type_str,str_add, i_time)
    # 保存临时数据并寻找本次迭代的错误语句
    cost, findFault, target_cost_sum, fault_of_cost,fault_to_cluster = getCost(target_sum, fault, target_cost_sum,cluster_type)

    # 保存每一次花费和找到的错误
    Tool_io.checkAndSaveResult("cost", cost, saveResult_path, gongshi_str, vector_type_str, cluster_type_str, str_add,i_time)
    Tool_io.checkAndSaveResult("cost_of_fault", fault_of_cost, saveResult_path, gongshi_str, vector_type_str,cluster_type_str, str_add, i_time)
    Tool_io.checkAndSaveResult("find_fault", findFault, saveResult_path, gongshi_str, vector_type_str,
                               cluster_type_str, str_add, i_time)
    # findFault 本次迭代中找到的错误 约简位置
    # find_fault 全局错误位置
    # print("结束时找到的本轮处理前fault:")
    # print(findFault)

    end_fault = []
    for item in findFault:
        end_fault.append(code_to_complete[item])

    # print("结束时找到的本轮处理前fault:")
    # print(end_fault)

    for item in end_fault:
        if item not in find_fault:
            find_fault.append(item)
    # print("结束时所有找到的fault:")
    # print(find_fault)
    # print("结束时再看看所有fault:")
    # print(fault_old)

    # print("end " + str(TCC) + " " + str(OCC) + " " + project_path + " " + version_file + " " + gongshi_str + " " + vector_type_str + " " + cluster_type_str)
    return True

def deal_different_type(root_path,MFS_version_path, MFO_version_path, project_path, version_file, out_md5,type):
    # 选择什么错误定位公式
    print("begin  " + project_path + " " + version_file + " " + time.strftime('%Y.%m.%d %H:%M:%S',
                                                                              time.localtime(time.time())))

    if type==1:
        # cluster_type = 2
        vector_type=1
        cluster_type=2
        for gongshi in range(6):
            # for vector_type in [1,2]:
            deal_location(False, True, MFS_version_path, MFO_version_path, project_path, version_file, out_md5, gongshi,
                          vector_type, cluster_type, root_path)
            # deal_location(False, False, MFS_version_path, MFO_version_path, project_path, version_file, out_md5, gongshi,
            #               vector_type, cluster_type, root_path)
        #
        # vector_type=1
        # cluster_type=4
        # for gongshi in range(6):
        #     # for vector_type in [1,2]:
        #     deal_location(False, False, MFS_version_path, MFO_version_path, project_path, version_file, out_md5, gongshi,
        #                   vector_type, cluster_type, root_path)

        # vector_type = 0
        # cluster_type = 0
        # gongshi = 4
        # deal_location(False, False, MFS_version_path, MFO_version_path, project_path, version_file, out_md5, gongshi,
        #               vector_type, cluster_type, root_path)
    else:
        gongshi=4
        vector_type=0
        cluster_type=0

        deal_location(False, False, MFS_version_path, MFO_version_path, project_path, version_file, out_md5, gongshi,
                      vector_type, cluster_type, root_path)

    print("finish  " + project_path + " " + version_file + " " + time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))


def deal(root_path, pooln):
    case_num = Tool_io.get_case_num(root_path)

    # bubaoliulist = ["grep","sed"]
    # for index in reversed(range(len(case_num))):
    #     if case_num[index][0] in bubaoliulist:
    #         del case_num[index]

    # baoliulist = ["sed", "grep", "totinfo", "tcas","schedule"]
    # baoliulist=["schedule2","printtokens2","printtokens","replace"]
    # baoliulist = ["replace"]
    # for index in reversed(range(len(case_num))):
    #     if case_num[index][0] not in baoliulist:
    #         del case_num[index]
    #
    # print(len(case_num))
    # print(case_num)

    pool = multiprocessing.Pool(processes=pooln)
    # 遍历所有文件夹
    # project_files = os.listdir(root_path)
    for project_file in case_num:
        project_name = project_file[0]
        # if project_name=="sed":
        #     continue
        project_path = root_path + "/" + project_name
        MFS_path = project_path + "/" + "MFsource"
        MFO_path = project_path + "/" + "MFoutput"
        if not os.path.exists(MFO_path):
            continue
        version_files = os.listdir(MFS_path)
        version_files.sort()
        if debug == True:
            out_md5 = None
        else:
            out_md5 = Tool_io.get_right_md5(project_path)
        for version_file in version_files:
            MFS_version_path = MFS_path + "/" + version_file
            MFO_version_path = MFO_path + "/" + version_file
            # 根据不同参数处理实验
            # deal_different_type(root_path,MFS_version_path, MFO_version_path, project_path, version_file, out_md5,1)
            pool.apply_async(deal_different_type,(root_path,MFS_version_path, MFO_version_path, project_path, version_file, out_md5,1,))
            # print("end " + project_name + " " + version_file+"\n\n")
            # exit(0)
    pool.close()
    pool.join()

    pass

debug = False
if __name__ == "__main__":
    pooln = 32
    root_path = sys.path[0] + "/"
    # root_path = "D:/arrange/filter1/"
    # root_path = "D:/arrange/filter1 20190916/"

    rateResult_path = root_path + "/ratesCC/"
    if os.path.exists(rateResult_path):
        shutil.rmtree(rateResult_path)
    os.mkdir(rateResult_path)

    faultFile = root_path + "/bug/"
    if os.path.exists(faultFile):
        shutil.rmtree(faultFile)
    os.mkdir(faultFile)

    deal(root_path, pooln)