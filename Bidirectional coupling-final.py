import subprocess #fluent启动
import time
from jos3 import JOS3 #人体热调节模型
from fluent_corba import CORBA #连接fluent
import os
import pathlib
import pandas as pd
import csv
import numpy as np

# Fluent文件目录，Fluent选择直接调用启动程序
# 定义Fluent的启动位置，2021R1版本
ansysPath = pathlib.Path(os.environ["AWP_ROOT211"])
fluentExe = str(ansysPath/"fluent"/"ntbin"/"win64"/"fluent.exe")
CFDworkPath = pathlib.Path(r"C:\Users\wuxiang\Desktop\case\CFD_JOS\kitchen_thermal_files\dp0\FFF\Fluent")
aasFilePath = CFDworkPath/'aaS_FluentId.txt'
jos3_script = "C:\\Users\\wuxiang\\Desktop\\JOS\\jos-3.py"
temp_file_path = CFDworkPath/'report-file-t-person.out'
velocity_file_path = CFDworkPath/'report-file-v-person.out'
SAVE_FILE_PATH = "C:/Users/wuxiang/Desktop/case/CFD_JOS/kitchen_thermal_files/dp0/FFF/Fluent/fluent_temp.csv"

# 修改保存函数，以CSV格式保存结果
def save_fluent(temp_file_path, fluent_temp, velocity_file_path, fluent_velocity, iteration):
    # 读取之前保存的结果
    saved_results_temp = load_saved_results("fluent_temp.csv")
    saved_results_velocity = load_saved_results("fluent_velocity.csv")

    # 添加当前迭代的温度值
    saved_results_temp.append({
        'iteration': iteration,
        'fluent_temp': fluent_temp
    })

    # 添加当前迭代的速度值
    saved_results_velocity.append({
        'iteration': iteration,
        'fluent_velocity': fluent_velocity
    })

    # 将结果保存到文件
    save_results(saved_results_temp, "fluent_temp.csv")
    save_results(saved_results_velocity, "fluent_velocity.csv")

def load_saved_results(file_name):
    # 检查文件是否存在
    file_path = os.path.join(CFDworkPath, file_name)
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            # 从文件加载之前保存的结果
            reader = csv.DictReader(file)
            saved_results = list(reader)
        return saved_results
    else:
        # 如果文件不存在，返回一个空列表
        return []

def save_results(results, file_name):
    file_path = os.path.join(CFDworkPath, file_name)
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", newline='') as file:
        # 将结果保存到CSV文件
        fieldnames = ['iteration', 'fluent_temp'] if "temp" in file_name else ['iteration', 'fluent_velocity']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # 写入CSV文件的表头
        writer.writeheader()
        # 写入每一行的数据
        writer.writerows(results)

# 修改文件读取函数，从fluent监测结果中读取后17列数据
def read_last_value(temp_file_path):
    # 输出读取数据的消息
    print(f"正在读取文件: {temp_file_path}")

    # 读取文件中的数据
    temp_list = []  # 存储从文件中读取的数据的列表
    with open(temp_file_path, "r") as file:
        lines = file.readlines()[3:]  # 跳过前两行标题
        for line in lines:
            values = line.split()
            # 将值转换为浮点数并取正值后添加到列表中
            # 将值转换为浮点数并取正值后添加到列表中
            temp_list.append([round(float(value), 2) for value in values])

    # 获取最后一行数据的后17列值
    last_values = temp_list[-1][-17:]
    return last_values

# 修改文件读取函数，从fluent监测结果中读取后17列数据
def read_last_value(velocity_file_path):
    # 输出读取数据的消息
    print(f"正在读取文件: {velocity_file_path}")

    # 读取文件中的数据
    velocity_list = []  # 存储从文件中读取的数据的列表
    with open(velocity_file_path, "r") as file:
        lines = file.readlines()[3:]  # 跳过前两行标题
        for line in lines:
            values = line.split()
            # 将值转换为浮点数并取正值后添加到列表中
            # 将值转换为浮点数并取正值后添加到列表中
            velocity_list.append([round(float(value), 2) for value in values])

    # 获取最后一行数据的后17列值
    last_values = velocity_list[-1][-17:]
    return last_values

