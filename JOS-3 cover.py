#jos-3 code#

# part 1 matrix
import numpy as np

def sub2whole(subarr_list): #多个子数组按照它们在 subarr_list 中的顺序水平和垂直拼接成一个整体的二维数组。
    ishape = 0
    jshape = 0
    for subarr in subarr_list:
        ishape += subarr.shape[0]
        jshape += subarr.shape[1]

    wholearr = np.zeros((ishape, jshape))
    i = 0
    j = 0
    for subarr in subarr_list:
        iend = i + subarr.shape[0]
        jend = j + subarr.shape[1]
        wholearr[i:iend, j:jend] = subarr.copy()
        i += subarr.shape[0]
        j += subarr.shape[1]

    return wholearr


BODY_NAMES = [
    "Head", "Neck", "Chest", "Back", "Pelvis",
    "LShoulder", "LArm", "LHand",
    "RShoulder", "RArm", "RHand",
    "LThigh", "LLeg", "LFoot",
    "RThigh", "RLeg", "RFoot"] #分身体部分
LAYER_NAMES = ["artery", "vein", "sfvein", "core", "muscle", "fat", "skin"] #分层

def index_order():
    """
    Defines the index's order of the matrix 定义矩阵的索引顺序
    Returns
    -------
    indexdict : nested dictionary
        keys are BODY_NAMES and LAYER_NAMES
    """
    # Defines exsisting layers as 1 or None 将现有层定义为有或者没有
    indexdict = {}

    for key in ["Head", "Pelvis"]:
        indexdict[key] = {
            "artery": 1, "vein": 1, "sfvein": None,
            "core": 1, "muscle": 1, "fat": 1, "skin": 1} #头与骨盆没有浅层静脉

    for key in ["Neck", "Chest", "Back"]:
        indexdict[key] = {
            "artery": 1, "vein": 1, "sfvein": None,
            "core": 1, "muscle": None, "fat": None, "skin": 1} #脖子、胸、背部没有浅层静脉、肌肉与脂肪

    for key in BODY_NAMES[5:]:  # 肢体各部分
        indexdict[key] = {
            "artery": 1, "vein": 1, "sfvein": 1,
            "core": 1, "muscle": None, "fat": None, "skin": 1} #肢体各部分没有脂肪与肌肉层

    # Sets ordered indices in the matrix 在矩阵中设置有序的索引
    indexdict["CB"] = 0
    order_count = 1
    for bn in BODY_NAMES:
        for ln in LAYER_NAMES:
            if not indexdict[bn][ln] is None:
                indexdict[bn][ln] = order_count
                order_count += 1

    return indexdict, order_count
IDICT, NUM_NODES = index_order()


def index_bylayer(layer):
    """
    Get indices of the matrix by the layer name.
    Parameters
    ----------
    layer : str
        Layer name of jos.
        ex) artery, vein, sfvein, core, muscle, fat or skin.
    Returns
    -------
    indices of the matrix : list
    """

    # Gets indices by the layer name 按层名获取索引
    outindex = []
    for bn in BODY_NAMES:
        for ln in LAYER_NAMES:
            if (layer.lower() == ln) and IDICT[bn][ln]:
                outindex.append(IDICT[bn][ln])
    return outindex


def validindex_bylayer(layer):
    """
    Get indices of the matrix by the layer name.
    Parameters
    ----------
    layer : str
        Layer name of jos.
        ex) artery, vein, sfvein, core, muscle, fat or skin.
    Returns
    -------
    indices of the matrix : list
    """

    # Gets valid indices of the layer name 获取层名的有效索引
    outindex = []
    for i, bn in enumerate(BODY_NAMES):
        if IDICT[bn][layer]:
            outindex.append(i)
    return outindex

# Constant parameters of the matrix' indicies 可以在后续的代码中方便地访问和使用这些索引信息，而不需要在每个使用处都重新计算
INDEX = {}
VINDEX = {}
for key in LAYER_NAMES:
    INDEX[key] = index_bylayer(key)
    VINDEX[key] = validindex_bylayer(key)


def localarr(bf_cr, bf_ms, bf_fat, bf_sk, bf_ava_hand, bf_ava_foot):
    """
    Create matrix to calculate heat exchage by blood flow in each segment [W/K] 创建矩阵来计算每个节段的血流量的热交换
        1.067 [Wh/(L･K)] * Bloodflow [L/h] = [W/K]
    """
    bf_local = np.zeros((NUM_NODES, NUM_NODES))
    for i, bn in enumerate(BODY_NAMES):
        # Dictionary of indecies in each body segment
        # key = layer name, value = index of matrix
        indexof = IDICT[bn]

        # Common 
        bf_local[indexof["core"], indexof["artery"]] = 1.067*bf_cr[i]  # art to cr 动脉到核心
        bf_local[indexof["skin"], indexof["artery"]] = 1.067*bf_sk[i]  # art to sk 动脉到皮肤
        bf_local[indexof["vein"], indexof["core"]] = 1.067*bf_cr[i]    # vein to cr 静脉到核心
        bf_local[indexof["vein"], indexof["skin"]] = 1.067*bf_sk[i]    # vein to sk 静脉到皮肤

        # If the segment has a muslce or fat layer 有肌肉、脂肪层的部位
        if not indexof["muscle"] is None:
            bf_local[indexof["muscle"], indexof["artery"]] = 1.067*bf_ms[i]  # art to ms  动脉到肌肉
            bf_local[indexof["vein"], indexof["muscle"]] = 1.067*bf_ms[i]    # vein to ms 静脉到肌肉
        if not indexof["fat"] is None:
            bf_local[indexof["fat"], indexof["artery"]] = 1.067*bf_fat[i]  # art to fat  动脉到脂肪
            bf_local[indexof["vein"], indexof["fat"]] = 1.067*bf_fat[i]    # vein to fat 静脉到脂肪

        # Only hand 手
        if i == 7 or i == 10:
            bf_local[indexof["sfvein"], indexof["artery"]] = 1.067*bf_ava_hand  # art to sfvein 动脉到浅层静脉
        # Only foot 脚
        if i == 13 or i == 16:
            bf_local[indexof["sfvein"], indexof["artery"]] = 1.067*bf_ava_foot  # art to sfvein 动脉到浅层静脉

    return bf_local


def vessel_bloodflow(bf_cr, bf_ms, bf_fat, bf_sk, bf_ava_hand, bf_ava_foot):
    """
    Get artery and vein blood flow rate [l/h] 得到动静脉血流率
    """
    xbf = bf_cr + bf_ms + bf_fat + bf_sk #总血流量

    bf_art = np.zeros(17)
    bf_vein = np.zeros(17)

    #Head
    bf_art[0] = xbf[0]
    bf_vein[0] = xbf[0]

    #Neck (+Head)
    bf_art[1] = xbf[1] + xbf[0] #头部血流传脖子动静脉
    bf_vein[1] = xbf[1] + xbf[0] 

    #Chest
    bf_art[2] = xbf[2]
    bf_vein[2] = xbf[2]

    #Back
    bf_art[3] = xbf[3]
    bf_vein[3] = xbf[3]

    #Pelvis (+Thighs, Legs, Feet, AVA_Feet)
    bf_art[4] = xbf[4] + xbf[11:17].sum() + 2*bf_ava_foot #下半身四肢6个部位的血流+双脚上的动脉传骨盆动静脉
    bf_vein[4] = xbf[4]  + xbf[11:17].sum() + 2*bf_ava_foot

    #L.Shoulder (+Arm, Hand, (artery只有AVA_Hand)) 
    bf_art[5] = xbf[5:8].sum() + bf_ava_hand
    bf_vein[5] = xbf[5:8].sum()   #左手3个部位的血流+左手上的动脉传左肩膀动静脉

    #L.Arm (+Hand)
    bf_art[6] = xbf[6:8].sum() + bf_ava_hand
    bf_vein[6] = xbf[6:8].sum()

    #L.Hand
    bf_art[7] = xbf[7] + bf_ava_hand
    bf_vein[7] = xbf[7]     #左手血流+左手动脉

    #R.Shoulder (+Arm, Hand, (artery只有AVA_Hand))
    bf_art[8] = xbf[8:11].sum() + bf_ava_hand
    bf_vein[8] = xbf[8:11].sum()

    #R.Arm (+Hand)
    bf_art[9] = xbf[9:11].sum() + bf_ava_hand
    bf_vein[9] = xbf[9:11].sum()

    #R.Hand
    bf_art[10] = xbf[10] + bf_ava_hand
    bf_vein[10] = xbf[10]

    #L.Thigh (+Leg, Foot, (artery只有AVA_Foot))
    bf_art[11] = xbf[11:14].sum() + bf_ava_foot
    bf_vein[11] = xbf[11:14].sum()

    #L.Leg (+Foot)
    bf_art[12] = xbf[12:14].sum() + bf_ava_foot
    bf_vein[12] = xbf[12:14].sum()

    #L.Foot
    bf_art[13] = xbf[13] + bf_ava_foot
    bf_vein[13] = xbf[13]

    #R.Thigh (+Leg, Foot, (artery只有AVA_Foot))
    bf_art[14] = xbf[14:17].sum() + bf_ava_foot
    bf_vein[14] = xbf[14:17].sum()

    #R.Leg (+Foot)
    bf_art[15] = xbf[15:17].sum() + bf_ava_foot
    bf_vein[15] = xbf[15:17].sum()

    #R.Foot
    bf_art[16] = xbf[16] + bf_ava_foot
    bf_vein[16] = xbf[16]

    return bf_art, bf_vein


def wholebody(bf_art, bf_vein, bf_ava_hand, bf_ava_foot):
    """
    Create matrix to calculate heat exchage by blood flow between segments [W/K]创建矩阵来计算节段之间血液流动的热量交换

    """

    def flow(up, down, bloodflow):
        arr = np.zeros((NUM_NODES, NUM_NODES))
        # Coefficient = 1.067 [Wh/L.K]
        arr[down,up] = 1.067*bloodflow  # Change unit [L/h] to [W/K]
        return arr

    arr83 = np.zeros((NUM_NODES, NUM_NODES))
    # Matrix offsets of segments
    CB = IDICT["CB"]                           #中央血池
    Head = IDICT["Head"]["artery"]             #动脉与头
    Neck = IDICT["Neck"]["artery"]             #动脉与脖子
    Chest = IDICT["Chest"]["artery"]           #动脉与胸部
    Back = IDICT["Back"]["artery"]             #动脉与后背
    Pelvis = IDICT["Pelvis"]["artery"]         #动脉与骨盆
    LShoulder = IDICT["LShoulder"]["artery"]   #动脉与左肩膀
    LArm = IDICT["LArm"]["artery"]             #动脉与左手臂
    LHand  = IDICT["LHand"]["artery"]          #动脉与左手
    RShoulder = IDICT["RShoulder"]["artery"]   #动脉与右肩膀
    RArm = IDICT["RArm"]["artery"]             #动脉与右手臂
    RHand = IDICT["RHand"]["artery"]           #动脉与右手
    LThigh = IDICT["LThigh"]["artery"]         #动脉与左大腿
    LLeg = IDICT["LLeg"]["artery"]             #动脉与左小腿
    LFoot = IDICT["LFoot"]["artery"]           #动脉与左脚
    RThigh = IDICT["RThigh"]["artery"]         #动脉与右大腿
    RLeg = IDICT["RLeg"]["artery"]             #动脉与右小腿
    RFoot = IDICT["RFoot"]["artery"]           #动脉与右脚


    arr83 += flow(CB, Neck, bf_art[1])           #CB to Neck.art 中央血池与脖子动脉换热
    arr83 += flow(Neck, Head, bf_art[0])         #Neck.art to Head.art 脖子动脉传热到头部动脉
    arr83 += flow(Head+1, Neck+1, bf_vein[0])    #Head.vein to Neck.vein 头部静脉到脖子静脉
    arr83 += flow(Neck+1, CB, bf_vein[1])        #Neck.vein to CB 脖子静脉到中央血池

    arr83 += flow(CB, Chest, bf_art[2])          #CB to Chest.art 中央血池到胸部动脉
    arr83 += flow(Chest+1, CB, bf_vein[2])       #Chest.vein to CB 胸部静脉到中央血池

    arr83 += flow(CB, Back, bf_art[3])           #CB to Back.art 中央血池到背部动脉
    arr83 += flow(Back+1, CB, bf_vein[3])        #Back.vein to CB 背部静脉到中央血池

    arr83 += flow(CB, Pelvis, bf_art[4])         #CB to Pelvis.art 中央血池到骨盆动脉
    arr83 += flow(Pelvis+1, CB, bf_vein[4])      #Pelvis.vein to CB 骨盆静脉到中央血池

    arr83 += flow(CB, LShoulder, bf_art[5])      #CB to LShoulder.art 中央血池到左肩膀动脉
    arr83 += flow(LShoulder, LArm, bf_art[6])    #LShoulder.art to LArm.art
    arr83 += flow(LArm, LHand, bf_art[7])        #LArm.art to LHand.art
    arr83 += flow(LHand+1, LArm+1, bf_vein[7])   #LHand.vein to LArm.vein
    arr83 += flow(LArm+1, LShoulder+1, bf_vein[6]) #LArm.vein to LShoulder.vein
    arr83 += flow(LShoulder+1, CB, bf_vein[5])   #LShoulder.vein to CB
    arr83 += flow(LHand+2, LArm+2, bf_ava_hand)  #LHand.sfvein to LArm.sfvein
    arr83 += flow(LArm+2, LShoulder+2, bf_ava_hand) #LArm.sfvein to LShoulder.sfvein
    arr83 += flow(LShoulder+2, CB, bf_ava_hand)  #LShoulder.sfvein to CB

    arr83 += flow(CB, RShoulder, bf_art[8])      #CB to RShoulder.art 中央血池到右肩膀动脉
    arr83 += flow(RShoulder, RArm, bf_art[9])    #RShoulder.art to RArm.art
    arr83 += flow(RArm, RHand, bf_art[10])       #RArm.art to RHand.art
    arr83 += flow(RHand+1, RArm+1, bf_vein[10])  #RHand.vein to RArm.vein
    arr83 += flow(RArm+1, RShoulder+1, bf_vein[9]) #RArm.vein to RShoulder.vein
    arr83 += flow(RShoulder+1, CB, bf_vein[8])   #RShoulder.vein to CB
    arr83 += flow(RHand+2, RArm+2, bf_ava_hand)  #RHand.sfvein to RArm.sfvein
    arr83 += flow(RArm+2, RShoulder+2, bf_ava_hand) #RArm.sfvein to RShoulder.sfvein
    arr83 += flow(RShoulder+2, CB, bf_ava_hand)  #RShoulder.sfvein to CB

    arr83 += flow(Pelvis, LThigh, bf_art[11])    #Pelvis to LThigh.art 骨盆动脉到左大腿动脉
    arr83 += flow(LThigh, LLeg, bf_art[12])      #LThigh.art to LLeg.art
    arr83 += flow(LLeg, LFoot, bf_art[13])       #LLeg.art to LFoot.art
    arr83 += flow(LFoot+1, LLeg+1, bf_vein[13])  #LFoot.vein to LLeg.vein
    arr83 += flow(LLeg+1, LThigh+1, bf_vein[12]) #LLeg.vein to LThigh.vein
    arr83 += flow(LThigh+1, Pelvis+1, bf_vein[11]) #LThigh.vein to Pelvis
    arr83 += flow(LFoot+2, LLeg+2, bf_ava_foot)  #LFoot.sfvein to LLeg.sfvein
    arr83 += flow(LLeg+2, LThigh+2, bf_ava_foot) #LLeg.sfvein to LThigh.sfvein
    arr83 += flow(LThigh+2, Pelvis+1, bf_ava_foot) #LThigh.vein to Pelvis

    arr83 += flow(Pelvis, RThigh, bf_art[14])    #Pelvis to RThigh.art 骨盆动脉到右大腿动脉
    arr83 += flow(RThigh, RLeg, bf_art[15])      #RThigh.art to RLeg.art
    arr83 += flow(RLeg, RFoot, bf_art[16])       #RLeg.art to RFoot.art
    arr83 += flow(RFoot+1, RLeg+1, bf_vein[16])  #RFoot.vein to RLeg.vein 右脚静脉到右小腿静脉
    arr83 += flow(RLeg+1, RThigh+1, bf_vein[15]) #RLeg.vein to RThigh.vein
    arr83 += flow(RThigh+1, Pelvis+1, bf_vein[14]) #RThigh.vein to Pelvis
    arr83 += flow(RFoot+2, RLeg+2, bf_ava_foot)  #RFoot.sfvein to RLeg.sfvein
    arr83 += flow(RLeg+2, RThigh+2, bf_ava_foot) #RLeg.sfvein to RThigh.sfvein 右小腿浅层静脉到大腿浅层静脉
    arr83 += flow(RThigh+2, Pelvis+1, bf_ava_foot) #RThigh.vein to Pelvis

    return arr83


