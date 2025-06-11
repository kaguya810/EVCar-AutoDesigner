%% 传动系统设计

%% ========== 集中化参数配置 ==========
params = struct();
% 基础参数
params.m = 4200;           % 满载质量 (kg)
params.g = 9.8;            % 重力加速度 (m/s^2)
params.f = 0.015;          % 滚动阻力系数
params.alpha_max = atan(0.2); % 最大坡度角 (rad)
params.r = 0.364;          % 车轮半径 (m)
params.T_max = 600;        % 电机峰值转矩 (N·m) 
params.eta_t = 0.92;       % 传动效率 
params.n_max = 8000;      % 电机最高转速 (rpm)
params.u_max = 120;        % 最高车速 (km/h)
params.i_t = 7;          % 目标总传动比
params.i0 = 4.0;           % 设计主减速比

% 齿轮通用参数
params.KA = 9.0;           % 中心距系数
params.eta_g = 0.96;       % 减速器效率
params.kc = 7.0;           % 齿宽系数
params.std_modules = [2.0, 2.5, 3.0, 3.5, 4.0]; % 标准模数系列 扩展系列

% 第一级变速器参数
params.mn1 = 3.5;          % 法向模数 (mm) 
params.beta1_min = deg2rad(15); % 最小螺旋角 (rad)
params.beta1_max = deg2rad(30); % 最大螺旋角 (rad)

% 第二级主减速器参数
params.mn2 = 3.5;          % 法向模数 (mm) 修改为2.5
params.beta2_min = deg2rad(15); % 最小螺旋角 (rad)
params.beta2_max = deg2rad(30); % 最大螺旋角 (rad)
params.z_vmin = 17;        % 最小当量齿数
params.KD2 = 13.8;         % 大齿轮直径系数
params.kd = 1;             % 动载系数
params.n = 1;              % 驱动桥数目

% 轴设计参数
params.K_in = 4.3;         % 输入轴经验系数
params.phi = 0.8;          % 附着系数
params.m2_prime = 1.2;    % 负荷系数 (商用车取1.1-1.2)
params.K_half = 0.211;     % 半轴直径系数

%% ========== 1. 传动比需求范围计算 ==========
F_grade = params.m * params.g * (params.f * cos(params.alpha_max) + sin(params.alpha_max));
i_t_min = (F_grade * params.r) / (params.T_max * params.eta_t); % 爬坡最小传动比
i_t_max = 0.377 * (params.n_max * params.r) / params.u_max;     % 车速最大传动比

% 目标总传动比设定
ig = params.i_t / params.i0; % 变速器传动比

fprintf('===== 传动比需求范围 =====\n');
fprintf('爬坡要求: i_t >= %.2f\n', i_t_min);
fprintf('车速要求: i_t <= %.2f\n', i_t_max);
fprintf('目标总传动比: %.2f\n', params.i_t);
fprintf('设计主减速比 i0: %.2f\n', params.i0);
fprintf('设计变速器传动比 ig: %.2f\n', ig);

%% ========== 2. 第一级变速器设计 ==========
A1 = params.KA * (params.T_max * ig * params.eta_g)^(1/3);
A1 = round_to_standard(A1); % 中心距标准化

% 齿数和初算
Zh1_est = (2 * A1 * cos(params.beta1_min)) / params.mn1;
z1_est = floor(Zh1_est / (1 + ig));
z2_est = Zh1_est - z1_est;

% 工艺合理性处理
z1 = max(17, round(z1_est)); 
z2 = round(z2_est);
ig_actual = z2 / z1;  % 实际传动比

% 实际螺旋角计算
beta_actual1 = acos((params.mn1 * (z1 + z2)) / (2 * A1));
beta_actual1_deg = rad2deg(beta_actual1);

% 螺旋角工艺检查
if beta_actual1_deg < rad2deg(params.beta1_min) || beta_actual1_deg > rad2deg(params.beta1_max)
    A1 = A1 + 5; 
    beta_actual1 = acos((params.mn1 * (z1 + z2)) / (2 * A1));
    beta_actual1_deg = rad2deg(beta_actual1);
end

% 几何参数计算
d1 = params.mn1 * z1 / cos(beta_actual1);     % 分度圆直径
da1 = d1 + 2 * params.mn1;                   % 齿顶圆直径
df1 = d1 - 2.5 * params.mn1;                 % 齿根圆直径
db1 = d1 * cosd(20);                         % 基圆直径

d2 = params.mn1 * z2 / cos(beta_actual1);
da2 = d2 + 2 * params.mn1;
df2 = d2 - 2.5 * params.mn1;
db2 = d2 * cosd(20);

%% ========== 3. 第二级主减速器设计 ==========
% 计算转矩 (新增)
T_c = (params.kd * params.T_max * params.i_t * params.eta_g) / params.n;