# Fluent运算函数
def run_fluent( is_initialization=False):
    # 执行 Fluent TUI 命令
    
    if is_initialization:
        commands = [Tui_initialize_1, Tui_initialize_2, Tui_initialize_3,
                    Tui_transi_1, Tui_TimeStepSize, Tui_transi_cal_1]
    else:
        commands = [Tui_Set_Flux0, Tui_Set_Flux1, Tui_Set_Flux2, Tui_Set_Flux3, Tui_Set_Flux4, Tui_Set_Flux5, 
                    Tui_Set_Flux6, Tui_Set_Flux7, Tui_Set_Flux8, Tui_Set_Flux9, Tui_Set_Flux10, Tui_Set_Flux11,
                    Tui_Set_Flux14, 
                    Tui_transi_1, Tui_TimeStepSize,  Tui_transi_cal_2]
    
    for i in commands:
        scheme.doMenuCommand(i)

# 服务器会话连接之前，清除工作目录下存在的aaS*.txt文件及其他多余文件
for file in CFDworkPath.glob("*aaS*.txt"): file.unlink()
for file in CFDworkPath.glob("*.trn"): file.unlink()
for file in CFDworkPath.glob("*.out"): file.unlink()

# 启动 Fluent 进程
fluent_process = subprocess.Popen(f'"{fluentExe}" 3ddp -aas -t12', shell=True, cwd=str(CFDworkPath))

# 监控 aasFilePath.txt 文件生成，等待 corba 连接
while True:
    try:
        if not aasFilePath.exists():
            time.sleep(0.2)
            continue
        else:
            if "IOR:" in aasFilePath.open("r").read():
                break
    except KeyboardInterrupt:
         sys.exit()

# 初始化 orb 环境
orb = CORBA.ORB_init()

# 获取 fluent 服务器会话实例
fluent_session = orb.string_to_object(aasFilePath.open("r").read())

#加载case或mesh文件 不能写文件路径 会报错
fluent_session.loadCase('FFF.2-12.cas.h5')

# 获取 scheme 脚本控制器实例
scheme = fluent_session.getSchemeControllerInstance()

# 以下代码是正式模拟程序，初始的 2 步其迭代步数应设置成 100
# Fluent
Flu_numsteps = 360  # Fluent 需要的时间步数
Flu_stepsize = 5  # Fluent 时间步长5s
Flu_maxiter_per_step = 40  # 每个时间步的迭代步数
Flu_numsteps_init = 2  # Fluent 预算稳定时间步数
Flu_maxiter_per_step_init = 100  # 预算稳定每个时间步的迭代步数

# 设置传递时间间隔
time_interval = 10  # fluent与JOS-3计算之间的等待时间

# 计算迭代次数
num_iterations = int((Flu_numsteps * Flu_stepsize / 20) + 1)  # 根据时间间隔计算迭代次数,每间隔60s计算交换一次数据, +1是考虑初始迭代
Flu_numsteps_every =int(Flu_numsteps/(num_iterations-1))  # Fluent 每次传输需要的时间步数

#初始参数-皮肤温度、环境温度
#皮肤热流初始值为初始热流50w/m2，fluent中设置
T_zoneKitch = 25 #夏季工况

#设置TUI命令
# 1.设置初始边界条件：fluent中已经设置好了，这里不用

# 2.如果是时段首次启动Fluent，需要对Fluent初始化
Tui_initialize_1 = '/solve/initialize/compute-defaults/all-zones'
Tui_initialize_2 = '/solve/initialize/set-defaults/temperature '+str(T_zoneKitch+273.15) #初始化环境温度 夏季298k 冬季293k
Tui_initialize_3 = '/solve/initialize/initialize-flow y'

# 3.设置瞬态迭代，时间步和每个时间步迭代次数，用于进行计算
Tui_transi_1 = '/define/models/unsteady-1st-order? yes'
Tui_TimeStepSize = '/solve/set/transient-controls/time-step-size 5' #时间步长1s
Tui_transi_cal_1 = '/solve/dual-time-iterate '+str(Flu_numsteps_init)+' '+str(Flu_maxiter_per_step_init) #预先计算2步，以及每步的迭代次数
Tui_transi_cal_2 = '/solve/dual-time-iterate '+str(Flu_numsteps_every)+' '+str(Flu_maxiter_per_step) #剩余的计算步数，以及每步的迭代次数

# 创建 JOS-3 模型
model = JOS3(
    height=1.62,
    weight=56,
    fat=30,
    age=36,
    sex="female",
    ci=2.23,
    ex_output="all",
)


# 初始环境
model.To = 25  # 夏季

# 运行 JOS-3 模型
model.simulate(
    times=10,  # Number of loops of a simulation
    dtime=60,  # Time delta [sec]. The default is 60.
)  # Exposure time = 30 [loops] * 60 [sec] = 30 [min]