def remove_bodyname(text): #从给定的文本中移除身体名称
    """
    Removing the body name from the parameter name.

    """

    rtext = text
    removed = None
    for bn in BODY_NAMES:
        if bn in text:
            rtext = rtext.replace(bn, "")
            removed = bn
            break
    return rtext, removed


#part 2 body construction

_BSAst = np.array([
        0.110, 0.029, 0.175, 0.161, 0.221,
        0.096, 0.063, 0.050, 0.096, 0.063, 0.050,
        0.209, 0.112, 0.056, 0.209, 0.112, 0.056,]) 
#JOS-3 模型中的人体各个节段的表面积比例来自于 65-MN 模型以及 Smith 模型中的比例（头部及颈部的表面积比例）
#各个身体节段的表面积比例，通过“胡咏梅，关于中国人体表面积公式的研究”修正

dubois = lambda height, weight: 0.2042 * (height ** 0.725) * (weight ** 0.425) #杜氏公式
china = lambda height, weight: 0.586*height + 0.0126*weight - 0.0461 
#选择计算体表面积的公式（中国标准女性）赵松山, 刘友梅, 姚家邦, 杨增仁, 梁月琴, 张是敬. 中国成年女子体表面积的测量[J]. 营养学报1987,9:200-207. 赵松山, 刘友梅, 姚家邦, 高书旺, 张是敬. 中国成年男子体表面积的测量[J]. 营养学报 1984,6:87-95. 
fujimoto = lambda height, weight: 0.1882 * (height ** 0.663) * (weight ** 0.444)
kurazumi = lambda height, weight: 0.2440 * (height ** 0.693) * (weight ** 0.383)

def body_surface_area(height=1.62, weight=56, equation="china",):
    """
    Calculate body surface area (BSA) [m2].计算体表面积

    Parameters
    ----------
    height : float, optional,Body height [m]. The default of JOS-3 is 1.72. 改为问卷结果
    weight : float, optional,Body weight [kg]. The default of JOS-3  is 74.43. 改为问卷结果
    equation : str, optional
        The equation name (str) of bsa calculation. Choose a name from "dubois",
        "china", "fujimoto", or "kurazumi". 

    Returns
    -------
    bsa : float,Body surface area (BSA) [m2].
    """

    if equation == "dubois":
        bsa = dubois(height, weight)
    elif equation == "china":
        bsa = china(height, weight)
    elif equation == "fujimoto":
        bsa = fujimoto(height, weight)
    elif equation == "kurazumi":
        bsa = kurazumi(height, weight)

    return bsa


def bsa_rate(height=1.62, weight=56, equation="china",):
    """
    Calculate the rate of BSA to standard body.计算体表面积与标准体表面积的比率。

    Parameters
    ----------
    height : float, optional, Body height [m]. The default is 1.72.
    weight : float, optional, Body weight [kg]. The default is 74.43.
    equation : str, optional, The equation name (str) of bsa calculation. Choose a name from "dubois", "takahira", "fujimoto", or "kurazumi". The default is "dubois".

    Returns
    -------
    bsa_rate : float
        The ratio of BSA to the standard body [-].
    """
    bsa_all = body_surface_area(height, weight, equation,)
    bsa_rate = bsa_all/_BSAst.sum()  # The BSA ratio to the standard body (1.87m2)
    return bsa_rate


def localbsa(height=1.62, weight=56, equation="china",):
    """
    Calculate local body surface area (BSA) [m2].

    The local body surface area has been derived from 65MN.
    The head have been devided to head and neck based on Smith's model.
        Head = 0.1396*0.1117/0.1414 (65MN_Head * Smith_Head / Smith_Head+Neck)
        Neck = 0.1396*0.0297/0.1414 (65MN_Head * Smith_Neck / Smith_Head+Neck)

    Parameters
    ----------
    height : float, optional, Body height [m]. 
    weight : float, optional, Body weight [kg]. 
    equation : str, optional
        The equation name (str) of bsa calculation. Choose a name from "dubois",
        "takahira", "fujimoto", or "kurazumi". The default is "dubois".

    Returns
    -------
    localbsa : ndarray(17,), Local body surface area (BSA) [m2].
    bsa_rate : float, The ratio of BSA to the standard body [-].

    """
    _bsa_rate = bsa_rate(height, weight, equation,)  # The BSA ratio to the standard body (1.87m2)
    bsa = _BSAst * _bsa_rate
    return bsa


def weight_rate(weight=56,):
    """
    Calculate the ratio of the body weitht to the standard body (74.43 kg).

    The standard values of local body weights are as below.
        weight_local = np.array([
            3.18, 0.84, 12.4, 11.03, 17.57,
            2.16, 1.37, 0.34, 2.16, 1.37, 0.34,
            7.01, 3.34, 0.48, 7.01, 3.34, 0.48])
    The data have been derived from 65MN.
    The weight of neck is extracted from the weight of 65MN's head based on
    the local body surface area of Smith's model.颈部重量从头部重量中提取，基于史密斯模型。

    Parameters
    ----------
    weight : float, optional
        The body weight [kg]. The default is 74.43.

    Returns
    -------
    weight_rate : float
        The ratio of the body weight to the standard body (74.43 kg).
        weight_rate = weight / 74.43
    """
    rate = weight / 74.43
    return rate


def bfb_rate(height=1.62, weight=56, equation="china", age=36, ci=2.19,):
    """
    Calculate the ratio of basal blood flow (BFB) of the standard body (290 L/h).计算标准体的基础血流量。

    Parameters
    ----------
    height : float, optional, Body height [m]. The default is 1.76.
    weight : float, optional, Body weight [kg]. The default is 56.
    equation : str, optional
    心输出量（cardiac output，CO）是指左或右心室每分钟泵出的血液量。即心率与每搏出量的乘积。
    CO = 0.024 × 𝑊eight − 0.057 × 𝐴g𝑒 − 0.305 × sex + 4.544
    age : float, optional, Age [years]. The default is 20.
    ci : float, optional, Cardiac index，心脏指数是指单位体表面积的心排出量 [L/min/㎡]. \\Cardiac Index = Cardiac Output / Body Surface Area\\ Cardiac Output=0.024*Weight-0.057*age-0.305*gender+4.544\\male=0,female=1

    Returns
    -------
    bfb_rate : float, Basal blood flow rate. 
    """

    ci *= 60  # Change unit [L/min/㎡] to [L/h/㎡]

    # Decrease of BFB by aging 血流量随年龄变化，修正为CI = CO / BSA =  (0.024 × weight - 0.057 × age - 0.305 × sex + 4.544)/(0.586 × height + 0.0126 × weight-0.0461)
    if age < 50:
        ci *= 1
    elif age < 60:
        ci *= 0.85
    elif age < 70:
        ci *= 0.75
    else:  # age >= 70
        ci *= 0.7

    bfb_all = ci * bsa_rate(height, weight, equation) * _BSAst.sum()  # [L/h]
    _bfb_rate = bfb_all / 290
    return _bfb_rate #使用修正公式计算后不执行年龄修正


def conductance(height=1.62, weight=56, equation="china", fat=33,):
    """
    Calculate thermal conductance between layers [W/K].计算层间的导热系数

    Parameters
    ----------
    height : float, optional
        Body height [m]. The default of jos-3 is 1.72.
    weight : float, optional
        Body weight [kg]. The default of jos-3 is 74.43.
    equation : str, optional
        The equation name (str) of bsa calculation. Choose a name from "dubois",
        "china", "fujimoto", or "kurazumi". The default is "dubois".
    fat : float, optional
        Body fat rate [%]. 

    Returns
    -------
    conductance : numpy.ndarray
        Thermal conductance between layers [W/K].
        The shape is (NUM_NODES, NUM_NODES).
    """
    #根据体脂率修改导热系数
    if fat < 12.5:
        cdt_cr_sk = np.array([
                1.341, 0.930, 1.879, 1.729, 2.370,
                1.557, 1.018, 2.210, 1.557, 1.018, 2.210,
                2.565, 1.378, 3.404, 2.565, 1.378, 3.404
                ])
    elif fat < 17.5:
        cdt_cr_sk = np.array([
                1.311, 0.909, 1.785, 1.643, 2.251,
                1.501, 0.982, 2.183, 1.501, 0.982, 2.183,
                2.468, 1.326, 3.370, 2.468, 1.326, 3.370
                ])
    elif fat < 22.5:
        cdt_cr_sk = np.array([
                1.282, 0.889, 1.698, 1.563, 2.142,
                1.448, 0.947, 2.156, 1.448, 0.947, 2.156,
                2.375, 1.276, 3.337, 2.375, 1.276, 3.337
                ])
    elif fat < 27.5:
        cdt_cr_sk = np.array([
                1.255, 0.870, 1.618, 1.488, 2.040,
                1.396, 0.913, 2.130, 1.396, 0.913, 2.130,
                2.285, 1.227, 3.304, 2.285, 1.227, 3.304
                ])
    else: #fat >= 27.5
        cdt_cr_sk = np.array([
                1.227, 0.852, 1.542, 1.419, 1.945,
                1.346, 0.880, 1.945, 1.346, 0.880, 1.945,
                2.198, 1.181, 3.271, 2.198, 1.181, 3.271
                ])

    cdt_cr_ms = np.zeros(17)   # core to muscle [W/K] 核心层到肌肉层
    cdt_ms_fat = np.zeros(17)  # muscle to fat [W/K]  肌肉层到脂肪层
    cdt_fat_sk = np.zeros(17)  # fat to skin [W/K]    脂肪层到皮肤层

    # Head and Pelvis consists of 65MN's conductances 头部和骨盆由65MN的热阻组成
    cdt_cr_ms[0] = 1.601  # Head 头部
    cdt_ms_fat[0] = 13.222
    cdt_fat_sk[0] = 16.008
    cdt_cr_ms[4] = 3.0813  # Pelvis 骨盆
    cdt_ms_fat[4] = 10.3738
    cdt_fat_sk[4] = 41.4954

    # vessel to core 核心层构成
    # The shape is a cylinder. 形状为圆柱体
    # It is assumed that the inner is vascular radius, 2.5mm and the outer is stolwijk's core radius. 核心半径来自stolwijk模型
    # The heat transer coefficient of the core is assumed as the Michel's counter-flow model 0.66816 [W/(m･K)]. 核心传热系数参考Michel
    cdt_ves_cr = np.array([
            0, 0, 0, 0, 0,
            0.586, 0.383, 1.534, 0.586, 0.383, 1.534,
            0.810, 0.435, 1.816, 0.810, 0.435, 1.816,])
    #superficial vein to skin 皮肤浅静脉
    cdt_sfv_sk = np.array([
            0, 0, 0, 0, 0,
            57.735, 37.768, 16.634, 57.735, 37.768, 16.634,
            102.012, 54.784, 24.277, 102.012, 54.784, 24.277,])

    # art to vein (counter-flow) [W/K]
    # The data has been derived Mitchell's model.
    # THe values = 15.869 [W/(m･K)] * the segment lenght [m]
    cdt_art_vein = np.array([
            0, 0, 0, 0, 0,
            0.537, 0.351, 0.762, 0.537, 0.351, 0.762,
            0.826, 0.444, 0.992, 0.826, 0.444, 0.992
            ])

    # Changes values by body size based on the standard body. 根据标准人体更改值。
    wr = weight_rate(weight)
    bsar = bsa_rate(height, weight, equation)
    # Head, Neck (Sphere shape) 头，脖子（圆球）
    cdt_cr_sk[:2] *= wr/bsar
    cdt_cr_ms[:2] *= wr/bsar
    cdt_ms_fat[:2] *= wr/bsar
    cdt_fat_sk[:2] *= wr/bsar
    cdt_ves_cr[:2] *= wr/bsar
    cdt_sfv_sk[:2] *= wr/bsar
    cdt_art_vein[:2] *= wr/bsar
    # Others (Cylinder shape) 其他（圆柱体）
    cdt_cr_sk[2:] *= bsar**2/wr
    cdt_cr_ms[2:] *= bsar**2/wr
    cdt_ms_fat[2:] *= bsar**2/wr
    cdt_fat_sk[2:] *= bsar**2/wr
    cdt_ves_cr[2:] *= bsar**2/wr
    cdt_sfv_sk[2:] *= bsar**2/wr
    cdt_art_vein[2:] *= bsar**2/wr

    cdt_whole = np.zeros((NUM_NODES, NUM_NODES))
    for i, bn in enumerate(BODY_NAMES):
        # Dictionary of indecies in each body segment
        # key = layer name, value = index of matrix
        indexof = IDICT[bn]

        # Common
        cdt_whole[indexof["artery"], indexof["vein"]] = cdt_art_vein[i]  # art to vein   动脉到静脉
        cdt_whole[indexof["artery"], indexof["core"]] = cdt_ves_cr[i]    # art to cr     动脉到核心层
        cdt_whole[indexof["vein"], indexof["core"]] = cdt_ves_cr[i]      # vein to cr    静脉到核心层

        # Only limbs
        if i >= 5:
            cdt_whole[indexof["sfvein"], indexof["skin"]] = cdt_sfv_sk[i]  # sfv to sk 皮肤浅静脉到皮肤

        # If the segment has a muscle or fat layer 如果节段有肌肉或脂肪层
        if not indexof["muscle"] is None:  # or not indexof["fat"] is None
            cdt_whole[indexof["core"], indexof["muscle"]] = cdt_cr_ms[i]  # cr to ms    核心到肌肉
            cdt_whole[indexof["muscle"], indexof["fat"]] = cdt_ms_fat[i]  # ms to fat   肌肉到脂肪
            cdt_whole[indexof["fat"], indexof["skin"]] = cdt_fat_sk[i]    # fat to sk   脂肪到皮肤

        else:
            cdt_whole[indexof["core"], indexof["skin"]] = cdt_cr_sk[i]    # cr to sk    核心到皮肤

    # Creates a symmetrical matrix 创建对称矩阵
    cdt_whole = cdt_whole + cdt_whole.T

    return cdt_whole.copy()