% 大齿轮直径计算 (新增)
D2 = params.KD2 * T_c^(1/3); % 单位: mm

% 初始螺旋角 (20°)
beta0 = deg2rad(20);

% 按目标传动比分配齿数
z3 = 14;  % 小齿轮齿数
z4 = round(z3 * params.i0); % 大齿轮齿数
i0_actual = z4 / z3;  % 实际传动比

% 模数计算 (新增)
m_n_est = D2 * cos(beta0) / z4;

% 选择最接近的标准模数
[~, idx] = min(abs(params.std_modules - m_n_est));
mn2_actual = params.std_modules(idx); % 实际使用的模数

% 修正螺旋角
cos_beta = (mn2_actual * z4) / D2;
if abs(cos_beta) > 1
    error('无法修正螺旋角，cos_beta=%f > 1，请调整参数', cos_beta);
end
beta_actual2 = acos(cos_beta);
beta_actual2_deg = rad2deg(beta_actual2);

% 当量齿数验证
z_v3 = z3 / (cos(beta_actual2))^3;

% 几何参数计算
d3 = mn2_actual * z3 / cos(beta_actual2);     % 分度圆直径
da3 = d3 + 2 * mn2_actual;                   % 齿顶圆直径
df3 = d3 - 2.5 * mn2_actual;                 % 齿根圆直径
db3 = d3 * cosd(20);                         % 基圆直径

d4 = mn2_actual * z4 / cos(beta_actual2);
da4 = d4 + 2 * mn2_actual;
df4 = d4 - 2.5 * mn2_actual;
db4 = d4 * cosd(20);

% 计算中心距 (用于输出)
A2 = (mn2_actual * (z3 + z4)) / (2 * cos(beta_actual2));

%% ========== 4. 轴径设计 ==========
% 输入轴
d_in = params.K_in * (params.T_max)^(1/3);  % mm

% 中间轴 (新增)
d_mid = 0.45 * A1;  % mm

% 驱动桥载荷 (新增)
G2 = params.m * params.g / 2;  % N (取满载重量的50%)

% 附着力矩 (修正)
M_phi = 0.5 * params.m2_prime * G2 * params.r * params.phi; % N·m

% 半轴直径 (注意单位转换)
d_half = params.K_half * (M_phi * 1000)^(1/3); % mm

%% ========== 5. 结果输出 ==========
fprintf('\n\n======================== 传动系统设计结果 ========================\n');

% 总传动比验证
i_t_actual = ig_actual * i0_actual;
fprintf('\n===== 传动比验证 =====\n');
fprintf('实际总传动比: %.2f\n', i_t_actual);
fprintf('需求范围: %.2f - %.2f\n', i_t_min, i_t_max);
fprintf('设计主减速比 i0: %.2f\n', i0_actual);
fprintf('设计变速器传动比 ig: %.2f\n', ig_actual);

% 第一级变速器结果
fprintf('\n===== 第一级变速器设计 =====\n');
fprintf('中心距: %d mm (标准化)\n', A1);
fprintf('法向模数: %.1f mm (标准值)\n', params.mn1);
fprintf('螺旋角: %.2f° (工艺范围: %.0f°-%.0f°)\n',...
        beta_actual1_deg, rad2deg(params.beta1_min), rad2deg(params.beta1_max));
fprintf('齿宽: %.1f mm (齿宽系数: %.1f)\n', params.kc*params.mn1, params.kc);
fprintf('小齿轮齿数: %d (最小齿数: %d)\n', z1, 17);
fprintf('大齿轮齿数: %d\n', z2);
fprintf('实际传动比: %.2f\n', ig_actual);

fprintf('----- 几何参数 -----\n');
fprintf('参数\t\t小齿轮(mm)\t大齿轮(mm)\n');
fprintf('分度圆直径\t%.2f\t\t%.2f\n', d1, d2);
fprintf('齿顶圆直径\t%.2f\t\t%.2f\n', da1, da2);
fprintf('齿根圆直径\t%.2f\t\t%.2f\n', df1, df2);
fprintf('基圆直径\t%.2f\t\t%.2f\n\n', db1, db2);

% 第二级主减速器结果
fprintf('\n===== 第二级主减速器设计 =====\n');
fprintf('大齿轮直径: %.2f mm (直径系数K_D2=%.1f)\n', D2, params.KD2);
fprintf('计算转矩: %.1f N.m\n', T_c);
fprintf('中心距: %.2f mm\n', A2);
fprintf('实际法向模数: %.2f mm (计算值: %.2f mm)\n', mn2_actual, m_n_est);
fprintf('螺旋角: %.2f° (初始: 20°)\n', beta_actual2_deg);
fprintf('齿宽: %.1f mm (齿宽系数: %.1f)\n', params.kc*mn2_actual, params.kc);
fprintf('小齿轮齿数: %d\n', z3);
fprintf('大齿轮齿数: %d\n', z4);
fprintf('实际传动比: %.4f\n', i0_actual);
fprintf('当量齿数验证: z_v3 = %.2f (>%.0f 安全)\n', z_v3, params.z_vmin);

