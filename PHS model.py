from pythermalcomfort.models import phs
"""
Parameters
tdb (float or array-like) – dry bulb air temperature, default in [°C]
tr (float or array-like) – mean radiant temperature, default in [°C]
v (float or array-like) – air speed, default in [m/s]
rh (float or array-like) – relative humidity, [%]
met (float or array-like) – metabolic rate, [W/(m2)]
clo (float or array-like) – clothing insulation, [clo]
posture (int) – a numeric value presenting posture of person [sitting=1, standing=2, crouching=3]
wme (float or array-like) – external work, [W/(m2)] default 0

Other Parameters
limit_inputs (boolean default True) – By default, if the inputs are outsude the standard applicability limits the function returns nan. If False returns values even if input values are outside the applicability limits of the model.
The 7933 limits are 15 < tdb [°C] < 50, 0 < tr [°C] < 60, 0 < vr [m/s] < 3, 100 < met [met] < 450, and 0.1 < clo [clo] < 1.
i_mst (float, default 0.38) – static moisture permeability index, [dimensionless]
a_p (float, default 0.54) – fraction of the body surface covered by the reflective clothing, [dimensionless]
drink (int, default 1) – 1 if workers can drink freely, 0 otherwise
weight (float, default 75) – body weight, [kg]
height (float, default 1.8) – height, [m]
walk_sp (float, default 0) – walking speed, [m/s]
theta (float, default 0) – angle between walking direction and wind direction [degrees]
acclimatized (int, default 100) – 100 if acclimatized subject, 0 otherwise
duration (int, default 480) – duration of the work sequence, [minutes]
f_r (float, default 0.97) – emissivity of the reflective clothing, [dimensionless] Some reference values pythermalcomfort.utilities.f_r_garments().
t_sk (float, default 34.1) – mean skin temperature when worker starts working, [°C]
t_cr (float, default 36.8) – mean core temperature when worker starts working, [°C]
t_re (float, default False) – mean rectal temperature when worker starts working, [°C]
t_cr_eq (float, default False) – mean core temperature as a function of met when worker starts working, [°C]
sweat_rate (float, default 0)

Returns
t_re (float) – rectal temperature, [°C]
t_sk (float) – skin temperature, [°C]
t_cr (float) – core temperature, [°C]
t_cr_eq (float) – core temperature as a function of the metabolic rate, [°C]
t_sk_t_cr_wg (float) – fraction of the body mass at the skin temperature
d_lim_loss_50 (float) – maximum allowable exposure time for water loss, mean subject, [minutes]
d_lim_loss_95 (float) – maximum allowable exposure time for water loss, 95% of the working population, [minutes]
d_lim_t_re (float) – maximum allowable exposure time for heat storage, [minutes]
water_loss_watt (float) – maximum water loss in watts, [W]
water_loss (float) – maximum water loss, [g]
"""

results = phs(tdb=34, tr=34, rh=34, v=0.1, met=150, clo=0.5, posture=2, wme=0)
print(results)