def capacity(height=1.62, weight=56, equation="china", age=36, ci=2.19):
    """
    Calculate the thermal capacity [J/K]. 计算热容量

    The values of vascular and central blood capacity have been derived from Yokoyama's model. 血池和中央血池容量的值来自Yokoyama。
    The specific heat of blood is assumed as 1.0 [kcal/L.K].

    Parameters
    ----------
    height : float, optional,Body height [m]. 
    weight : float, optional,Body weight [kg]. 
    equation : str, optional
        The equation name (str) of bsa calculation. Choose a name from "dubois",
        "china", "fujimoto", or "kurazumi". 
    age : float, optional,Age [years]. 
    ci : float, optional,Cardiac index [L/min/㎡]. 

    Returns
    -------
    capacity : numpy.ndarray.
        Thermal capacity [W/K].
        The shape is (NUM_NODES).
    """
    # artery [Wh/K] 动脉
    cap_art = np.array([
            0.096, 0.025, 0.12, 0.111, 0.265,
            0.0186, 0.0091, 0.0044, 0.0186, 0.0091, 0.0044,
            0.0813, 0.04, 0.0103, 0.0813, 0.04, 0.0103,])

    # vein [Wh/K] 静脉
    cap_vein = np.array([
            0.321, 0.085, 0.424, 0.39, 0.832,
            0.046, 0.024, 0.01, 0.046, 0.024, 0.01,
            0.207, 0.1, 0.024, 0.207, 0.1, 0.024,])

    # superficial vein [Wh/K] 浅层静脉
    cap_sfv = np.array([
            0, 0, 0, 0, 0,
            0.025, 0.015, 0.011, 0.025, 0.015, 0.011,
            0.074, 0.05, 0.021, 0.074, 0.05, 0.021,])

    # central blood [Wh/K] 中央血池
    cap_cb = 1.999

    # core [Wh/K] 核心层
    cap_cr = np.array([
            1.7229, 0.564, 10.2975, 9.3935, 4.488,
            1.6994, 1.1209, 0.1536, 1.6994, 1.1209, 0.1536,
            5.3117, 2.867, 0.2097, 5.3117, 2.867, 0.2097,])

    # muscle [Wh/K] 肌肉层
    cap_ms = np.array([
            0.305, 0.0, 0.0, 0.0, 7.409,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,])

    # fat [Wh/K] 脂肪层
    cap_fat = np.array([
            0.203, 0.0, 0.0, 0.0, 1.947,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,])

    # skin [Wh/K] 皮肤层
    cap_sk = np.array([
            0.1885, 0.058, 0.441, 0.406, 0.556,
            0.126, 0.084, 0.088, 0.126, 0.084, 0.088,
            0.334, 0.169, 0.107, 0.334, 0.169, 0.107,])

    # Changes the values based on the standard body 基于标准人体更改值
    bfbr = bfb_rate(height, weight, equation, age, ci)
    wr = weight_rate(weight)
    cap_art *= bfbr
    cap_vein *= bfbr
    cap_sfv *= bfbr
    cap_cb *= bfbr
    cap_cr *= wr
    cap_ms *= wr
    cap_fat *= wr
    cap_sk *= wr

    cap_whole = np.zeros(NUM_NODES)
    cap_whole[0] = cap_cb

    for i, bn in enumerate(BODY_NAMES): #更新 cap_whole 数组中的元素
        # Dictionary of indecies in each body segment
        # key = layer name, value = index of matrix
        indexof = IDICT[bn]

        # Common
        cap_whole[indexof["artery"]] = cap_art[i]
        cap_whole[indexof["vein"]] = cap_vein[i]
        cap_whole[indexof["core"]] = cap_cr[i]
        cap_whole[indexof["skin"]] = cap_sk[i]

        # Only limbs 肢体
        if i >= 5:
            cap_whole[indexof["sfvein"]] = cap_sfv[i]

        # If the segment has a muscle or fat layer 有肌肉或者脂肪层
        if not indexof["muscle"] is None:  # or not indexof["fat"] is None
            cap_whole[indexof["muscle"]] = cap_ms[i]
            cap_whole[indexof["fat"]] = cap_fat[i]

    cap_whole *= 3600  # Changes unit [Wh/K] to [J/K]
    return cap_whole


#part 3 thermal regulation

import math

_BSAst = np.array([
        0.110, 0.029, 0.175, 0.161, 0.221,
        0.096, 0.063, 0.050, 0.096, 0.063, 0.050,
        0.209, 0.112, 0.056, 0.209, 0.112, 0.056,])


def conv_coef(posture="standing", va=0.1, ta=28.8, tsk=34.0,):
    """
    Calculate convective heat transfer coefficient (hc) [W/K.m2] 对流换热系数
    
    Parameters
    ----------
    posture : str, optional,Select posture from standing, sitting or lying. 从站、坐或躺中选择姿势, The default is "standing".
    va : float or iter, optionalAir velocity [m/s]. If iter is input, its length should be 17.The default is 0.1.
    ta : float ,r iter, optional,Air temperature [oC]. If iter is input, its length should be 17.The default is 28.8.
    tsk : float or iter, optional
    Skin temperature [oC]. If iter is input, its length should be 17.The default is 34.0.

    Returns
    -------
    hc : numpy.ndarray
        Convective heat transfer coefficient (hc) [W/K.m2].

    """

    #对流换热系数及辐射换热系数两种修正方法
    #1.CFD获取，对流换热系数直接获取，辐射换热系数间接计算得到
    #2.经验公式修正，JOS-3模型源文件采用的方法，可通过非均匀环境实验获取建立的经验公式
    # Natural convection 自然对流
    if posture.lower() == "standing":
        # Analysis of natural and forced convection heat losses from a thermal manikin: Comparative assessment of the static and dynamic postures. J. Wind Eng. Ind. Aerodyn. 132 (2014) 66–76
        #http://dx.doi.org/10.1016/j.jweia.2014.06.019 颈部hc取头部的值
        hc_natural = np.array([
                4.3, 4.3, 2.8, 2.3, 2.8,
                3.2, 3.7, 5.3, 3.4, 3.6, 4.1,
                3.9, 3.4, 4.4, 3.9, 3.9, 4.4,])

    elif posture.lower() in ["sitting", "sedentary"]:
        # Ichihara et al., 1997, https://doi.org/10.3130/aija.62.45_5 JOS-3默认
        hc_natural = np.array([
                4.75, 4.75, 3.12, 2.48, 1.84,
                3.76, 3.62, 2.06, 3.76, 3.62, 2.06,
                2.98, 2.98, 2.62, 2.98, 2.98, 2.62,])

    # Forced convection 强制对流
    # 基于营造及评价非均匀热环境目标的人体对流换热系数研究* 暖通空调 HV&AC 2023年第53卷第9期 ；向下气流取值
    hc_a = np.array([
            9.29, 9.29, 7.67, 8.09, 8.3,
            13.96, 15.04, 18.62, 12.5, 13.98, 19.11,
            10.58, 12.88, 11.29, 10.18, 10.18, 12.33,])
    hc_b = np.array([
            0.5, 0.5, 0.7, 0.36, 0.59,
            0.61, 0.53, 0.54, 0.52, 0.48, 0.55,
            0.54, 0.44, 0.39, 0.49, 0.48, 0.46,])
    hc_forced = hc_a * (va ** hc_b)

    # Select natural or forced hc.自然对流，强制对流
    # If local va is under 0.2 m/s, the hc valuse is natural. 低于0.2为自然对流
    hc = np.where(va<0.2, hc_natural, hc_forced) # hc [W/K.m2)]

    return hc


def rad_coef(posture="standing"): #辐射换热系数
    """
    Calculate radiative heat transfer coefficient (hr) [W/K.m2]
    
    Parameters 
    ----------
    posture : str, optional,Select posture from standing, sitting or lying. The default is "standing".

    Returns
    -------
    hc : numpy.ndarray
        Radiative heat transfer coefficient (hr) [W/K.m2]. 计算辐射传热系数

    """
    
    
    if posture.lower() == "standing":
        # 修正：Quintela, D., Gaspar, A., Borges, C., 2004. Analysis of sensible heat exchanges from athermal manikin. Eur. J. Appl. Physiol. 92, 663–668, http://dx.doi.org/10.1007/s00421-004-1132-3.
        hr = np.array([
                5.7, 5.7, 4.2 ,4.5, 4.5,
                4.5, 4.9, 4.3, 4.2, 4.1, 4.1,
                4.8, 5, 5, 4.4, 5.1, 5,])
    elif posture.lower() in ["sitting", "sedentary"]:
        # Ichihara et al., 1997, https://doi.org/10.3130/aija.62.45_5
        hr = np.array([
                4.96, 4.96, 3.99, 4.64, 4.21,
                4.96, 4.21, 4.74, 4.96, 4.21, 4.74,
                4.10, 4.74, 6.36, 4.10, 4.74, 6.36,])
    return hr


def fixed_hc(hc, va):
    """
    Fixes hc values to fit tow-node-model's values. 修正hc值以适合二节点模型。
    """
    mean_hc = np.average(hc, weights=_BSAst)
    mean_va = np.average(va, weights=_BSAst)
    mean_hc_whole = max(3, 8.600001*(mean_va**0.53))
    _fixed_hc = hc * mean_hc_whole/mean_hc
    return _fixed_hc


def fixed_hr(hr):
    """
    Fixes hr values to fit tow-node-model's values. 修正hr值以适合二节点模型。
    """
    mean_hr = np.average(hr, weights=_BSAst)
    _fixed_hr = hr * 4.7/mean_hr
    return _fixed_hr

def operative_temp(ta, tr, hc, hr): #计算操作温度
    to = (hc*ta + hr*tr) / (hc + hr)
    return to


def clo_area_factor(clo): #计算服装面积修正因子（clothing area factor）根据服装的热阻水平来调整服装对热传递的影响。在低热阻的情况下，修正因子的增加可能更大，而在高热阻的情况下，增加相对较小。
    fcl = np.where(clo<0.5, clo*0.2+1, clo*0.1+1.05)
    return fcl


def dry_r(hc, hr, clo):
    """
    Calculate total sensible thermal resistance. 计算总显热阻。

    Parameters
    ----------
    hc : float or array, Convective heat transfer coefficient (hc) [W/K.m2].
    hr : float or array, Radiative heat transfer coefficient (hr) [W/K.m2].
    clo : float or array, Clothing insulation [clo].

    Returns
    -------
    rt : float or array, Total sensible thermal resistance between skin and ambient.
    """
    fcl = clo_area_factor(clo)
    r_a = 1/(hc+hr)
    r_cl = 0.155*clo
    r_t = r_a/fcl + r_cl
    return r_t


def wet_r(hc, clo, iclo, lewis_rate=16.5): 
    """
    Calculate total evaporative thermal resistance.

    Parameters
    ----------
    hc : float or array, Convective heat transfer coefficient (hc) [W/K.m2].
    clo : float or array, Clothing insulation [clo].
    iclo : float, or array, optional, Clothing vapor permeation efficiency [-]. The default is 0.45. 服装蒸汽渗透效率
    lewis_rate : float, optional, Lewis rate [K/kPa]. The default is 16.5. 路易斯数，如果环境压力变化需要修正

    Returns
    -------
    ret : float or array, Total evaporative thermal resistance.

    """
    #参考EN A-夏季  EN-D-冬季 结果 Measurement of local evaporative resistance of atypical clothing ensemble using a sweating thermal manikin. doi: 10.1002/2475-8876.12124
    fcl = clo_area_factor(clo)
    r_cl = 0.155 * clo
    r_ea = 1 / (lewis_rate * hc)
    r_ecl = r_cl / (lewis_rate * iclo)
    r_et = r_ea / fcl + r_ecl
    return r_et


def heat_resistances(
        ta=np.ones(17)*26,
        tr=np.ones(17)*26,
        va=np.ones(17)*0.05,
        tsk=np.ones(17)*34,
        clo=np.array([0, 1.37, 1.37, 1.37, 1.37, 1.37, 1.37, 1.37, 1.37, 1.37, 1.37, 1.37, 1.37, 1.37, 1.37, 1.37, 1.37,]),  
        #夏季短衣短裤(夏季头部、颈部、小臂、手部、小腿-0)，ASHRAE 55-2017 冬季长保温衣服裤子 (冬季头部、手部=0)
        posture="standing",
        iclo=np.array([0.01, 0.01, 1.13, 0.5, 1.78, 0.51, 0.39, 0, 0.51, 0.39, 0, 0.4, 0.07, 0.62, 0.4, 0.07, 0.62,]),  
        #参考EN A结果 Measurement of local evaporative resistance of atypical clothing ensemble using a sweating thermal manikin. doi: 10.1002/2475-8876.12124
        options={},):

    hc = fixed_hc(conv_coef(posture, va, ta, tsk,))
    hr = fixed_hr(rad_coef(posture,))
    to = operative_temp(ta, tr, hc, hr,)
    fcl = clo_area_factor(clo,)
    r_t, r_a, r_cl = dry_r(hc, hr, clo)
    r_et, r_ea, r_ecl = wet_r(hc, clo, iclo)

    return to, r_t, r_et, r_a, r_cl, r_ea, r_ecl, fcl