fprintf('----- 几何参数 -----\n');
fprintf('参数\t\t小齿轮(mm)\t大齿轮(mm)\n');
fprintf('分度圆直径\t%.2f\t\t%.2f\n', d3, d4);
fprintf('齿顶圆直径\t%.2f\t\t%.2f\n', da3, da4);
fprintf('齿根圆直径\t%.2f\t\t%.2f\n', df3, df4);
fprintf('基圆直径\t%.2f\t\t%.2f\n\n', db3, db4);

% 轴径设计结果
fprintf('\n===== 轴径设计 =====\n');
fprintf('输入轴直径: %.2f mm (系数K=%.1f)\n', d_in, params.K_in);
fprintf('中间轴直径: %.2f mm (计算: 0.45*A1)\n', d_mid);
fprintf('半轴直径: %.2f mm (附着系数φ=%.1f)\n', d_half, params.phi);
fprintf('附着力矩: %.1f N.m\n', M_phi);

% ========== 6. 设计验证 ==========
fprintf('\n===== 设计验证 =====');
fprintf('\n1. 总传动比: %.2f (需求: %.2f - %.2f)', i_t_actual, i_t_min, i_t_max);
fprintf('\n2. 螺旋角: 一级=%.2f° (%.0f°-%.0f°), 二级=%.2f° (%.0f°-%.0f°)',...
        beta_actual1_deg, rad2deg(params.beta1_min), rad2deg(params.beta1_max),...
        beta_actual2_deg, rad2deg(params.beta2_min), rad2deg(params.beta2_max));
fprintf('\n3. 根切预防: 一级小齿轮z1=%d(≥17), 二级当量齿数z_v3=%.2f(≥%.0f)',...
        z1, z_v3, params.z_vmin);
fprintf('\n4. 标准模数: 一级=%.1f(mm), 二级=%.2f(mm)', params.mn1, mn2_actual);
fprintf('\n5. 中心距标准化: 一级=%d(mm), 二级=%.2f(mm)', A1, A2);

% 验证条件
beta_range1 = [rad2deg(params.beta1_min), rad2deg(params.beta1_max)];
beta_range2 = [rad2deg(params.beta2_min), rad2deg(params.beta2_max)];

is_ratio_valid = (i_t_actual >= i_t_min) && (i_t_actual <= i_t_max);
is_beta_valid = (beta_actual1_deg >= beta_range1(1)) && (beta_actual1_deg <= beta_range1(2)) && ...
                (beta_actual2_deg >= beta_range2(1)) && (beta_actual2_deg <= beta_range2(2));
is_undercut_valid = (z1 >= 17) && (z_v3 >= params.z_vmin);

fprintf('\n\n===== 设计状态 =====');
if is_ratio_valid
    fprintf('\n✓ 总传动比 %.2f 在需求范围 [%.2f-%.2f] 内', i_t_actual, i_t_min, i_t_max);
else
    fprintf('\n✗ 总传动比 %.2f 超出需求范围 [%.2f-%.2f]', i_t_actual, i_t_min, i_t_max);
end

if is_beta_valid
    fprintf('\n✓ 螺旋角均在工艺要求范围内');
else
    fprintf('\n✗ 螺旋角超出工艺范围: 一级=%.2f°(要求%.0f°-%.0f°), 二级=%.2f°(要求%.0f°-%.0f°)',...
            beta_actual1_deg, beta_range1(1), beta_range1(2),...
            beta_actual2_deg, beta_range2(1), beta_range2(2));
end

if is_undercut_valid
    fprintf('\n✓ 根切预防措施有效');
else
    fprintf('\n✗ 根切风险: 一级z1=%d<17 或 二级z_v3=%.2f<%.0f', z1, z_v3, params.z_vmin);
end

if is_ratio_valid && is_beta_valid && is_undercut_valid
    fprintf('\n\n✅ 设计合格: 所有工艺和功能要求均满足!\n');
else
    fprintf('\n\n⚠️ 设计存在问题: 请检查不满足条件的项目!\n');
end

fprintf('\n======================== 设计完成 ========================\n');


%% ========== 辅助函数：中心距标准化 ==========
function std_value = round_to_standard(value)
    std_series = 50:5:200; % 生成50-200的5mm间隔系列
    [~, idx] = min(abs(std_series - value));
    std_value = std_series(idx);
end
