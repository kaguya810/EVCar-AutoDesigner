%% 电机选择设计
clc; clear;

%% 使用说明（2025.06 V3 Build By KAGUYA810）
%
% 修改车辆参数: 更新params结构体中的对应字段值，同工程全部代码。
% 修改电机型号: 更新motor结构体中的对应字段值。

%% 集中化参数
params = struct();

% 车辆基本参数
params.m = 4200;       % 满载质量 (kg)
params.g = 9.8;        % 重力加速度 (m/s^2)
params.f = 0.015;      % 滚动阻力系数
params.Cd = 0.38;      % 空气阻力系数
params.A = 3.769;      % 迎风面积 (m^2)
params.eta_t = 0.92;   % 机械传动效率
params.rho_a = 1.2258; % 空气密度 (kg/m^3)
params.delta = 1.01;   % 质量转换系数

% 性能指标参数
params.u_max = 120;    % 最高车速 (km/h)
params.u_p = 30;       % 爬坡车速 (km/h)
params.alpha_max = atan(0.2); % 最大坡度角 (rad)
params.u_m_kph = 50;   % 加速末速 (km/h)
params.u_m = 50 * (1000/3600); % 加速末速 (m/s)
params.t_a = 9;        % 加速时间 (s)

% 电机设计参数
params.n_b = 2500;     % 电机额定转速 (rpm)
params.n_max_design = 4500; % 设计最高转速 (rpm)

%% 计算中间变量
sin_alpha = sin(params.alpha_max); % 0.1961
cos_alpha = cos(params.alpha_max); % 0.9806

%% 计算基速车速 (km/h 和 m/s)
u_b_kmh = (params.u_max * params.n_b) / params.n_max_design; % 66.67 km/h
u_b = u_b_kmh * (1000/3600);     % 18.52 m/s
if (params.u_m < u_b)
    u_b = 0; % 加速工况基速设定
end

%% 1. 最高车速功率 P_m1 (kW)
rolling_force = params.m * params.g * params.f;
air_force_max = (params.Cd * params.A * params.u_max^2) / 21.15;
total_force_max = rolling_force + air_force_max;
coeff_p1 = params.u_max / (3600 * params.eta_t);
P_m1 = coeff_p1 * total_force_max; % 57.69 kW

%% 2. 最大爬坡度功率 P_m2 (kW)
grade_force = params.m * params.g * (params.f * cos_alpha + sin_alpha);
air_force_grade = (params.Cd * params.A * params.u_p^2) / 21.15;
total_force_grade = grade_force + air_force_grade;
coeff_p2 = params.u_p / (3600 * params.eta_t);
P_m2 = coeff_p2 * total_force_grade; % 79.16 kW

%% 3. 加速性能功率 P_m3 (kW)
rolling_term = (2/3) * params.m * params.g * params.f * params.u_m;
air_term = (params.rho_a * params.Cd * params.A * params.u_m^3) / 5;
accel_term = params.delta * params.m * (params.u_m^2 + u_b^2) / (2 * params.t_a);
total_power = rolling_term + air_term + accel_term;
coeff_p3 = 1 / (1000 * params.eta_t);
P_m3 = coeff_p3 * total_power; % 56.66 kW

%% 电机功率需求
P_e_min = P_m1; % 额定功率下限 (kW)
P_emax_min = max([P_m1, P_m2, P_m3]); % 峰值功率下限 (kW)

%% 电机选型结果
motor = struct();
motor.model = 'SD290高压版';
motor.P_e = 58.00;        % 额定功率 (kW)
motor.P_emax = 100.00;    % 峰值功率 (kW)
motor.n_e = 2500;         % 额定转速 (rpm)
motor.n_max = 8000;       % 最高转速 (rpm)
motor.T_max = 600.00;     % 峰值转矩 (N·m)
motor.voltage = 650.00;   % 电压 (V)

%% 输出结果
fprintf('===== 电机需求功率 =====\n');
fprintf('P_m1 (最高车速): %.2f kW\n', P_m1);
fprintf('P_m2 (最大爬坡): %.2f kW\n', P_m2);
fprintf('P_m3 (加速性能): %.2f kW\n', P_m3);
fprintf('额定功率需求: ≥ %.2f kW\n', P_e_min);
fprintf('峰值功率需求: ≥ %.2f kW\n\n', P_emax_min);

fprintf('===== 电机选型结果 =====\n');
fprintf('型号: %s\n', motor.model);
fprintf('额定功率: %.2f kW\n', motor.P_e);
fprintf('峰值功率: %.2f kW\n', motor.P_emax);
fprintf('额定转速: %.2f rpm\n', motor.n_e);
fprintf('最高转速: %.2f rpm\n', motor.n_max);
fprintf('峰值转矩: %.2f N·m\n', motor.T_max);
fprintf('电压: %.2f V\n', motor.voltage);