def error_signals(err_cr=0, err_sk=0):
    """
    Calculate WRMS and CLDS signals of thermoregulation

    Parameters
    ----------
    err_cr, err_sk : float or array, optional, Difference between setpoint and body temperatures.The default is 0.温度设定点与身体温度的误差

    Returns
    -------
    wrms, clds : array, WRMS and CLDS signals.
    """

    # SKINR
    receptor = np.array([
            0.0549, 0.0146, 0.1492, 0.1321, 0.2122,
            0.0227, 0.0117, 0.0923, 0.0227, 0.0117, 0.0923,
            0.0501, 0.0251, 0.0167, 0.0501, 0.0251, 0.0167,])

    # wrms signal 温暖信号
    wrm = np.maximum(err_sk, 0) 
    wrm *= receptor
    wrms = wrm.sum() 
    # clds signal 寒冷信号
    cld = np.minimum(err_sk, 0) 
    cld *= -receptor
    clds = cld.sum()

    return wrms, clds


# Antoine equation [kPa] 安托万方程，安托万方程是一种用于描述物质的饱和蒸气压与温度之间关系的经验方程。
antoine = lambda x: math.e**(16.6536-(4030.183/(x+235)))
# Tetens equation [kPa] 塔费尔方程，塔费尔方程是另一种描述水蒸气饱和压力的经验方程。
tetens = lambda x: 0.61078*10**(7.5*x/(x+237.3))


def evaporation(err_cr, err_sk, tsk, ta, rh, ret, 
                height=1.62, weight=56, equation="china", age=36):
    """
    Calculate evaporative heat loss. 计算蒸发热损失。

    Parameters
    ----------
    err_cr, err_sk : array, Difference between setpoint and body temperatures [oC].
    tsk : array, Skin temperatures [oC].
    ta : array, Air temperatures at local body segments [oC].
    rh : array, Relative humidity at local body segments [%].
    ret : array, Total evaporative thermal resistances [m2.K/W].
    height : float, optional,Body height [m]. The default is 1.72.
    weight : float, optional,Body weight [kg]. The default is 74.43.
    equation : str, optional
        The equation name (str) of bsa calculation. Choose a name from "dubois",
        "takahira", "fujimoto", or "kurazumi". The default is "dubois".
    age : float, optional, Age [years]. The default is 20.

    Returns
    -------
    wet : array, Local skin wettedness [-].
    e_sk : array, Evaporative heat loss at the skin by sweating and diffuse [W].
    e_max : array, Maximum evaporative heat loss at the skin [W].
    e_sweat : TYPE, Evaporative heat loss at the skin by only sweating [W].

    """

    wrms, clds = error_signals(err_cr, err_sk,)      # Thermoregulation signals 热调节信号
    bsar = bsa_rate(height, weight, equation,)       # BSA rate 表面积率
    bsa = _BSAst * bsar                              # BSA 表面积
    p_a = antoine(ta)*rh/100                         # Saturated vapor pressure of ambient [kPa] 环境饱和蒸汽压
    p_sk_s = antoine(tsk)                            # Saturated vapor pressure at the skin [kPa] 皮肤的饱和蒸汽压
    e_max = (p_sk_s - p_a) / ret * bsa               # Maximum evaporative heat loss 最大蒸发热损失

    # SKINS
    skin_sweat = np.array([
            0.064, 0.017, 0.146, 0.129, 0.206,
            0.051, 0.026, 0.0155, 0.051, 0.026, 0.0155,
            0.073, 0.036, 0.0175, 0.073, 0.036, 0.0175,])

    sig_sweat = (371.2*err_cr[0]) + (33.64*(wrms-clds))
    sig_sweat = max(sig_sweat, 0)
    sig_sweat *= bsar

    # Signal decrement by aging 年龄导致的信号衰减
    if age < 60:
        sd_sweat = np.ones(17)
    else: #age >= 60
        sd_sweat = np.array([
                0.69, 0.69, 0.59, 0.52, 0.40,
                0.75, 0.75, 0.75, 0.75, 0.75, 0.75,
                0.40, 0.40, 0.40, 0.40, 0.40, 0.40,])

    e_sweat = skin_sweat * sig_sweat * sd_sweat * 2**((err_sk)/10)
    wet = 0.06 + 0.94*(e_sweat/e_max)
    wet = np.minimum(wet, 1)  # Wettedness' upper limit 湿润度上限
    e_sk = wet * e_max
    e_sweat = (wet - 0.06) / 0.94 * e_max  # Effective sweating 有效出汗
    return wet, e_sk, e_max, e_sweat


def skin_bloodflow(err_cr, err_sk, 
        height=1.62, weight=56, equation="china", age=36, ci=2.19,): #计算皮肤血流速率（BFsk）
    """
    Calculate skin blood flow rate (BFsk) [L/h].

    Parameters
    ----------
    err_cr, err_sk : array, Difference between setpoint and body temperatures [oC].
    height : float, optional, Body height [m]. The default is 1.72.
    weight : float, optional, Body weight [kg]. The default is 74.43.
    equation : str, optional, The equation name (str) of bsa calculation. Choose a name from "dubois",
        "takahira", "fujimoto", or "kurazumi". The default is "dubois".
    age : float, optional, Age [years]. The default is 20.
    ci : float, optional, Cardiac index [L/min/㎡]. The default is 2.59.

    Returns
    -------
    BFsk : array, Skin blood flow rate [L/h].

    """

    wrms, clds = error_signals(err_cr, err_sk)

    # BFBsk 皮肤血流量
    bfb_sk = np.array([
            1.754, 0.325, 1.967, 1.475, 2.272,
            0.91, 0.508, 1.114, 0.91, 0.508, 1.114,
            1.456, 0.651, 0.934, 1.456, 0.651, 0.934,])
    # SKIND
    skin_dilat = np.array([
            0.0692, 0.0992, 0.0580, 0.0679, 0.0707,
            0.0400, 0.0373, 0.0632, 0.0400, 0.0373, 0.0632,
            0.0736, 0.0411, 0.0623, 0.0736, 0.0411, 0.0623,])
    # SKINC
    skin_stric = np.array([
            0.0213, 0.0213, 0.0638, 0.0638, 0.0638,
            0.0213, 0.0213, 0.1489, 0.0213, 0.0213, 0.1489,
            0.0213, 0.0213, 0.1489, 0.0213, 0.0213, 0.1489,])

    sig_dilat = (100.5*err_cr[0]) + (6.4*(wrms-clds))
    sig_stric = (-10.8*err_cr[0]) + (-10.8*(wrms-clds))
    sig_dilat = max(sig_dilat, 0)
    sig_stric = max(sig_stric, 0)

    # Signal decrement by aging
    if age < 60:
        sd_dilat = np.ones(17)
        sd_stric = np.ones(17)
    else: #age >= 60
        sd_dilat = np.array([
                0.91, 0.91, 0.47, 0.47, 0.31,
                0.47, 0.47, 0.47, 0.47, 0.47, 0.47,
                0.31, 0.31, 0.31, 0.31, 0.31, 0.31,
                ])
        sd_stric = np.ones(17)

    #皮肤血流量 [L/h]
    bf_sk = (1 + skin_dilat * sd_dilat * sig_dilat) / \
            (1 + skin_stric * sd_stric * sig_stric) * bfb_sk * 2**(err_sk/6)
    
    bfbr = bfb_rate(height, weight, equation, age, ci,)
    bf_sk *= bfbr
    return bf_sk


def ava_bloodflow(err_cr, err_sk, 
        height=1.62, weight=56, equation="china", age=36, ci=2.19,): #计算动脉-静脉吻合血流速率（AVA）
    """
    Calculate areteriovenous anastmoses (AVA) blood flow rate [L/h] based on Takemori's 竹森 model, 1995.

    Parameters
    ----------
    err_cr, err_sk : array, Difference between setpoint and body temperatures [oC].
    height : float, optional, Body height [m]. The default is 1.72.
    weight : float, optional, Body weight [kg]. The default is 74.43.
    equation : str, optional
        The equation name (str) of bsa calculation. Choose a name from "dubois",
        "takahira", "fujimoto", or "kurazumi". The default is "dubois".
    age : float, optional, Age [years]. The default is 20.
    ci : float, optional, Cardiac index [L/min/m2]. The default is 2.59.

    Returns
    -------
    BFava_hand, BFava_foot : array, AVA blood flow rate at hand and foot [L/h].

    """
    # Cal. mean error body core temp. 核心温度平均误差
    cap_bcr = [10.2975, 9.3935, 13.834]  # Thermal capacity at Chest, Back and Pelvis 胸部、背部和骨盆的热容
    err_bcr = np.average(err_cr[2:5], weights=cap_bcr)

    # Cal. mean error skin temp. 皮肤温度平均误差
    bsa = _BSAst
    err_msk = np.average(err_sk, weights=bsa)

    # Openbess of AVA [-]
    sig_ava_hand = 0.265 * (err_bcr + 0.43) + 0.953 * (err_msk + 0.1905) + 0.9126
    sig_ava_foot = 0.265 * (err_bcr - 0.97) + 0.953 * (err_msk - 0.0095) + 0.9126

    sig_ava_hand = min(sig_ava_hand, 1)
    sig_ava_hand = max(sig_ava_hand, 0)
    sig_ava_foot = min(sig_ava_foot, 1)
    sig_ava_foot = max(sig_ava_foot, 0)

    bfbr = bfbr = bfb_rate(height, weight, equation, age, ci,)
    # AVA blood flow rate [L/h]
    bf_ava_hand = 1.71 * bfbr * sig_ava_hand  # Hand
    bf_ava_foot = 2.16 * bfbr * sig_ava_foot  # Foot
    return bf_ava_hand, bf_ava_foot


def basal_met(height=1.62, weight=56, age=36,
            sex="female", equation="Chinese"):
    """
    Calculate basal metabolic rate [W]. 基础代谢率

    Parameters
    ----------
    height : float, optional, body height [m]. The default is 1.72.
    weight : float, optional, Body weight [kg]. The default is 74.43.
    age : float, optional, Age [years]. The default is 20.
    sex : str, optional, Choose male or female. The default is "male".
    equation : str, optional, Choose harris-benedict or ganpule. The default is "harris-benedict".

    Returns
    -------
    BMR : float, Basal metabolic rate [W].

    """

    if equation=="harris-benedict":
        if sex=="male":
            bmr = 88.362 + 13.397*weight + 500.3*height - 5.677*age #西方人体建立harris公式
        else:
            bmr = 88.362 + 13.397*weight + 500.3*height - 5.677*age

    elif equation=="Chinese":
        if sex=="male":
            bmr = 13.88*weight + 416*height - 3.43*age + 54.34
        else:
            bmr = 13.88*weight + 416*height - 3.43*age - 112.4 + 54.34 #LIU equation（中国台湾）

    elif equation=="japanese" or equation=="ganpule":
        # Ganpule et al., 2007, https://doi.org/10.1038/sj.ejcn.1602645
        if sex=="male":
            bmr = 0.0481*weight + 2.34*height - 0.0138*age - 0.4235
        else:
            bmr = 0.0481*weight + 2.34*height - 0.0138*age - 0.9708
        bmr *= 1000 / 4.186

    bmr *= 0.048  # [kcal/day] to [W]

    return bmr


def local_mbase(height=1.62, weight=56, age=36,
            sex="female", equation="Chinese"):
    """
    Calculate local basal metabolic rate [W].

    Parameters
    ----------
    height : float, optional,Body height [m]. The default is 1.72.
    weight : float, optional, Body weight [kg]. The default is 74.43.
    age : float, optional, Age [years]. The default is 20.
    sex : str, optional, Choose male or female. The default is "male".
    equation : str, optional, Choose harris-benedict or ganpule. The default is "harris-benedict".

    Returns
    -------
    mbase : array, Local basal metabolic rate (Mbase) [W].基础代谢量

    """

    mbase_all = basal_met(height, weight, age, sex, equation)
    # Distribution coefficient of basal metabolic rate 基础代谢率分布系数
    mbf_cr = np.array([
            0.19551, 0.00324, 0.28689, 0.25677, 0.09509,
            0.01435, 0.00409, 0.00106, 0.01435, 0.00409, 0.00106,
            0.01557, 0.00422, 0.00250, 0.01557, 0.00422, 0.00250,])
    mbf_ms = np.array([
            0.00252, 0.0, 0.0, 0.0, 0.04804,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,])
    mbf_fat = np.array([
            0.00127, 0.0, 0.0, 0.0, 0.00950,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,])
    mbf_sk = np.array([
            0.00152, 0.00033, 0.00211, 0.00187, 0.00300,
            0.00059, 0.00031, 0.00059, 0.00059, 0.00031, 0.00059,
            0.00144, 0.00027, 0.00118, 0.00144, 0.00027, 0.00118,])

    mbase_cr = mbf_cr * mbase_all
    mbase_ms = mbf_ms * mbase_all
    mbase_fat = mbf_fat * mbase_all
    mbase_sk = mbf_sk * mbase_all
    return mbase_cr, mbase_ms, mbase_fat, mbase_sk


def local_mwork(bmr, par):
    """
    Calculate local metabolic rate by work [W]  按工作计算局部代谢率

    Parameters
    ----------
    bmr : float, Basal metbolic rate [W].
    par : float, Physical activity ratio [-].

    Returns
    -------
    Mwork : array, Local metabolic rate by work [W].

    """
    mwork_all = (par-1) * bmr
    mwf = np.array([
            0, 0, 0.091, 0.08, 0.129,
            0.0262, 0.0139, 0.005, 0.0262, 0.0139, 0.005,
            0.2010, 0.0990, 0.005, 0.2010, 0.0990, 0.005])
    mwork = mwork_all * mwf
    return mwork


