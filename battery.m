%% 电池系统设计

%% 集中化参数
params = struct();

% 电池单体参数
params.battery.V_s = 3.6;          % 单体电压 (V)
params.battery.C_s = 5;            % 单体容量 (Ah)
params.battery.E_s = 18.25;        % 单体能量 (Wh)
params.battery.m_s = 0.0678;       % 单体质量 (kg)
params.battery.model = '亿纬锂能50E 21700'; % 电池型号

% 电机参数
params.motor.U_e = 650;            % 电机额定电压 (V)
params.motor.P_emax = 100;         % 电机峰值功率 (kW)
params.motor.eta_e = 0.90;         % 电机效率
params.motor.eta_ec = 0.95;        % 控制器效率

% 车辆参数
params.vehicle.S = 200;            % 续驶里程 (km)
params.vehicle.u = 60;             % 匀速车速 (km/h)
params.vehicle.m = 4200;           % 满载质量 (kg)
params.vehicle.g = 9.8;            % 重力加速度 (m/s^2)
params.vehicle.f = 0.015;          % 滚动阻力系数
params.vehicle.Cd = 0.38;          % 空气阻力系数
params.vehicle.A = 3.769;          % 迎风面积 (m^2)
params.vehicle.eta_t = 0.92;       % 传动效率

% 系统参数
params.system.DOD = 0.90;          % 放电深度（DOD）

%% 1. 串联数目计算
n_s = ceil(params.motor.U_e / params.battery.V_s);  % 181节
U_pack = n_s * params.battery.V_s; % 651.6V

%% 2. 匀速行驶功率计算
F_f = params.vehicle.m * params.vehicle.g * params.vehicle.f;          % 滚动阻力 (N)
F_w = (params.vehicle.Cd * params.vehicle.A * params.vehicle.u^2) / 21.15; % 空气阻力 (N)
F_total = F_f + F_w;                % 总阻力 (N)
P_req = (F_total * params.vehicle.u) / (3600 * params.vehicle.eta_t); % 需求功率 (kW)
P_batt = P_req / (params.motor.eta_e * params.motor.eta_ec); % 电池输出功率 (kW)

%% 3. 续驶里程能量计算
t = params.vehicle.S / params.vehicle.u; % 行驶时间 (h)
E_total = P_batt * t * 1000;        % 总能耗 (Wh)
E_batt = E_total / params.system.DOD; % 电池组能量 (Wh)

%% 4. 并联数目计算 (能量需求)
n_p_energy = ceil(E_batt / (n_s * params.battery.E_s)); % 21组

%% 5. 峰值功率校核
P_s = params.battery.V_s * params.battery.C_s;  % 单体功率 (W)
P_bmax = (P_s * n_s * n_p_energy) / 1000;       % 电池组功率 (kW)
P_demand = params.motor.P_emax / (params.motor.eta_e * params.motor.eta_ec); % 需求功率 (kW)

% 功率不满足时重新计算
if P_bmax < P_demand
    n_p_power = ceil(P_demand * 1000 / (P_s * n_s * params.motor.eta_e * params.motor.eta_ec));
    n_p = max(n_p_energy, n_p_power);            % 取较大值
else
    n_p = n_p_energy;
end

%% 6. 电池组参数计算
N_total = n_s * n_p;                % 总电池数
C_pack = params.battery.C_s * n_p;  % 总容量 (Ah)
E_pack = N_total * params.battery.E_s / 1000; % 总能量 (kWh)
m_pack = N_total * params.battery.m_s; % 总质量 (kg)

%% 7. 续驶里程验证
E_usable = E_pack * 1000 * params.system.DOD; % 可用能量 (Wh)
t_actual = E_usable / (P_batt * 1000);        % 实际行驶时间 (h)
S_actual = params.vehicle.u * t_actual;       % 实际续驶里程 (km)

%% 输出结果
fprintf('===== 电池组参数 =====\n');
fprintf('电池型号: %s\n', params.battery.model);
fprintf('串联数目: %d 节\n', n_s);
fprintf('并联数目: %d 组\n', n_p);
fprintf('总电池数: %d 节\n', N_total);
fprintf('总电压: %.2f V\n', U_pack);
fprintf('总容量: %.2f Ah\n', C_pack);
fprintf('总能量: %.2f kWh\n', E_pack);
fprintf('总质量: %.2f kg\n\n', m_pack);

fprintf('===== 性能验证 =====\n');
fprintf('匀速需求功率: %.2f kW\n', P_req);
fprintf('电池输出功率: %.2f kW\n', P_batt);
fprintf('峰值功率需求: %.2f kW\n', P_demand);
fprintf('电池组输出功率: %.2f kW\n', (P_s * n_s * n_p)/1000);
if S_actual >= params.vehicle.S
    fprintf('实际续驶里程: %.2f km > %.0f km (满足要求)\n', S_actual, params.vehicle.S);
else
    fprintf('实际续驶里程: %.2f km < %.0f km (不满足要求)\n', S_actual, params.vehicle.S);
end

