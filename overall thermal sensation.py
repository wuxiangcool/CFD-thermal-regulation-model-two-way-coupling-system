def calculate_overall_sensation(local_sensations):
    """
    根据局部感受计算整体热感觉
    :param local_sensations: 包含各个局部感受的列表
    :return: 热感受模型类型和整体热感觉值
    """
    # 统计正感受和负感受的数量
    n_minus = sum(1 for s in local_sensations if s < 0)
    n_plus = sum(1 for s in local_sensations if s > 0)
    
    # 初始化热感受模型类型和整体热感觉
    model_type = ""
    overall_sensation = 0
    less_extreme_sensations = []  # 设置默认值
    
    # 'no-opposite-sensation'条件的判断
    if n_minus == 0 or n_plus == 0 or (n_minus > n_plus and max(local_sensations) <= 1) or (n_plus > n_minus and min(local_sensations) >= -1):
        # 如果满足'no-opposite-sensation'条件，则进一步判断属于哪种模型
        print("no-opposite-sensation model")
        if abs(max(local_sensations)) >= 2 or abs(min(local_sensations)) >= 2:
            model_type = "High levels of thermal sensation (complaint model)"
            
            third_max = sorted(local_sensations)[-3]
            third_min = sorted(local_sensations)[2]
            
            if third_max > 2:  # Warm side
                print("Warm side")
                overall_sensation = 0.5 * max(local_sensations) + 0.5 * third_max
            elif third_min < -2:  # Cold side
                print("Cold side")
                overall_sensation = 0.38 * min(local_sensations) + 0.62 * third_min
        else:
            model_type = "Low levels of thermal sensation (gradual model)"
            if n_plus >= n_minus:
                interval = 2 / (len(local_sensations) - 2)
                #print("interval：", interval)
                local_sensations_sorted = sorted(local_sensations, reverse=True)  # 按降序排列
                third_max = local_sensations_sorted[2]  # 第三大的值
                # 判断条件
                i=n_plus+1
                if max(local_sensations) > 2 - interval * (i - 2) and third_max < 2: #Slightly warm sensations
                    print("Slightly warm sensations") 
                    less_extreme_sensations = local_sensations_sorted[:i]
                    overall_sensation = sum(less_extreme_sensations) / i
                else:
                     print("wrong1")   
            if n_plus < n_minus:
                interval = 2 / (len(local_sensations) - 2)
                local_sensations_sorted = sorted(local_sensations) # 按升序排列
                third_min = local_sensations_sorted[2]  # 第三小的值
                i=n_minus+1
                # 判断条件
                if min(local_sensations) < -2 + interval * (i - 2) and third_min > -2: #Slightly cool sensations
                    print("Slightly cool sensations") 
                    less_extreme_sensations = local_sensations_sorted[:i]
                    overall_sensation = sum(less_extreme_sensations) / i
                else:
                     print("wrong2")   

                
    else:
        # 如果不满足'no-opposite-sensation'条件，则属于'opposite-sensation'模型
        model_type = "opposite-sensation model"
        print("opposite-sensation model")
        # 获取第2、3、4个数据
        relevant_sensations = local_sensations[1:4] #主要部位的热感觉
        # 如果其中有一个小于 -1，则整体热感觉值为这三个数据中的最小值
        if any(s < -1 for s in relevant_sensations):
            overall_sensation = min(relevant_sensations)
        else:
            overall_sensation = final_overall_sensation
       
    return model_type, overall_sensation

def calculate_individual_force(local_sensations, a, b, c):
    """
    计算个体力量
    :param delta_Slocal: 局部感受变化
    :param a: 斜率系数
    :param b: 纵截距
    :param c: 截距
    :return: 个体力量
    """
    delta_Slocal=local_sensations

    if delta_Slocal <=-2:
       a=[0.54,	0.91, 0.91,	0.94, 0.43,	0.37, 0.25, 0.43, 0.37, 0.25, 0.81, 0.7, 0.5, 0.81, 0.7, 0.5 ]
       b=[-1.1,	-1.14, -0.92, -0.64, -0.56,	-0.73, 0, -0.56, -0.73, 0, -0.6, -0.59, 0, -0.6, -0.59, 0 ]
       c=[-2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2 ]
    if -2< delta_Slocal <2:
       a=[0.5,	0.57, 0.46,	0.32, 0.28,	0.38, 0, 0.28,	0.38, 0, 0.3, 0.29, 0,0.3, 0.29, 0 ]
       b=[0,0, 0, 0, 0,	0, 0,0, 0, 0,0, 0, 0,0, 0, 0 ]
       c=[0,0, 0, 0, 0,	0, 0,0, 0, 0,0, 0, 0,0, 0, 0 ]
    if delta_Slocal>=2:
       a=[0.69,	1.14, 0.92,	0.64, 0.56,	0.73, 0, 0.56,	0.73, 0, 0.6, 0.59, 0, 0.6, 0.59, 0 ]
       b=[-1.1,	-1.14, -0.92, -0.64, -0.56,	-0.73, 0, -0.56, -0.73, 0, -0.6, -0.59, 0, -0.6, -0.59, 0 ]
       c=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 1 ]

    individual_force = a * (delta_Slocal - c) + b

    return individual_force

def calculate_final_overall_sensation(Soverall_bigger_group, Soverall_modifier, second_max_modifier):
    """
    计算最终的整体感受
    :param Soverall_bigger_group: 较大组的整体感受
    :param Soverall_modifier: 个体力量对整体感受的修正值
    :param second_max_modifier: 第二大个体力量
    :return: 最终整体感受
    """
    combined_force = max(Soverall_modifier) + 0.1 * max(second_max_modifier, default=0)
    final_overall_sensation = Soverall_bigger_group + combined_force
    return final_overall_sensation

# 示例用法
local_sensations = [-0.6, 	0.6 ,	0.1 ,	-0.5, 	0.9 ,	-0.1 	,0.1, 	0.0 ,	-0.3, 	0.0, 	0.4 ,	1.0 ,	0.0 ,	0.6, 	0.7 ,	0.0 
 ]
model_type, overall_sensation = calculate_overall_sensation(local_sensations)
print("热感受模型类型：", model_type)
print("整体热感觉：", overall_sensation)