PRE_SHIV = 0
def shivering(err_cr, err_sk, tcr, tsk,
              height=1.62, weight=56, equation="china", age=36, sex="female", dtime=60,
              options={}):
    """
    Calculate local metabolic rate by shivering [W]. 计算颤抖局部代谢率
    
    Parameters
    ----------
    err_cr, err_sk : array, Difference between setpoint and body temperatures [oC].
    tcr, tsk : array, Core and skin temperatures [oC].
    height : float, optional, Body height [m]. The default is 1.72.
    weight : float, optional, Body weight [kg]. The default is 74.43.
    equation : str, optional
        The equation name (str) of bsa calculation. Choose a name from "dubois",
        "takahira", "fujimoto", or "kurazumi". The default is "dubois".
    age : float, optional, Age [years]. The default is 20.
    sex : str, optional, Choose male or female. The default is "male".
    dtime : float, optional, Interval of analysis time. The default is 60.

    Returns
    -------
    Mshiv : array, Local metabolic rate by shivering [W].

    """    
    wrms, clds = error_signals(err_cr, err_sk,)
    shivf = np.array([
            0.0339, 0.0436, 0.27394, 0.24102, 0.38754,
            0.00243, 0.00137, 0.0002, 0.00243, 0.00137, 0.0002,
            0.0039, 0.00175, 0.00035, 0.0039, 0.00175, 0.00035,])
    sig_shiv = 24.36 * clds * (-err_cr[0])
    sig_shiv = max(sig_shiv, 0)

    if options:
        if options["shivering_threshold"]: #起始颤抖阈值检查
            # Asaka, 2016
            # Threshold of starting shivering
            tskm = np.average(tsk, weights=_BSAst) # Mean skin temp.
            if tskm < 31:
                thres = 36.6
            else:
                if sex == "male":
                    thres = -0.2436 * tskm + 44.10
                else: # sex == "female":
                    thres = -0.2250 * tskm + 43.05
            # Second threshold of starting shivering
            if thres < tcr[0]:
                sig_shiv = 0

    global PRE_SHIV  # Previous shivering thermogenesis [W] 颤抖产热，限制颤抖产热速率
    if options:
        if options["limit_dshiv/dt"]:
            # Asaka, 2016
            # dshiv < 0.0077 [W/s]
            dshiv = sig_shiv - PRE_SHIV
            if options["limit_dshiv/dt"] is True: # default is 0.0077 [W/s]
                limit_dshiv = 0.0077 * dtime
            else:
                limit_dshiv = options["limit_dshiv/dt"] * dtime
            if dshiv > limit_dshiv:
                sig_shiv = limit_dshiv + PRE_SHIV
            elif dshiv < -limit_dshiv:
                sig_shiv = -limit_dshiv + PRE_SHIV
        PRE_SHIV = sig_shiv

    # Signal sd_shiv by aging 根据年龄修正颤抖系数
    if age < 30:
        sd_shiv = np.ones(17)
    elif age < 40:
        sd_shiv = np.ones(17) * 0.97514
    elif age < 50:
        sd_shiv = np.ones(17) * 0.95028
    elif age < 60:
        sd_shiv = np.ones(17) * 0.92818
    elif age < 70:
        sd_shiv = np.ones(17) * 0.90055
    elif age < 80:
        sd_shiv = np.ones(17) * 0.86188
    else: #age >= 80
        sd_shiv = np.ones(17) * 0.82597

    bsar = bsa_rate(height, weight, equation)
    mshiv = shivf * bsar * sd_shiv * sig_shiv
    return mshiv

shivering
def nonshivering(err_cr, err_sk,
             height=1.62, weight=56, equation="china", age=36,
             coldacclimation=False, batpositive=True,
             options={},):
    """
    Calculate local metabolic rate by non-shivering [W]

    Parameters
    ----------
    err_cr, err_sk : array, Difference between setpoint and body temperatures [oC].
    height : float, optional, Body height [m]. The default is 1.72.
    weight : float, optional, Body weight [kg]. The default is 74.43.
    equation : str, optional
        The equation name (str) of bsa calculation. Choose a name from "dubois",
        "takahira", "fujimoto", or "kurazumi". The default is "dubois".
    age : float, optional, Age [years]. The default is 20.
    coldacclimation : bool, optional
        Whether the subject acclimates cold enviroment or not. The default is False.
    batpositive : bool, optional
        Whether BAT ativity is positive or not. The default is True.

    Returns
    -------
    Mnst : array
        Local metabolic rate by non-shivering [W].

    """
    # NST (Non-Shivering Thermogenesis) model, Asaka, 2016
    wrms, clds = error_signals(err_cr, err_sk, )

    bmi = weight / height**2

    # BAT: brown adipose tissue [SUV] 棕色脂肪组织
    bat = 10**(-0.10502 * bmi + 2.7708)

    # age factor 根据年龄修正bat
    if age < 30:
        bat *= 1.61
    elif age < 40:
        bat *= 1.00
    else: # age >= 40
        bat *= 0.80

    if coldacclimation:
        bat += 3.46

    if not batpositive:
        # incidence age factor: T.Yoneshiro 2011 
        if age < 30:
            bat *= 44/83
        elif age < 40:
            bat *= 15/38
        elif age < 50:
            bat *= 7/26
        elif age < 50:
            bat *= 1/8
        else: # age > 60
            bat *= 0

    # NST limit
    thres = ((1.80 * bat + 2.43) + 5.62)  # [W]

    sig_nst = 2.8 * clds  # [W]
    sig_nst = min(sig_nst, thres)

    mnstf = np.array([
            0.000, 0.190, 0.000, 0.190, 0.190,
            0.215, 0.000, 0.000, 0.215, 0.000, 0.000,
            0.000, 0.000, 0.000, 0.000, 0.000, 0.000,])
    bsar = bsa_rate(height, weight, equation)
    mnst = bsar * mnstf * sig_nst
    return mnst


def sum_m(mbase, mwork, mshiv, mnst):
    qcr = mbase[0].copy()
    qms = mbase[1].copy()
    qfat = mbase[2].copy()
    qsk = mbase[3].copy()

    for i, bn in enumerate(BODY_NAMES):
        # If the segment has a muscle layer, muscle heat production increases by the activity. 如果该节段有肌肉层，肌肉产热增加。如果该节段有肌肉层，肌肉产热增加。
        if not IDICT[bn]["muscle"] is None:
            qms[i] += mwork[i] + mshiv[i]
        # In other segments, core heat production increase, instead of muscle. 其他层核心产热代替肌肉产热
        else:
            qcr[i] += mwork[i] + mshiv[i]
    qcr += mnst  # Non-shivering thermogenesis occurs in core layers 核心层没有颤抖产热
    return qcr, qms, qfat, qsk


def crmsfat_bloodflow(mwork, mshiv,
        height=1.62, weight=56, equation="china", age=36, ci=2.19,): #计算核心、肌肉和脂肪层的血流速率
    """
    Calculate core, muslce and fat blood flow rate [L/h].

    Parameters
    ----------
    mwork : array, Metablic rate by work [W].
    mshiv : array, Metablic rate by shivering [W].
    height : float, optional, Body height [m]. 
    weight : float, optional, Body weight [kg]. 
    equation : str, optional
        The equation name (str) of bsa calculation. Choose a name from "dubois",
        "china", "fujimoto", or "kurazumi".
    age : float, optional, Age [years]. 
    ci : float, optional, Cardiac index [L/min/㎡]. 

    Returns
    -------
    BFcr, BFms, BFfat : array, Core, muslce and fat blood flow rate [L/h].

    """
    # Basal blood flow rate [L/h]
    # core, CBFB
    bfb_cr = np.array([
            35.251, 15.240, 89.214, 87.663, 18.686,
            1.808, 0.940, 0.217, 1.808, 0.940, 0.217,
            1.406, 0.164, 0.080, 1.406, 0.164, 0.080,])
    # muscle, MSBFB
    bfb_ms = np.array([
            0.682, 0.0, 0.0, 0.0, 12.614,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,])
    # fat, FTBFB
    bfb_fat = np.array([
            0.265, 0.0, 0.0, 0.0, 2.219,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,])

    bfbr = bfb_rate(height, weight, equation, age, ci)
    bf_cr = bfb_cr * bfbr
    bf_ms = bfb_ms * bfbr
    bf_fat = bfb_fat * bfbr

    for i, bn in enumerate(BODY_NAMES):
        # If the segment has a muscle layer, muscle blood flow increases. 如果该节段有肌肉层，肌肉血流增加
        if not IDICT[bn]["muscle"] is None:
            bf_ms[i] += (mwork[i] + mshiv[i])/1.163
        # In other segments, core blood flow increase, instead of muscle blood flow. 在其他部位，核心血流量增加，而不是肌肉血流量增加
        else:
            bf_cr[i] += (mwork[i] + mshiv[i])/1.163
    return bf_cr, bf_ms, bf_fat


def sum_bf(bf_cr, bf_ms, bf_fat, bf_sk, bf_ava_hand, bf_ava_foot):
    co = 0
    co += bf_cr.sum()
    co += bf_ms.sum()
    co += bf_fat.sum()
    co += bf_sk.sum()
    co += 2*bf_ava_hand
    co += 2*bf_ava_foot
    return co


def resp_heatloss(t, p, met):
    res_sh = 0.0014 * met * (34 - t)   #显热
    res_lh = 0.0173 * met * (5.87 - p) #潜热
    return res_sh, res_lh


def get_lts(ta):
    return 2.418*1000

#part 4 params

import textwrap

ALL_OUT_PARAMS = {
    'Age': {'ex_output': True,
         'meaning': 'Age',
         'suffix': None,
         'unit': 'years'},

    'BFava_foot': {'ex_output': True,
                   'meaning': 'AVA blood flow rate of one foot',
                   'suffix': None,
                   'unit': 'L/h'},

    'BFava_hand': {'ex_output': True,
                   'meaning': 'AVA blood flow rate of one hand',
                   'suffix': None,
                   'unit': 'L/h'},

    'BFcr': {'ex_output': True,
             'meaning': 'Core blood flow rate of the body part',
             'suffix': 'Body name',
             'unit': 'L/h'},

    'BFfat': {'ex_output': True,
              'meaning': 'Fat blood flow rate of the body part',
              'suffix': 'Body name',
              'unit': 'L/h'},

    'BFms': {'ex_output': True,
             'meaning': 'Muscle blood flow rate of the body part',
             'suffix': 'Body name',
             'unit': 'L/h'},

    'BFsk': {'ex_output': True,
             'meaning': 'Skin blood flow rate of the body part',
             'suffix': 'Body name',
             'unit': 'L/h'},

    'BSA': {'ex_output': True,
            'meaning': 'Body surface area of the body part',
            'suffix': 'Body name',
            'unit': 'm2'},

    'CO': {'ex_output': False,
           'meaning': 'Cardiac output (the sum of the whole blood flow)',
           'suffix': None,
           'unit': 'L/h'},

    'CycleTime': {'ex_output': False,
                  'meaning': 'The counts of executing one cycle calculation',
                  'suffix': None,
                  'unit': '-'},

    'Emax': {'ex_output': True,
             'meaning': 'Maximum evaporative heat loss at the skin of th body '
                        'part',
             'suffix': 'Body name',
             'unit': 'W'},

    'Esk': {'ex_output': True,
            'meaning': 'Evaporative heat loss at the skin of the body part',
            'suffix': 'Body name',
            'unit': 'W'},

    'Esweat': {'ex_output': True,
               'meaning': 'Evaporative heat loss at the skin by only sweating of '
                          'the body part',
               'suffix': 'Body name',
               'unit': 'W'},

    'Fat': {'ex_output': True,
            'meaning': 'Body fat rate',
            'suffix': None,
            'unit': '%'},

    'Height': {'ex_output': True,
               'meaning': 'Body heigh',
               'suffix': None,
               'unit': 'm'},

    'Icl': {'ex_output': True,
            'meaning': 'Clothing insulation value of the body part',
            'suffix': 'Body name',
            'unit': 'clo'},

    'LHLsk': {'ex_output': True,
              'meaning': 'Latent heat loss at the skin of the body part',
              'suffix': 'Body name',
              'unit': 'W'},

    'Mbasecr': {'ex_output': True,
                'meaning': 'Core heat production by basal metaborism of th body '
                           'part',
                'suffix': 'Body name',
                'unit': 'W'},

    'Mbasefat': {'ex_output': True,
                 'meaning': 'Fat heat production by basal metaborism of th body '
                            'part',
                 'suffix': 'Body name',
                 'unit': 'W'},

    'Mbasems': {'ex_output': True,
                'meaning': 'Muscle heat production by basal metaborism of th body '
                           'part',
                'suffix': 'Body name',
                'unit': 'W'},

    'Mbasesk': {'ex_output': True,
                'meaning': 'Skin heat production by basal metaborism of th body '
                           'part',
                'suffix': 'Body name',
                'unit': 'W'},

    'Met': {'ex_output': False,
            'meaning': 'Total heat production of the whole body',
            'suffix': None,
            'unit': 'W'},

    'Mnst': {'ex_output': True,
             'meaning': 'Core heat production by non-shivering of the body part',
             'suffix': 'Body name',
             'unit': 'W'},

    'ModTime': {'ex_output': False,
                'meaning': 'Simulation times',
                'suffix': None,
                'unit': 'sec'},

    'Mshiv': {'ex_output': True,
              'meaning': 'Core or muscle heat production by shivering of th body '
                         'part',
              'suffix': 'Body name',
              'unit': 'W'},

    'Mwork': {'ex_output': True,
              'meaning': 'Core or muscle heat production by work of the body part',
              'suffix': 'Body name',
              'unit': 'W'},

    'Name': {'ex_output': True,
             'meaning': 'Name of the model',
             'suffix': None,
             'unit': '-'},

    'PAR': {'ex_output': True,
            'meaning': 'Physical activity ratio',
            'suffix': None,
            'unit': '-'},

    'Qcr': {'ex_output': True,
            'meaning': 'Core total heat production of the body part',
            'suffix': 'Body name',
            'unit': 'W'},

    'Qfat': {'ex_output': True,
             'meaning': 'Fat total heat production of the body part',
             'suffix': 'Body name',
             'unit': 'W'},

    'Qms': {'ex_output': True,
            'meaning': 'Muscle total heat production of the body part',
            'suffix': 'Body name',
            'unit': 'W'},

    'Qsk': {'ex_output': True,
            'meaning': 'Skin total heat production of the body part',
            'suffix': 'Body name',
            'unit': 'W'},

    'RES': {'ex_output': False,
            'meaning': 'Heat loss by the respiration',
            'suffix': None,
            'unit': 'W'},

    'RESlh': {'ex_output': True,
              'meaning': 'Latent heat loss by respiration of the body part',
              'suffix': 'Body name',
              'unit': 'W'},
    'RESsh': {'ex_output': True,
              'meaning': 'Sensible heat loss by respiration of the body part',
              'suffix': 'Body name',
              'unit': 'W'},

    'RH': {'ex_output': True,
           'meaning': 'Relative humidity of the body part',
           'suffix': 'Body name',
           'unit': '%'},

    'Ret': {'ex_output': True,
            'meaning': 'Total evaporative heat resistance of the body part',
            'suffix': 'Body name',
            'unit': 'm2.kPa/W'},

    'Rt': {'ex_output': True,
           'meaning': 'Total heat resistance of the body part',
           'suffix': 'Body name',
           'unit': 'm2.K/W'},

    'SHLsk': {'ex_output': True,
              'meaning': 'Sensible heat loss at the skin of the body part',
              'suffix': 'Body name',
              'unit': 'W'},

    'Setptcr': {'ex_output': True,
                'meaning': 'Set point skin temperatre of the body part',
                'suffix': 'Body name',
                'unit': 'oC'},

    'Setptsk': {'ex_output': True,
                'meaning': 'Set point core temperatre of the body part',
                'suffix': 'Body name',
                'unit': 'oC'},

    'Sex': {'ex_output': True,
            'meaning': 'Male or female',
            'suffix': None,
            'unit': '-'},

    'THLsk': {'ex_output': False,
              'meaning': 'Heat loss from the skin of the body part',
              'suffix': 'Body name',
              'unit': 'W'},

    'Ta': {'ex_output': True,
           'meaning': 'Air temperature of the body part',
           'suffix': 'Body name',
           'unit': 'oC'},

    'Tar': {'ex_output': True,
            'meaning': 'Arterial temperature of the body part',
            'suffix': 'Body name',
            'unit': 'oC'},

    'Tcb': {'ex_output': True,
            'meaning': 'Central blood temperature',
            'suffix': None,
            'unit': 'oC'},

    'Tcr': {'ex_output': False,
            'meaning': 'Core temperature of the body part',
            'suffix': 'Body name',
            'unit': 'oC'},

    'Tfat': {'ex_output': True,
             'meaning': 'Fat temperature of the body part',
             'suffix': 'Body name',
             'unit': 'oC'},

    'Tms': {'ex_output': True,
            'meaning': 'Muscle temperature as the body part',
            'suffix': 'Body name',
            'unit': 'oC'},

    'To': {'ex_output': True,
           'meaning': 'Operative temperature of the body part',
           'suffix': 'Body name',
           'unit': 'oC'},

    'Tr': {'ex_output': True,
           'meaning': 'Mean radiant temperature of the body part',
           'suffix': 'Body name',
           'unit': 'oC'},

    'Tsk': {'ex_output': False,
            'meaning': 'Skin temperature of the body part',
            'suffix': 'Body name',
            'unit': 'oC'},

    'TskMean': {'ex_output': False,
                'meaning': 'Mean skin temperature of the body',
                'suffix': None,
                'unit': 'oC'},

    'Tsve': {'ex_output': True,
             'meaning': 'Superfical vein temperature of the body part',
             'suffix': 'Body name',
             'unit': 'oC'},

    'Tve': {'ex_output': True,
            'meaning': 'Vein temperature of the body part',
            'suffix': 'Body name',
            'unit': 'oC'},

    'Va': {'ex_output': True,
           'meaning': 'Air velocity of the body part',
           'suffix': 'Body name',
           'unit': 'm/s'},

    'Weight': {'ex_output': True,
               'meaning': 'Body weight',
               'suffix': None,
               'unit': 'kg'},

    'Wet': {'ex_output': False,
            'meaning': 'Local skin wettedness of the body part',
            'suffix': 'Body name',
            'unit': '-'},

    'WetMean': {'ex_output': False,
                'meaning': 'Mean skin wettedness of the body',
                'suffix': None,
                'unit': '-'},

    'Wle': {'ex_output': False,
            'meaning': 'Weight loss rate by the evaporation and respiration of '
                       'the whole body',
            'suffix': None,
            'unit': 'g/sec'},

    'dt': {'ex_output': False,
        'meaning': 'Time delta of the model',
        'suffix': None,
        'unit': 'sec'}}


