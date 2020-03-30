# coding=utf-8
from __future__ import division

import hashlib
import os
import pickle
from functools import partial

def checkAndSaveResult(name, save_content, saveResult_path, gongshi_str, vector_type_str, cluster_type_str, str_add,i_time):
    checkAndSave(saveResult_path,gongshi_str + "_" + vector_type_str + "_" + cluster_type_str + "_" + name + str_add + "_" + str(i_time), save_content)

def checkAndLoadResult(name, save_content, saveResult_path, gongshi_str, vector_type_str, cluster_type_str, str_add,i_time):
    save_content=checkAndLoad(saveResult_path,gongshi_str + "_" + vector_type_str + "_" + cluster_type_str + "_" + name + str_add + "_" + str(i_time))
    return save_content

def md5sum(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding="utf-8",errors="ignore") as f:
            strings = f.read()
            # print(strings)
            if "print" in filename:
                if "doesn't exists" in strings:
                    if "print_tokens" in strings:
                        # print(filename + "一定出错")
                        return "print tokens not exists"
                    elif "garbage/nothing" in strings:
                        # print(filename + "找到不存在的测试用例")
                        return "nothing"

        with open(filename, 'rb') as f:
            d = hashlib.md5()
            for buf in iter(partial(f.read, 128), b''):
                d.update(buf)
            f.close()
        return d.hexdigest()
    else:
        return None

def get_case_num(root_path):
    case_num = {}
    # 首先获得所有项目的测试用例数量
    project_files = os.listdir(root_path)
    for project_file in project_files:
        project_name = project_file
        project_path = root_path + "/" + project_name
        scriptPath = project_path + "/gettraces.sh"
        if not os.path.exists(scriptPath):
            continue
        Case_num = getTestNum(scriptPath)
        case_num[project_name] = Case_num
    case_num = sorted(case_num.items(), key=lambda d: d[1], reverse=False)
    return case_num

def getTestNum(scriptPath):
    f = open(scriptPath, 'r')
    script_lines = f.readlines()
    f.close()
    for i in range(0, script_lines.__len__())[::-1]:
        temp_line = script_lines[i]
        if "$target/" in temp_line and "cp" in temp_line:
            Case_num = 1 + int(temp_line.split('$target/')[1].split('.txt')[0])
            return Case_num
    return 0

def get_right_md5(project_path):
    scriptPath = project_path + "/gettraces.sh"
    Case_num = getTestNum(scriptPath)

    Out_Result = []
    for Rcov in range(Case_num):
        temp_Out_Path = outputPath = project_path + \
                                     "/outputs/v0" + "/t" + str(Rcov + 1)
        tempMD5 = md5sum(temp_Out_Path)
        Out_Result.append(tempMD5)
    return Out_Result

def getLines(origin_fault_source_path):
    fh = open(origin_fault_source_path)
    string = fh.readlines()
    fh.close()
    return string

def checkAndSave(root, param, content):
    dump_path = root + "/" + param
    if not os.path.exists(dump_path):
        f = open(dump_path, 'wb')
        pickle.dump(content, f)
        f.close()

def checkAndLoad(root, param):
    dump_path = root + "/" + param
    if os.path.exists(dump_path):
        f = open(dump_path, 'rb')
        content = pickle.load(f)
        f.close()
        return content
    return None


def readFile(Spath, Opath):
    savedata = checkAndLoad(Opath, "savedata")
    if savedata != None:
        covMatrix = savedata[1]
        fault = savedata[2]
        in_vector = savedata[3]
        failN = savedata[4]
        passN = savedata[5]
        return covMatrix, fault, in_vector, failN, passN

    covMatrix_path = Opath + "/covMatrix.in"
    fault_position_path = Spath + "/fault_record.txt"
    in_vector_path = Opath + "/in_vector.txt"

    if not os.path.exists(covMatrix_path) or not os.path.exists(fault_position_path) or not os.path.exists(
            in_vector_path):
        return None, None, None, None,None

    f = open(covMatrix_path, 'r')
    tempCovMatrix = f.readlines()
    f.close()
    covMatrix = []
    for i in range(len(tempCovMatrix)):
        tempStatementlist = tempCovMatrix[i].split(' ')
        tempcovMatrix = []
        for j in range(len(tempStatementlist)):
            tempStatement = tempStatementlist[j]
            if tempStatement != "":
                tempcovMatrix.append(int(tempStatement))
        covMatrix.append(tempcovMatrix)

    f = open(fault_position_path, 'r')
    fault_position = f.readlines()
    f.close()
    fault = []
    for i in range(len(fault_position)):
        temp = int(fault_position[i].split(" :")[0].split("line ")[1]) - 1
        fault.append(temp)

    f = open(in_vector_path, 'r')
    in_vector_str = f.read()
    f.close()
    in_vector = []
    failN = 0
    passN = 0
    for i in range(len(in_vector_str)):
        temp = int(in_vector_str[i])
        in_vector.append(temp)
        if temp == 1:
            failN += 1
        else:
            passN += 1

    savedata = {}
    savedata[1] = covMatrix
    savedata[2] = fault
    savedata[3] = in_vector
    savedata[4] = failN
    savedata[5] = passN
    checkAndSave(Opath, "savedata", savedata)
    return covMatrix, fault, in_vector, failN, passN

if __name__ == "__main__":
    get_case_num("/mnt/f/FLN/filter/")