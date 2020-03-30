# coding=utf-8
from __future__ import division

import math

# anf, anp
def cal_crosstab(Nf, Ns, Ncfw, Ncsw, Nufw, Nusw):
    N = Nf + Ns
    Sw = 0
    Ncw = Ncfw + Ncsw
    Nuw = Nufw + Nusw
    try:
        Ecfw = Ncw * (Nf / N)
        Ecsw = Ncw * (Ns / N)
        Eufw = Nuw * (Nf / N)
        Eusw = Nuw * (Ns / N)
        X2w = pow(Ncfw - Ecfw, 2) / Ecfw + pow(Ncsw - Ecsw, 2) / Ecsw + pow(Nufw - Eufw, 2) / Eufw + pow(
            Nusw - Eusw, 2) / Eusw
        yw = (Ncfw / Nf) / (Ncsw / Ns)
        if yw > 1:
            Sw = X2w
        elif yw < 1:
            Sw = -X2w
    except:
        Sw = 0
    return Sw

def cal_dstar(tf, tp, aef, aep, anf, anp, index):
    a = aep + (tf - aef)
    if a == 0:
        return 0
    b = math.pow(aef, index)
    c = b / a
    return c

def cal_ochiai(tf, tp, aef, aep, anf, anp):
    if aef == 0:
        return 0
    a = aef + aep
    b = math.sqrt(tf * a)
    if b == 0:
        return 0
    c = aef / b
    return c

def cal_ochiai_new(tf, tp, aef, aep, anf, anp):
    a=tf+aep
    if a==0:
        return 0
    b=aef/a
    return b

def cal_turantula(tf, tp, aef, aep, anf, anp):
    if aef == 0:
        return 0
    if tf == 0 or tp == 0:
        return 0
    a = aef / tf
    b = aep / tp
    c = a / (a + b)
    return c

def cal_op2(tf, tp, aef, aep, anf, anp):
    a = aep / (tp + 1)
    b = aef - a
    return b


# anf, anp
def cal_crosstab_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s):
    a = cal_crosstab(tf, tp - cc_s, fail_s, pass_s - cc_s, tf - fail_s, tp - pass_s)
    b = cal_crosstab(tf + cc_s, tp - cc_s, fail_s + cc_s, pass_s - cc_s, tf - fail_s, tp - pass_s)
    c = cal_crosstab(tf + cc_pro_sum, tp - cc_pro_sum, fail_s + cc_s, pass_s - cc_s, tf - fail_s, tp - pass_s)
    return a, b, c

def cal_ochiai_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s):
    a = cal_ochiai(tf, tp - cc_s, fail_s, pass_s - cc_s, None, None)
    b = cal_ochiai(tf + cc_s, tp - cc_s, fail_s +
                   cc_s, pass_s - cc_s, None, None)
    c = cal_ochiai(tf + cc_pro_sum, tp - cc_pro_sum,
                   fail_s + cc_s, pass_s - cc_s, None, None)
    return a, b, c

def cal_ochiai_cc_new(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s):
    a = cal_ochiai_new(tf, tp - cc_s, fail_s, pass_s - cc_s, None, None)
    b = cal_ochiai_new(tf + cc_s, tp - cc_s, fail_s +
                       cc_s, pass_s - cc_s, None, None)
    c = cal_ochiai_new(tf + cc_pro_sum, tp - cc_pro_sum,
                       fail_s + cc_s, pass_s - cc_s, None, None)
    return a, b, c

def cal_dstar_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s):
    a = cal_dstar(tf, tp - cc_s, fail_s, pass_s - cc_s, None, None, 3)
    b = cal_dstar(tf + cc_s, tp - cc_s, fail_s +
                  cc_s, pass_s - cc_s, None, None, 3)
    c = cal_dstar(tf + cc_pro_sum, tp - cc_pro_sum, fail_s +
                  cc_s, pass_s - cc_s, None, None, 3)
    return a, b, c

def cal_turantula_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s):
    a = cal_turantula(tf, tp - cc_s, fail_s, pass_s - cc_s, None, None)
    b = cal_turantula(tf + cc_s, tp - cc_s, fail_s +
                      cc_s, pass_s - cc_s, None, None)
    c = cal_turantula(tf + cc_pro_sum, tp - cc_pro_sum,
                      fail_s + cc_s, pass_s - cc_s, None, None)
    return a, b, c

def cal_op2_cc(tf, tp, fail_s, pass_s, cc_pro_sum, cc_s):
    a = cal_op2(tf, tp - cc_s, fail_s, pass_s - cc_s, None, None)
    b = cal_op2(tf + cc_s, tp - cc_s, fail_s + cc_s, pass_s - cc_s, None, None)
    c = cal_op2(tf + cc_pro_sum, tp - cc_pro_sum,
                fail_s + cc_s, pass_s - cc_s, None, None)
    return a, b, c


def CBFL_location(use_list, covMatrix_int, in_vector):
    statement_num = len(covMatrix_int[0])
    case_num = len(covMatrix_int)
    # print(statement_num)
    # exit(0)

    sus_oc = {}
    sus_tu = {}
    sus_op = {}
    sus_ds = {}
    sus_cr = {}
    sus_oc_new = {}

    tf = 0
    tp = 0
    for case_index in range(case_num):
        if use_list == None or len(use_list) == 0 or case_index in use_list:
            if in_vector[case_index] == 1:
                tf += 1
            else:
                tp += 1

    for statement_index in range(statement_num):
        initial_int = covMatrix_int[0][statement_index]
        if initial_int == 2:
            sus_oc[statement_index] = -1
            sus_tu[statement_index] = -1
            sus_op[statement_index] = -1
            sus_ds[statement_index] = -1
            sus_cr[statement_index] = -1

            sus_oc_new[statement_index] = -1
        else:
            aef = 0
            aep = 0
            anf = 0
            anp = 0
            for case_index in range(case_num):
                if use_list == None or len(use_list) == 0 or case_index in use_list:
                    current_int = covMatrix_int[case_index][statement_index]
                    if current_int == 1:
                        if in_vector[case_index] == 1:
                            aef += 1
                        else:
                            aep += 1
                    else:
                        if in_vector[case_index] == 1:
                            anf += 1
                        else:
                            anp += 1

            tempp = cal_ochiai(tf, tp, aef, aep, anf, anp)
            sus_oc[statement_index] = tempp
            tempp = cal_turantula(tf, tp, aef, aep, anf, anp)
            sus_tu[statement_index] = tempp
            tempp = cal_op2(tf, tp, aef, aep, anf, anp)
            sus_op[statement_index] = tempp
            tempp = cal_dstar(tf, tp, aef, aep, anf, anp, 3)
            sus_ds[statement_index] = tempp
            tempp = cal_crosstab(tf, tp, aef, aep, anf, anp)
            sus_cr[statement_index] = tempp
            tempp = cal_ochiai_new(tf, tp, aef, aep, anf, anp)
            sus_oc_new[statement_index] = tempp
    return sus_oc, sus_tu, sus_op, tf, tp, sus_ds, sus_cr, sus_oc_new