def show_outparam_docs():
    """
    Show the documentation of the output parameters.

    Returns
    -------
    docstirng : str
        Text of the documentation of the output parameters

    """


    outparams = textwrap.dedent("""
    Output parameters
    -------
    """)

    exoutparams = textwrap.dedent("""
    Extra output parameters
    -------
    """)

    sortkeys = list(ALL_OUT_PARAMS.keys())
    sortkeys.sort()
    for key in sortkeys:
        value = ALL_OUT_PARAMS[key]

        line = "{}: {} [{}]".format(key.ljust(8), value["meaning"], value["unit"])

        if value["ex_output"]:
            exoutparams += line + "\n"
        else:
            outparams += line + "\n"

    docs = outparams + "\n" + exoutparams
    docs = textwrap.indent(docs.strip(), "    ")

    return docs

#part 5 comfort
import math

def pmv(ta, tr, va, rh, met, clo, wmet=0): #根据PMV公式（Equation 63）计算PMV值。
    """
    Get PMV value based on the 2017 ASHRAE Handbook—Fundamentals, Chapter 9:
    Thermal Comfort, Equations 63 - 68.

    Parameters
    ----------
    ta : float, optional
        Air temperature [oC]
    tr : float, optional
        Mean radiant temperature [oC]
    va : float, optional
        Air velocity [m/s]
    rh : float, optional
        Relative humidity [%]
    met : float, optional
        Metabolic rate [met]
    clo : float, optional
        Clothing insulation [clo]
    wmet : float, optional
        External work [met], optional. The default is 0.

    Returns
    -------
    PMV value
    """

    met *= 58.15     # chage unit [met] to [W/m2]
    wmet *= 58.15    # chage unit [met] to [W/m2]
    mw = met - wmet  # heat production [W/m2] 产热量

    if clo < 0.5: fcl = 1 + 0.2*clo  # clothing area factor [-]
    else: fcl = 1.05 + 0.1*clo

    antoine = lambda x: math.e**(16.6536-(4030.183/(x+235)))   # antoine's formula
    pa = antoine(ta) * rh/100                                  # vapor pressure [kPa]
    rcl = 0.155 * clo                                          # clothing thermal resistance [K.m2/W]
    hcf = 12.1 * va**0.5                                       # forced convective heat transfer coefficience

    hc = hcf             # initial convective heat transfer coefficience
    tcl = (34 + ta) / 2  # initial clothing temp.

    # Cal. clothing temp. by iterative calculation method
    for i in range(100):
        # clothing temp. [oC]
        tcliter = 35.7 - 0.028 * mw \
            - rcl * (39.6 * 10**(-9) * fcl * ((tcl+273)**4 - (tr+273)**4) \
                     + fcl * hc * (tcl - ta))  # Eq.68
        # new clothin temp. [oC] 服装温度
        tcl = (tcliter + tcl) / 2

        hcn = 2.38 * abs(tcl - ta)**0.25  # natural convective heat transfer coefficience 自然对流换热系数

        # select forced or natural convection 强制对流与自然对流
        if  hcn > hcf: hc = hcf
        else: hc = hcf

        # terminate iterative calculation
        if abs(tcliter - tcl) < 0.0001:
            break

    # tcl = 35.7 - 0.0275 * mw \
    #     - rcl * (mw - 3.05 * (5.73 - 0.007 * mw - pa) \
    #     - 0.42 * (mw - 58.15) - 0.0173 * met * (5.87 - pa) \
    #     + 0.0014 * met * (34 - ta))  # Eq.64

    # Heat loss of human body 热损失
    rad = 3.96 * (10**(-8)) * fcl * ((tcl+273)**4 - (tr+273)**4)  # by radiation 辐射
    conv = fcl * hc * (tcl - ta)                                  # by convction 对流
    diff = 3.05 * (5.73 - 0.007 * mw - pa)                        # by insensive perspiration 血管扩散
    sweat = max(0, 0.42 * (mw - 58.15))                           # by sweating 出汗
    res = 0.0173 * met * (5.87 - pa) + 0.0014 * met * (34 - ta)   # by repiration 呼吸
    load = mw - rad - conv - diff - sweat - res

    pmv_value = (0.303 * math.exp(-0.036 * met) + 0.028) * load  # Eq.63

    return pmv_value

def preferred_temp(va=0.1, rh=50, met=1, clo=0):
    """
    Calculate operative temperature [oC] at PMV=0. 计算PMV=0时的操作温度

    Parameters
    ----------
    va : float, optional
        Air velocity [m/s]. The default is 0.1.
    rh : float, optional
        Relative humidity [%]. The default is 50.
    met : float, optional
        Metabolic rate [met]. The default is 1.
    clo : float, optional
        Clothing insulation [clo]. The default is 0.

    Returns
    -------
    to : float
        Operative temperature [oC].
    """

    to = 28 # initial temp 初始温度
    for i in range(100):
        vpmv = pmv(to, to, va, rh, met, clo)
        if abs(vpmv) < 0.001: break
        else: to = to - vpmv/3
    return to

#part 6 jos-3

import csv
import datetime as dt
import os