result = model._run()
heat_flux0 = round (result["THLsk"][0] /0.104, 2)#头
heat_flux1 = round (result["THLsk"][1] /0.060, 2)#颈部
heat_flux2 = round (result["THLsk"][2] /0.171, 2)#胸部 
heat_flux3 = round (result["THLsk"][3] /0.159, 2)#背部
heat_flux4 = round (result["THLsk"][4] /0.203, 2)#骨盆
heat_flux5 = round (result["THLsk"][5] /0.069, 2)#左肩膀
heat_flux6 = round (result["THLsk"][6] /0.054, 2)#左臂
heat_flux7 = round (result["THLsk"][7] /0.042, 2)#左手
heat_flux8 = round (result["THLsk"][8] /0.069, 2)#右肩膀
heat_flux9 = round (result["THLsk"][9] /0.054, 2)#右臂
heat_flux10 = round (result["THLsk"][10] /0.042, 2)#右手
heat_flux11 = round ((result["THLsk"][11]  + result["THLsk"][12] + result["THLsk"][13]) /(0.163 + 0.113 + 0.059) , 2)#左大腿+小腿 + 脚
#heat_flux12 = result["THLsk"][12] /0.113#左小腿
#heat_flux13 = result["THLsk"][13] /0.059#左脚
heat_flux14 = round ((result["THLsk"][14]  + result["THLsk"][15] + result["THLsk"][16]) /(0.163 + 0.113 + 0.059) , 2)#右大腿+小腿 + 脚
#heat_flux15 = result["THLsk"][15] /0.113#右小腿
#heat_flux16 = result["THLsk"][16] /0.059#右脚}

# 用于存储每次循环后的 JOS-3 模型计算结果
jos3_results = []

def clear_saved_results():
    file_path1 = os.path.join(CFDworkPath, "fluent_temp.csv")
    file_path2 = os.path.join(CFDworkPath, "fluent_velocity.csv")
    # 检查文件是否存在
    if os.path.exists(file_path1):
        # 如果文件存在，在开始迭代时清除文件
        os.remove(file_path1)
    if os.path.exists(file_path2):
        # 如果文件存在，在开始迭代时清除文件
        os.remove(file_path2)

# 在迭代开始前调用该函数，它会检查并清除 fluent_temp.csv ;fluent_velocity.csv文件
clear_saved_results()

