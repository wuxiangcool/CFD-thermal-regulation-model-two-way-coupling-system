from pythermalcomfort.models import two_nodes
from pythermalcomfort.utilities import body_surface_area

#输入参数
#tdb (float or array-like) - dry bulb air temperature, default in [°C] 
#tr (float or array-like) - mean radiant temperature, default in [°C] 
#v (float or array-like) - air speed, default in [m/s] in [fps] 
#rh (float or array-like) -relative humidity, [%]
#met (float or array-like) - metabolic rate, [met]
#clo (float or array-like) – clothing insulation, [clo]
#wme (float or array-like) - external work, [met] 
#default Obody_surface_area (float) - body surface area, default value 1.8258 [m2] 
#The body surface area can be calculated using the functionpythermalcomfort.utilities.body_surface_area()
#p_atmospheric (float) - atmospheric pressure, default value 101325 [Pa] in [atm] if units = 'IP'body_position (str default="standing" or array-like) - select either "sitting" or "standing"
#max_skin_blood_flow (float) - maximum blood flow from the core to the skin, [kg/h/m2] 

# 手动计算 body_surface_area 的值
weight = 65
height = 1.7
bsa_value = body_surface_area(weight, height, formula='dubois')

# 将 body_surface_area 的值传递给 two_nodes 函数
result = two_nodes(tdb=34, tr=34, v=0.1, rh=34, met=1.2, clo=0.6, body_surface_area=bsa_value)

# 打印结果
print(result)