class JOS3():
    """
        Parameters
    -------
    height : float, optional
        Body height [m]. The default is 1.72.
    weight : float, optional
        Body weight [kg]. The default is 74.43.
    fat : float, optional
        Fat rte [%]. The default is 15.
    age : int, optional
        Age [years]. The default is 20.
    sex : str, optional
        Sex ("male" or "female"). The default is "male".
    ci : float, optional
        Cardiac index [L/min/m2]. The default is 2.6432.心指数
    bmr_equation : str, optional
        Choose a BMR equation. The default is "harris-benedict".
    bsa_equation : str, optional
        Choose a BSA equation.
        You can choose
        The default is "dubois".
    ex_output : None, list or "all", optional
        If you want to get extra output parameters, set the parameters as the list format.
        If ex_output is "all", all parameters are output.
        The default is None.


    Setter & Getter
    -------
    Input parameters of environmental conditions are set as the Setter format.
    If you set the different conditons in each body parts, set the list.
    List input must be 17 lengths and means the input of "Head", "Neck", "Chest",
    "Back", "Pelvis", "LShoulder", "LArm", "LHand", "RShoulder", "RArm",
    "RHand", "LThigh", "LLeg", "LFoot", "RThigh", "RLeg" and "RFoot".

    Ta : float or list
        Air temperature [oC].
    Tr : float or list
        Mean radiant temperature [oC].
    To : float or list
        Operative temperature [oC].
    Va : float or list
        Air velocity [m/s].
    RH : float or list
        Relative humidity [%].
    Icl : float or list
        Clothing insulation [clo].
    PAR : float
        Physical activity ratio [-].
        This equals the ratio of metaboric rate to basal metablic rate.
        PAR of sitting quietly is 1.2.
    posture : str
        Choose a posture from standing, sitting or lying.
    bodytemp : numpy.ndarray (85,)
        All segment temperatures of JOS-3

    Getter
    -------
    JOS3 has some useful getters to check the current parameters.

    BSA : numpy.ndarray (17,)
        Body surface areas by local body segments [m2].
    Rt : numpy.ndarray (17,)
        Dry heat resistances between the skin and ambience areas by local body segments [K.m2/W].
    Ret : numpy.ndarray (17,)
        Wet (Evaporative) heat resistances between the skin and ambience areas by local body segments [Pa.m2/W].
    Wet : numpy.ndarray (17,)
        Skin wettedness on local body segments [-].
    WetMean : float
        Mean skin wettedness of the whole body [-].
    TskMean : float
        Mean skin temperature of the whole body [oC].
    Tsk : numpy.ndarray (17,)
        Skin temperatures by the local body segments [oC].
    Tcr : numpy.ndarray (17,)
        Skin temperatures by the local body segments [oC].
    Tcb : numpy.ndarray (1,)
        Core temperatures by the local body segments [oC].
    Tar : numpy.ndarray (17,)
        Arterial temperatures by the local body segments [oC].
    Tve : numpy.ndarray (17,)
        Vein temperatures by the local body segments [oC].
    Tsve : numpy.ndarray (12,)
        Superfical vein temperatures by the local body segments [oC].
    Tms : numpy.ndarray (2,)
        Muscle temperatures of Head and Pelvis [oC].
    Tfat : numpy.ndarray (2,)
        Fat temperatures of Head and Pelvis  [oC].
    BMR : float
        Basal metabolic rate [W/m2].
    """

    def __init__(
            self,
            height=1.62,  #身高
            weight=56,    #体重
            fat=33,       #脂肪率 体脂百分比 = 1.2 × BMI + 0.23 × 年龄 - 5.4 - 10.8 × 性别（男为1，女为0）
            age=36,       #年龄
            sex="female", #性别
            ci=2.19,      #心指数
            bmr_equation="Chinese",  #代谢率公式
            bsa_equation="china",    #体表面积公式
            ex_output=None,
            ):

        self._height = height
        self._weight = weight
        self._fat = fat
        self._sex = sex
        self._age = age
        self._ci = ci
        self._bmr_equation = bmr_equation
        self._bsa_equation = bsa_equation
        self._ex_output = ex_output

        # Body surface area [m2] 皮肤表面积
        self._bsa_rate = bsa_rate(height, weight, bsa_equation,)
        # Body surface area rate [-] 身体表面积比例
        self._bsa = localbsa(height, weight, bsa_equation,)
        # Basal blood flow rate [-] 基础血流量
        self._bfb_rate = bfb_rate(height, weight, bsa_equation, age, ci)
        # Thermal conductance [W/K] 导热系数
        self._cdt = conductance(height, weight, bsa_equation, fat,)
        # Thermal capacity [J/K] 热容量
        self._cap = capacity(height, weight, bsa_equation, age, ci)

        # Set point temp [oC]
        self.setpt_cr = np.ones(17)*37  # core核心温度
        self.setpt_sk = np.ones(17)*34  # skin皮肤温度

        # Initial body temp [oC] 初始体温
        self._bodytemp = np.ones(NUM_NODES) * 36

        # Default values of input condition 输入条件的默认值
        self._ta = np.ones(17)*26    #空气温度17个节点都为26
        self._tr = np.ones(17)*26    #平均辐射温度
        self._rh = np.ones(17)*75    #相对湿度
        self._va = np.ones(17)*0.05  #空气流速
        self._clo = np.ones(17)*0.5 #服装热阻 夏季0.5 clo； 冬季1.01 clo
        self._iclo = np.ones(17) * 0.45 #蒸汽渗透效率
        self._par = 1.8 # Physical activity ratio 体力活动比率：代谢率与基础代谢率之比，ASHRAE 55-2017中得Table 5.2.1.2可知，做饭为1.6-2.0met
        self._posture = "standing"  #姿势
        self._hc = None             #对流换热系数，None 起到了一个占位符的作用，表示这些值在初始化时是未知的，将在后续的使用中得到赋值。
        self._hr = None             #辐射换热系数，同上
        self.ex_q = np.zeros(NUM_NODES)  #外部热量
        self._t = dt.timedelta(0)   # Elapsed time 经过的时间
        self._cycle = 0             # Cycle time 循环时间
        self.model_name = "JOS3"
        self.options = {
                "nonshivering_thermogenesis": True, #考虑非颤抖引起的产热，初始只考虑这项
                "cold_acclimated": False,           #表示考虑冷暴露
                "shivering_threshold": False,       #考虑颤抖引起的产热
                "limit_dshiv/dt": False,            #限制颤抖产热速率
                "bat_positive": False,              #表示考虑棕色脂肪
                "ava_zero": False,                  #将手脚动脉血流的计算结果 bf_ava_hand 和 bf_ava_foot 设为 0
                "shivering": False,}
        PRE_SHIV = 0 # reset
        self._history = []
        self._t = dt.timedelta(0) # Elapsed time
        self._cycle = 0 # Cycle time

        # Reset setpoint temperature
        dictout = self._reset_setpt()
        self._history.append(dictout)  # Save the last model parameters


    def _reset_setpt(self):
        """
        Reset setpoint temperature by steady state calculation.
        Be careful, input parameters (Ta, Tr, RH, Va, Icl, PAR) and body
        tempertures are also resetted.
        通过稳态计算重置设定点温度。小心，输入参数（Ta、Tr、RH、Va、Icl、PAR）和身体温度也会重新设定。

        Returns
        -------
        Parameters of JOS-3 : dict
        """
        # Set operative temperature under PMV=0 environment 设置pmv=0环境下的操作温度
        # PAR = 1.8 取做饭1.6-2.0平均值
        # 1 met = 58.15 W/m2
        met = self.BMR * 1.25 / 58.15  # [met]
        self.To = preferred_temp(met=met)
        self.RH = 50
        self.Va = 0.1
        self.Icl = 0
        self.PAR = 1.8

        # Steady-calculation 稳态计算
        self.options["ava_zero"] = True
        for t in range(10):
            dictout = self._run(dtime=60000, passive=True)

        # Set new setpoint temperatures 设置新的设定点温度
        self.setpt_cr = self.Tcr
        self.setpt_sk = self.Tsk
        self.options["ava_zero"] = False

        return dictout


    def simulate(self, times, dtime=60, output=True):
        """
        Execute JOS-3 model. 运行JOS-3模型。

        Parameters
        ----------
        times : int
            Number of loops of a simulation 模拟的循环数
        dtime : int or float, optional
            Time delta [sec]. The default is 60.
        output : bool, optional
            If you don't record paramters, set False. The default is True.

        Returns
        -------
        None.

        """
        for t in range(times):
            self._t += dt.timedelta(0, dtime)
            self._cycle += 1
            dictdata = self._run(dtime=dtime, output=output)
            if output:
                # self.history.append(dictdata)
                self._history.append(dictdata)


    def _run(self, dtime=60, passive=False, output=True):
        """
        Run a model for a once and get model parameters. 运行一次模型并获取模型参数

        Parameters
        ----------
        dtime : int or float, optional
            Time delta [sec]. The default is 60.
        passive : bool, optional
            If you run a passive model, set True. The default is False.
        output : bool, optional
            If you don't need paramters, set False. The default is True.

        Returns
        -------
        dictout : dictionary
            Output parameters.

        """
        tcr = self.Tcr
        tsk = self.Tsk

        # Convective and radiative heat transfer coefficient [W/K.m2] 对流和辐射传热系数
        hc = fixed_hc(conv_coef(self._posture, self._va, self._ta, tsk,), self._va)
        hr = fixed_hr(rad_coef(self._posture,))
        # Manual setting
        if self._hc is not None:
            hc = self._hc
        if self._hr is not None:
            hr = self._hr

        # Operarive temp. [oC], heat and evaporative heat resistance [m2.K/W], [m2.kPa/W]
        to = operative_temp(self._ta, self._tr, hc, hr,) #操作温度
        r_t = dry_r(hc, hr, self._clo)                   #热阻
        r_et = wet_r(hc, self._clo, self._iclo)          #蒸发热阻

        #------------------------------------------------------------------
        # Thermoregulation 温度调节
        #------------------------------------------------------------------
        # Setpoint temperature of thermoregulation 温度调节设定点温度
        if passive:
            setpt_cr = tcr.copy()
            setpt_sk = tsk.copy()
        else:
            setpt_cr = self.setpt_cr.copy()
            setpt_sk = self.setpt_sk.copy()
        # Difference between setpoint and body temperatures 设定点和身体温度之间的差异
        err_cr = tcr - setpt_cr
        err_sk = tsk - setpt_sk

        # Skinwettedness [-], Esk, Emax, Esw [W] 皮肤湿润
        wet, e_sk, e_max, e_sweat = evaporation(
                err_cr, err_sk, tsk,
                self._ta, self._rh, r_et,
                self._height, self._weight, self._bsa_equation, self._age)

        # Skin blood flow, basal skin blood flow [L/h] 皮肤血流量
        bf_sk = skin_bloodflow(err_cr, err_sk,
            self._height, self._weight, self._bsa_equation, self._age, self._ci)

        # Hand, Foot AVA blood flow [L/h] 手脚动脉血流
        bf_ava_hand, bf_ava_foot = ava_bloodflow(err_cr, err_sk,
            self._height, self._weight, self._bsa_equation, self._age, self._ci)
        if self.options["ava_zero"] and passive:
            bf_ava_hand = 0
            bf_ava_foot = 0

        # Thermogenesis by shivering [W] 颤抖
        mshiv = shivering(
                err_cr, err_sk, tcr, tsk,
                self._height, self._weight, self._bsa_equation, self._age, self._sex, dtime,
                self.options,)

        # Thermogenesis by non-shivering [W] 不颤抖
        if self.options["nonshivering_thermogenesis"]:
            mnst = nonshivering(err_cr, err_sk,
                self._height, self._weight, self._bsa_equation, self._age,
                self.options["cold_acclimated"], self.options["bat_positive"])
        else: # not consider NST
            mnst = np.zeros(17)

        #------------------------------------------------------------------
        # Thermogenesis 产热过程
        #------------------------------------------------------------------
        # Basal thermogenesis [W] 基础产热
        mbase = local_mbase(
                self._height, self._weight, self._age, self._sex,
                self._bmr_equation,)
        mbase_all = sum([m.sum() for m in mbase])

        # Thermogenesis by work [W] 工作产热
        mwork = local_mwork(mbase_all, self._par)

        # Sum of thermogenesis in core, muscle, fat, skin [W] 各个部位总产热
        qcr, qms, qfat, qsk = sum_m(mbase, mwork, mshiv, mnst,)
        qall = qcr.sum() + qms.sum() + qfat.sum() + qsk.sum()

        #------------------------------------------------------------------
        # Other
        #------------------------------------------------------------------
        # Blood flow in core, muscle, fat [L/h] 核心、肌肉、脂肪层的血流量
        bf_cr, bf_ms, bf_fat = crmsfat_bloodflow(mwork, mshiv,
            self._height, self._weight, self._bsa_equation, self._age, self._ci)

        # Heat loss by respiratory 呼吸热损失
        p_a = antoine(self._ta)*self._rh/100
        res_sh, res_lh = resp_heatloss(self._ta[0], p_a[0], qall)

        # Sensible heat loss [W] 显热损失
        shlsk = (tsk - to) / r_t * self._bsa

        # Cardiac output [L/h] 心输出量
        co = sum_bf(
                bf_cr, bf_ms, bf_fat, bf_sk, bf_ava_hand, bf_ava_foot)

        # Weight loss rate by evaporation [g/sec] 蒸发失重率
        wlesk = (e_sweat + 0.06*e_max) / 2418
        wleres = res_lh / 2418

        #------------------------------------------------------------------
        # Matrix 矩阵
        #------------------------------------------------------------------
        # Matrix A
        # (83, 83,) ndarray
        bf_art, bf_vein = vessel_bloodflow(
                bf_cr, bf_ms, bf_fat, bf_sk, bf_ava_hand, bf_ava_foot
                )
        bf_local = localarr(
                bf_cr, bf_ms, bf_fat, bf_sk, bf_ava_hand, bf_ava_foot
                )
        bf_whole = wholebody(
                bf_art, bf_vein, bf_ava_hand, bf_ava_foot
                )
        arr_bf = np.zeros((NUM_NODES,NUM_NODES))
        arr_bf += bf_local
        arr_bf += bf_whole

        arr_bf /= self._cap.reshape((NUM_NODES,1)) # Change unit [W/K] to [/sec] 换单位
        arr_bf *= dtime                            # Change unit [/sec] to [-]

        arr_cdt = self._cdt.copy()
        arr_cdt /= self._cap.reshape((NUM_NODES,1)) # Change unit [W/K] to [/sec]
        arr_cdt *= dtime                            # Change unit [/sec] to [-]

        arrB = np.zeros(NUM_NODES)
        arrB[INDEX["skin"]] += 1/r_t*self._bsa
        arrB /= self._cap  # Change unit [W/K] to [/sec]
        arrB *= dtime      # Change unit [/sec] to [-]

        arrA_tria = -(arr_cdt + arr_bf)

        arrA_dia = arr_cdt + arr_bf
        arrA_dia = arrA_dia.sum(axis=1) + arrB
        arrA_dia = np.diag(arrA_dia)
        arrA_dia += np.eye(NUM_NODES)

        arrA = arrA_tria + arrA_dia
        arrA_inv = np.linalg.inv(arrA)

        # Matrix Q [W] / [J/K] * [sec] = [-]
        # Thermogensis
        arrQ = np.zeros(NUM_NODES)
        arrQ[INDEX["core"]] += qcr
        arrQ[INDEX["muscle"]] += qms[VINDEX["muscle"]]
        arrQ[INDEX["fat"]] += qfat[VINDEX["fat"]]
        arrQ[INDEX["skin"]] += qsk

        # Respiratory [W] 呼吸
        arrQ[INDEX["core"][2]] -= res_sh + res_lh #Chest core 胸部核心负责呼吸换热

        # Sweating [W] 出汗
        arrQ[INDEX["skin"]] -= e_sk 

        # Extra heat gain [W] 额外得热
        arrQ += self.ex_q.copy()

        arrQ /= self._cap  # Change unit [W]/[J/K] to [K/sec]
        arrQ *= dtime      # Change unit [K/sec] to [K]

        # Boundary matrix [℃] 边界矩阵
        arr_to = np.zeros(NUM_NODES)
        arr_to[INDEX["skin"]] += to

        # all
        arr = self._bodytemp + arrB * arr_to + arrQ

        #------------------------------------------------------------------
        # New body temp. [oC]
        #------------------------------------------------------------------
        self._bodytemp = np.dot(arrA_inv, arr)

        #------------------------------------------------------------------
        # Output paramters
        #------------------------------------------------------------------
        dictout = {}
        if output:  # Default output
            dictout["CycleTime"] = self._cycle
            dictout["ModTime"] = self._t
            dictout["dt"] = dtime
            dictout["TskMean"] = self.TskMean
            dictout["Tsk"] = self.Tsk
            dictout["Tcr"] = self.Tcr
            dictout["WetMean"] = np.average(wet, weights=_BSAst)
            dictout["Wet"] = wet
            dictout["Wle"] = (wlesk.sum() + wleres)
            dictout["CO"] = co
            dictout["Met"] = qall
            dictout["RES"] = res_sh + res_lh
            dictout["THLsk"] = shlsk + e_sk


        detailout = {}
        if self._ex_output and output:
            detailout["Name"] = self.model_name
            detailout["Height"] = self._height
            detailout["Weight"] = self._weight
            detailout["BSA"] = self._bsa
            detailout["Fat"] = self._fat
            detailout["Sex"] = self._sex
            detailout["Age"] = self._age
            detailout["Setptcr"] = setpt_cr
            detailout["Setptsk"] = setpt_sk
            detailout["Tcb"] = self.Tcb
            detailout["Tar"] = self.Tar
            detailout["Tve"] = self.Tve
            detailout["Tsve"] = self.Tsve
            detailout["Tms"] = self.Tms
            detailout["Tfat"] = self.Tfat
            detailout["To"] = to
            detailout["Rt"] = r_t
            detailout["Ret"] = r_et
            detailout["Ta"] = self._ta.copy()
            detailout["Tr"] = self._tr.copy()
            detailout["RH"] = self._rh.copy()
            detailout["Va"] = self._va.copy()
            detailout["PAR"] = self._par
            detailout["Icl"] = self._clo.copy()
            detailout["Esk"] = e_sk
            detailout["Emax"] = e_max
            detailout["Esweat"] = e_sweat
            detailout["BFcr"] = bf_cr
            detailout["BFms"] = bf_ms[VINDEX["muscle"]]
            detailout["BFfat"] = bf_fat[VINDEX["fat"]]
            detailout["BFsk"] = bf_sk
            detailout["BFava_hand"] = bf_ava_hand
            detailout["BFava_foot"] = bf_ava_foot
            detailout["Mbasecr"] = mbase[0]
            detailout["Mbasems"] = mbase[1][VINDEX["muscle"]]
            detailout["Mbasefat"] = mbase[2][VINDEX["fat"]]
            detailout["Mbasesk"] = mbase[3]
            detailout["Mwork"] = mwork
            detailout["Mshiv"] = mshiv
            detailout["Mnst"] = mnst
            detailout["Qcr"] = qcr
            detailout["Qms"] = qms[VINDEX["muscle"]]
            detailout["Qfat"] = qfat[VINDEX["fat"]]
            detailout["Qsk"] = qsk
            dictout["SHLsk"] = shlsk
            dictout["LHLsk"] = e_sk
            dictout["RESsh"] = res_sh
            dictout["RESlh"] = res_lh


        if self._ex_output == "all":
            dictout.update(detailout)
        elif isinstance(self._ex_output, list):  # if ex_out type is list
            outkeys = detailout.keys()
            for key in self._ex_output:
                if key in outkeys:
                    dictout[key] = detailout[key]
        return dictout


    def dict_results(self):
        """
        Get results as pandas.DataFrame format.

        Returns
        -------
        Dictionaly of the results
        """
        if not self._history:
            print("The model has no data.")
            return None

        def check_word_contain(word, *args):
            """
            Check if word contains *args.
            """
            boolfilter = False
            for arg in args:
                if arg in word:
                    boolfilter = True
            return boolfilter

        # Set column titles
        # If the values are iter, add the body names as suffix words.
        # If the values are not iter and the single value data, convert it to iter.
        key2keys = {}  # Column keys
        for key, value in self._history[0].items():
            try:
                length = len(value)
                if isinstance(value, str):
                    keys = [key]  # str is iter. Convert to list without suffix
                elif check_word_contain(key, "sve", "sfv", "superficialvein"):
                    keys = [key+BODY_NAMES[i] for i in VINDEX["sfvein"]]
                elif check_word_contain(key, "ms", "muscle"):
                    keys = [key+BODY_NAMES[i] for i in VINDEX["muscle"]]
                elif check_word_contain(key, "fat"):
                    keys = [key+BODY_NAMES[i] for i in VINDEX["fat"]]
                elif length == 17:  # if data contains 17 values
                    keys = [key+bn for bn in BODY_NAMES]
                else:
                    keys = [key+BODY_NAMES[i] for i in range(length)]
            except TypeError:  # if the value is not iter.
                keys= [key]  # convert to iter
            key2keys.update({key: keys})

        data = []
        for i, dictout in enumerate(self._history):
            row = {}
            for key, value in dictout.items():
                keys = key2keys[key]
                if len(keys) == 1:
                    values = [value]  # make list if value is not iter
                else:
                    values = value
                row.update(dict(zip(keys, values)))
            data.append(row)

        outdict = dict(zip(data[0].keys(), [[] for i in range(len(data[0].keys()))]))
        for row in data:
            for k in data[0].keys():
                outdict[k].append(row[k])
        return outdict


    def to_csv(self, path=None, folder=None, unit=True, meanig=True):
        """
        Export results as csv format.

        Parameters
        ----------
        path : str, optional
            Output path. If you don't use the default file name, set a name.
            The default is None.
        folder : str, optional
            Output folder. If you use the default file name with the current time,
            set a only folder path.
            The default is None.
        unit : bool, optional
            Write units in csv file. The default is True.
        meaning : bool, optional
            Write meanings of the parameters in csv file. The default is True.
     
        """

        if path is None:
            nowtime = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            path = "{}_{}.csv".format(self.model_name, nowtime)
            if folder:
                os.makedirs(folder, exist_ok=True)
                path = folder + os.sep + path
        elif not ((path[-4:] == ".csv") or (path[-4:] == ".txt")):
            path += ".csv"
        dictout = self.dict_results()

        columns = [k for k in dictout.keys()]
        units = []
        meanigs = []
        for col in columns:
            param, rbn = remove_bodyname(col)
            if param in ALL_OUT_PARAMS:
                u = ALL_OUT_PARAMS[param]["unit"]
                units.append(u)

                m = ALL_OUT_PARAMS[param]["meaning"]
                if rbn:
                    meanigs.append(m.replace("body part", rbn))
                else:
                    meanigs.append(m)
            else:
                units.append("")
                meanigs.append("")

        with open(path, "wt", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(list(columns))
            if unit: writer.writerow(units)
            if meanig: writer.writerow(meanigs)
            for i in range(len(dictout["CycleTime"])):
                row = []
                for k in columns:
                    row.append(dictout[k][i])
                writer.writerow(row)


    #--------------------------------------------------------------------------
    # Setter
    #--------------------------------------------------------------------------
    def _set_ex_q(self, tissue, value):
        """
        Set extra heat gain by tissue name.

        Parameters
        ----------
        tissue : str
            Tissue name. "core", "skin", or "artery".... If you set value to
            Head muscle and other segment's core, set "all_muscle".
        value : int, float, array
            Heat gain [W]

        Returns
        -------
        array
            Extra heat gain of model.
        """
        self.ex_q[INDEX[tissue]] = value
        return self.ex_q


    #--------------------------------------------------------------------------
    # Setter & getter
    #--------------------------------------------------------------------------

    @property
    def Ta(self):
        """
        Getter

        Returns
        -------
        Ta : numpy.ndarray (17,)
            Air temperature [oC].
        """
        return self._ta
    @Ta.setter
    def Ta(self, inp):
        self._ta = _to17array(inp)

    @property
    def Tr(self):
        """
        Getter

        Returns
        -------
        Tr : numpy.ndarray (17,)
            Mean radiant temperature [oC].
        """
        return self._tr
    @Tr.setter
    def Tr(self, inp):
        self._tr = _to17array(inp)

    @property
    def To(self):
        """
        Getter

        Returns
        -------
        To : numpy.ndarray (17,)
            Operative temperature [oC].
        """
        hc = fixed_hc(conv_coef(self._posture, self._va, self._ta, self.Tsk,), self._va)
        hr = fixed_hr(rad_coef(self._posture,))
        to = operative_temp(self._ta, self._tr, hc, hr,)
        return to
    @To.setter
    def To(self, inp):
        self._ta = _to17array(inp)
        self._tr = _to17array(inp)

    @property
    def RH(self):
        """
        Getter

        Returns
        -------
        RH : numpy.ndarray (17,)
            Relative humidity [%].
        """
        return self._rh
    @RH.setter
    def RH(self, inp):
        self._rh = _to17array(inp)

    @property
    def Va(self):
        """
        Getter

        Returns
        -------
        Va : numpy.ndarray (17,)
            Air velocity [m/s].
        """
        return self._va
    @Va.setter
    def Va(self, inp):
        self._va = _to17array(inp)

    @property
    def posture(self):
        """
        Getter

        Returns
        -------
        posture : str
            Current JOS3 posture.
        """
        return self._posture
    @posture.setter
    def posture(self, inp):
        if inp == 0:
            self._posture = "standing"
        elif inp == 1:
            self._posture = "sitting"
        elif inp == 2:
            self._posture = "lying"
        elif type(inp) == str:
            if inp.lower() == "standing":
                self._posture = "standing"
            elif inp.lower() in ["sitting", "sedentary"]:
                self._posture = "sitting"
            elif inp.lower() in ["lying", "supine"]:
                self._posture = "lying"
        else:
            self._posture = "standing"
            print('posture must be 0="standing", 1="sitting" or 2="lying".')
            print('posture was set "standing".')

    @property
    def Icl(self):
        """
        Getter

        Returns
        -------
        Icl : numpy.ndarray (17,)
            Clothing insulation [clo].
        """
        return self._clo
    @Icl.setter
    def Icl(self, inp):
        self._clo = _to17array(inp)

    @property
    def PAR(self):
        """
        Getter

        Returns
        -------
        PAR : float
            Physical activity ratio [-].
            This equals the ratio of metaboric rate to basal metablic rate.
            PAR of sitting quietly is 1.2.
        """
        return self._par
    @PAR.setter
    def PAR(self, inp):
        self._par = inp

    @property
    def bodytemp(self):
        """
        Getter

        Returns
        -------
        bodytemp : numpy.ndarray (85,)
            All segment temperatures of JOS-3
        """
        return self._bodytemp
    @bodytemp.setter
    def bodytemp(self, inp):
        self._bodytemp = inp.copy()

    #--------------------------------------------------------------------------
    # Getter
    #--------------------------------------------------------------------------

    @property
    def BSA(self):
        """
        Getter

        Returns
        -------
        BSA : numpy.ndarray (17,)
            Body surface areas by local body segments [m2].
        """
        return self._bsa.copy()

    @property
    def Rt(self):
        """
        Getter

        Returns
        -------
        Rt : numpy.ndarray (17,)
            Dry heat resistances between the skin and ambience areas by local body segments [K.m2/W].
        """
        hc = fixed_hc(conv_coef(self._posture, self._va, self._ta, self.Tsk,), self._va)
        hr = fixed_hr(rad_coef(self._posture,))
        return dry_r(hc, hr, self._clo)

    @property
    def Ret(self):
        """
        Getter

        Returns
        -------
        Ret : numpy.ndarray (17,)
            Wet (Evaporative) heat resistances between the skin and ambience areas by local body segments [Pa.m2/W].
        """
        hc = fixed_hc(conv_coef(self._posture, self._va, self._ta, self.Tsk,), self._va)
        return wet_r(hc, self._clo, self._iclo)

    @property
    def Wet(self):
        """
        Getter

        Returns
        -------
        Wet : numpy.ndarray (17,)
            Skin wettedness on local body segments [-].
        """
        err_cr = self.Tcr - self.setpt_cr
        err_sk = self.Tsk - self.setpt_sk
        wet, *_ = evaporation(err_cr, err_sk,
                self._ta, self._rh, self.Ret, self._bsa_rate, self._age)
        return wet

    @property
    def WetMean(self):
        """
        Getter

        Returns
        -------
        WetMean : float
            Mean skin wettedness of the whole body [-].
        """
        wet = self.Wet
        return np.average(wet, weights=_BSAst)



    @property
    def TskMean(self):
        """
        Getter

        Returns
        -------
        TskMean : float
            Mean skin temperature of the whole body [oC].
        """
        return np.average(self._bodytemp[INDEX["skin"]], weights=_BSAst)

    @property
    def Tsk(self):
        """
        Getter

        Returns
        -------
        Tsk : numpy.ndarray (17,)
            Skin temperatures by the local body segments [oC].
        """
        return self._bodytemp[INDEX["skin"]].copy()

    @property
    def Tcr(self):
        """
        Getter

        Returns
        -------
        Tcr : numpy.ndarray (17,)
            Skin temperatures by the local body segments [oC].
        """
        return self._bodytemp[INDEX["core"]].copy()

    @property
    def Tcb(self):
        """
        Getter

        Returns
        -------
        Tcb : numpy.ndarray (1,)
            Core temperatures by the local body segments [oC].
        """
        return self._bodytemp[0].copy()

    @property
    def Tar(self):
        """
        Getter

        Returns
        -------
        Tar : numpy.ndarray (17,)
            Arterial temperatures by the local body segments [oC].
        """
        return self._bodytemp[INDEX["artery"]].copy()

    @property
    def Tve(self):
        """
        Getter

        Returns
        -------
        Tve : numpy.ndarray (17,)
            Vein temperatures by the local body segments [oC].
        """
        return self._bodytemp[INDEX["vein"]].copy()

    @property
    def Tsve(self):
        """
        Getter

        Returns
        -------
        Tsve : numpy.ndarray (12,)
            Superfical vein temperatures by the local body segments [oC].
        """
        return self._bodytemp[INDEX["sfvein"]].copy()

    @property
    def Tms(self):
        """
        Getter

        Returns
        -------
        Tms : numpy.ndarray (2,)
            Muscle temperatures of Head and Pelvis [oC].
        """
        return self._bodytemp[INDEX["muscle"]].copy()

    @property
    def Tfat(self):
        """
        Getter

        Returns
        -------
        Tfat : numpy.ndarray (2,)
            Fat temperatures of Head and Pelvis  [oC].
        """
        return self._bodytemp[INDEX["fat"]].copy()

    @property
    def bodyname(self):
        """
        Getter

        Returns
        -------
        bodyname : list
            JOS3 body names,
            "Head", "Neck", "Chest", "Back", "Pelvis",
            "LShoulder", "LArm", "LHand",
            "RShoulder", "RArm", "RHand",
            "LThigh", "LLeg", "LHand",
            "RThigh", "RLeg" and "RHand".
        """
        body = [
                "Head", "Neck", "Chest", "Back", "Pelvis",
                "LShoulder", "LArm", "LHand",
                "RShoulder", "RArm", "RHand",
                "LThigh", "LLeg", "LHand",
                "RThigh", "RLeg", "RHand",]
        return body

    @property
    def results(self):
        return self.dict_results()

    @property
    def BMR(self):
        """
        Getter

        Returns
        -------
        BMR : float
            Basal metabolic rate [W/m2].
        """
        bmr = basal_met(
                self._height, self._weight, self._age,
                self._sex, self._bmr_equation,)
        return bmr / self.BSA.sum()


def _to17array(inp):
    """
    Make ndarray (17,).

    Parameters
    ----------
    inp : int, float, ndarray, list
        Number you make as 17array.

    Returns
    -------
    ndarray
    """
    try:
        if len(inp) == 17:
            array = np.array(inp)
        else:
            first_item = inp[0]
            array = np.ones(17)*first_item
    except:
        array = np.ones(17)*inp
    return array.copy()

#Make a model:

#人体参数调整
model = JOS3(
    height=1.62,  #根据调查问卷
    weight=56,    #根据调查问卷
    age=36,       #根据调查问卷
    sex="female", #根据调查问卷
    fat=33,                 #修正：体脂百分比 = 1.2 × BMI + 0.23 × 年龄 - 5.4 - 10.8 × 性别（男为1，女为0）
    bmr_equation="Chinese", #修正： LIU 方程：BMR = 13.88  weight + 416  height - 3.43  age- 112.40  sex (men = 0; women = 1) +54.34
    bsa_equation="china",   #修正：中国女性：BSA = 0.586 × height + 0.0126 × weight−0.0461；中国男性：BSA = 0.586 × height + 0.0126 × weight−0.0698
    ci=2.19,                #修正：CI = CO / BSA =  (0.024 × weight - 0.057 × age - 0.305 × sex + 4.544)/(0.586 × height + 0.0126 × weight-0.0461)
    ex_output="all",
)

#Set the first phase:

model.To = [12.7,18.4,18.8,15.2,23,
            13.3,19.1,14.9,
            14.7,15.5,16.1,
            17.9,15.9,15.8,
            20.8,21.2,21.9]    # Operative temperature [oC] 操作温度

''' 
"Head", "Neck", "Chest", "Back", "Pelvis",
    "LShoulder", "LArm", "LHand",
    "RShoulder", "RArm", "RHand",
    "LThigh", "LLeg", "LFoot",
    "RThigh", "RLeg", "RFoot"] 
'''

model.RH = 60    # Relative humidity [%] 相对湿度 重庆市冬季白天的全年平均相对湿度是60% 自然补风室外空气进入
model.Va = [0.32,0.09,0.05,0.05,0.04,
            0.21,0.07,0.05,
            0.06,0.05,0.03,
            0.05,0.05,0.05,
            0.06,0.03,0.03]   # Air velocity [m/s] 空气流速

''' 
"Head", "Neck", "Chest", "Back", "Pelvis",
    "LShoulder", "LArm", "LHand",
    "RShoulder", "RArm", "RHand",
    "LThigh", "LLeg", "LFoot",
    "RThigh", "RLeg", "RFoot"] 
'''
#修正参数hc, hr

#工作条件调整
model.PAR = 1.8  # Physical activity ratio [-] 身体活动指数 修正为做饭时
#夏季短衣短裤(夏季头部、颈部、小臂、手部、小腿-0)，ASHRAE 55-2017 冬季长保温衣服裤子 (冬季头部、手部=0)
model.iclo=np.array([0,0,0.36,0.87,0.43,0.44,0.48,0.05,0.44,0.48,0.05,0.52,0.37,0.07,0.52,0.37,0.07,]) #服装蒸发效率-冬季
model.Icl=np.array([0,0,1.65,1.2,2.42,0.98,0.78,0.03,0.98,0.78,0.03,0.84,0.62,0.02,0.84,0.62,0.02,])  #服装热阻-冬季
#model.iclo=np.array([0,0,0.27,0.72,0.34,0.42,0,0,0.42,0,0,0.63,0.26,0.32,0.63,0.26,0.32,]) #服装蒸发效率-夏季
#model.Icl=np.array([0,0,1.13,0.5,1.78,0.51,0,0,0.51,0,0,0.4,0.07,0.62,0.4,0.07,0.62,])  #服装热阻-夏季
model.posture = "standing"  # Set the posture 姿势
# Run JOS-3 model
model.simulate(
    times=10,  # Number of loops of a simulation
    dtime=60,  # Time delta [sec]. The default is 60.
)  # Exposure time = 30 [loops] * 60 [sec] = 30 [min] 做饭时间

#Show the results:

import pandas as pd
df = pd.DataFrame(model.dict_results())  # Make pandas.DataFrame
df.TskMean.plot()                        # Show the graph of mean skin temp. 显示平均皮肤温度的图表

#Exporting the results as csv:

model.to_csv(folder="C:/Users/wuxiang/Desktop")

#Show the documentaion of the output parameters:

print(show_outparam_docs())

#Check basal metabolic rate [W/m2] using Getters:

model.BMR

# 直接输出平均皮肤温度 Tskmean
Tsk_mean = model.TskMean
print("平均皮肤温度 (Tskmean):", Tsk_mean)