# fluent 与 JOS-3 模型数据传递
for iteration in range(num_iterations):

    # 如果是第一次迭代，执行初始化命令
    is_initialization = iteration == 0

    # 设置 Fluent 的 TUI 命令，更新人体表面温度
    Tui_Set_Flux0 = '/define/boundary-conditions/set/wall head-wall () heat-flux no ' + str(heat_flux0) + ' quit'
    Tui_Set_Flux1 = '/define/boundary-conditions/set/wall neck-wall () heat-flux no ' + str(heat_flux1) + ' quit'
    Tui_Set_Flux2 = '/define/boundary-conditions/set/wall chest-wall () heat-flux no ' + str(heat_flux2) + ' quit'
    Tui_Set_Flux3 = '/define/boundary-conditions/set/wall back-wall () heat-flux no ' + str(heat_flux3) + ' quit'
    Tui_Set_Flux4 = '/define/boundary-conditions/set/wall pelvis-wall () heat-flux no ' + str(heat_flux4) + ' quit'
    Tui_Set_Flux5 = '/define/boundary-conditions/set/wall l_shoulder-wall () heat-flux no ' + str(heat_flux5) + ' quit'
    Tui_Set_Flux6 = '/define/boundary-conditions/set/wall l_arm-wall () heat-flux no ' + str(heat_flux6) + ' quit'
    Tui_Set_Flux7 = '/define/boundary-conditions/set/wall l_hand-wall () heat-flux no ' + str(heat_flux7) + ' quit'
    Tui_Set_Flux8 = '/define/boundary-conditions/set/wall r_shoulder-wall () heat-flux no ' + str(heat_flux8) + ' quit'
    Tui_Set_Flux9 = '/define/boundary-conditions/set/wall r_arm-wall () heat-flux no ' + str(heat_flux9) + ' quit'
    Tui_Set_Flux10 = '/define/boundary-conditions/set/wall r_hand-wall () heat-flux no ' + str(heat_flux10) + ' quit'
    Tui_Set_Flux11 = '/define/boundary-conditions/set/wall l_foot-wall () heat-flux no ' + str(heat_flux11) + ' quit'
    #Tui_Set_Flux12 = '/define/boundary-conditions/set/wall human-wall () heat-flux no ' + str(heat_flux12) + ' quit'
    #Tui_Set_Flux13 = '/define/boundary-conditions/set/wall human-wall () heat-flux no ' + str(heat_flux13) + ' quit'
    Tui_Set_Flux14 = '/define/boundary-conditions/set/wall r_foot-wall () heat-flux no ' + str(heat_flux14) + ' quit'
    #Tui_Set_Flux15 = '/define/boundary-conditions/set/wall human-wall () heat-flux no ' + str(heat_flux15) + ' quit'
    #Tui_Set_Flux16 = '/define/boundary-conditions/set/wall human-wall () heat-flux no ' + str(heat_flux16) + ' quit'
    #Tui_Set_Temp1 = '/define/boundary-conditions/set/wall human-wall () temperature no '+str(T_skin+273.15)+' quit'

    # 运行 Fluent，并传递 JOS-3 模型结果
    run_fluent(is_initialization)

    # 读取 report-file-t-person.out 文件中的最后17个值
    fluent_temp = read_last_value(temp_file_path)
    fluent_velocity = read_last_value(velocity_file_path)
    print(f"Fluent环境温度: {fluent_temp}")
    print(f"Fluent环境速度: {fluent_velocity}")

    # 保存当前 Fluent 计算结果到文件
    save_fluent(temp_file_path, fluent_temp, velocity_file_path, fluent_velocity , iteration)

    # 传递当前 Fluent 计算结果给 JOS-3 模型
    model.To = np.array(fluent_temp) - 273.15  # 转换为摄氏度
    model.Va = np.array(fluent_velocity) 
    
    # 运行 JOS-3 模型
    model.simulate(
    times=1,  # Number of loops of a simulation
    dtime=20,  # Time delta [sec]. The default is 60.
)  # Exposure time = 30 [loops] * 60 [sec] = 30 [min]

    result = model._run()
    # 输出HTLsk的结果
    print("HTLsk Result:", result["THLsk"])

    heat_flux0 = round (result["THLsk"][0] /0.104, 2)#头
    heat_flux1 = round (result["THLsk"][1] /0.060, 2)#颈部
    heat_flux2 = round (result["THLsk"][2] /0.171, 2)#胸部 
    heat_flux3 = round (result["THLsk"][3] /0.159, 2)#背部
    heat_flux4 = round (result["THLsk"][4] /0.203, 2)#骨盆
    heat_flux5 = round (result["THLsk"][5] /0.069, 2)#左肩膀
    heat_flux6 = round (result["THLsk"][6] /0.054, 2)#左臂
    heat_flux7 = round (result["THLsk"][7] /0.042, 2)#左手
    heat_flux8 = round (result["THLsk"][8] /0.069, 2)#右肩膀
    heat_flux9 = round (result["THLsk"][9] /0.054, 2)#右臂
    heat_flux10 = round (result["THLsk"][10] /0.042, 2)#右手
    heat_flux11 = round ((result["THLsk"][11]  + result["THLsk"][12] + result["THLsk"][13]) /(0.163 + 0.113 + 0.059) , 2)#左大腿+小腿 + 脚
    #heat_flux12 = result["THLsk"][12] /0.113#左小腿
    #heat_flux13 = result["THLsk"][13] /0.059#左脚
    heat_flux14 = round ((result["THLsk"][14]  + result["THLsk"][15] + result["THLsk"][16]) /(0.163 + 0.113 + 0.059) , 2)#右大腿+小腿 + 脚
    #heat_flux15 = result["THLsk"][15] /0.113#右小腿
    #heat_flux16 = result["THLsk"][16] /0.059#右脚}

    # 获取 JOS-3 模型计算的皮肤温度
    skin_temperature = model.TskMean
    
    # 输出计算完成的消息
    print("JOS-3计算并传递热流完成.当前皮肤温度:", skin_temperature)

    # 将当前 JOS-3 模型计算结果添加到列表
    jos3_results.append(model.dict_results())

    # 检查是否是最后一次迭代
    if iteration < num_iterations - 1:

        # 等待 Fluent 计算完成
        fluent_process.wait()

        # 休眠指定的时间间隔
        time.sleep(time_interval)

# 等待最后一次 Fluent 计算完成
fluent_process.wait()

# 输出计算完成的消息
print("Fluent计算完成")

# 只输出最后一步迭代的结果
final_result_df = pd.DataFrame(jos3_results[-1])
final_result_df.to_csv("C:/Users/wuxiang/Desktop/jos3_final_result.csv", index=False)

# 显示平均皮肤温度的图表
final_result_df.TskMean.plot()

# 输出计算完成的消息
print("温度图表格输出完成")
