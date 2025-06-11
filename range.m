%% 新能源汽车续航里程影响因素分析
clc; clear; close all;

%% ==================== 集中化参数配置 ====================
params = struct();
% 基础固定参数
params.u_a = 60;            % 巡航车速 (km/h)
params.eta_t = 0.92;        % 传动效率
params.eta_e = 0.92;        % 电机效率
params.g = 9.8;             % 重力加速度 (m/s^2)
params.W0 = 138.74;           % 电池总能量 (kWh)

% 基准参数
params.m_base = 4200;       % 满载质量 (kg)
params.m_norm = 3030;       % 整备质量 (Kg)
params.f_base = 0.015;      % 滚动阻力系数
params.Cd_base = 0.38;      % 空气阻力系数
params.A_base = 3.769;          % 迎风面积 (m²)

% 分析范围参数
params.m_range = linspace(params.m_norm, params.m_base, 100);   % 质量范围 (kg)
params.f_range = linspace(0.008, 0.018, 100); % 滚动阻力系数范围
params.Cd_range = linspace(0.25, 0.45, 100);  % 空气阻力系数范围
params.A_range = linspace(1.5, 3.5, 100);     % 迎风面积范围 (m²)

%% ==================== 通用计算函数 ====================
function S = calculate_range(params, varargin)
    % 解析可选参数（允许覆盖基准值）
    p = inputParser;
    addParameter(p, 'm', params.m_base);
    addParameter(p, 'f', params.f_base);
    addParameter(p, 'Cd', params.Cd_base);
    addParameter(p, 'A', params.A_base);
    parse(p, varargin{:});
    
    % 提取参数
    u_a = params.u_a;
    eta_e = params.eta_e;
    eta_t = params.eta_t;
    g = params.g;
    W0 = params.W0;
    m = p.Results.m;
    f = p.Results.f;
    Cd = p.Results.Cd;
    A = p.Results.A;
    
    % 行驶阻力功率计算 (kW)
    rolling_term = m * g * f;
    air_term = (Cd * A * u_a^2) / 21.15;
    P = (u_a / (3600 * eta_t)) * (rolling_term + air_term);
    
    % 续航里程计算 (km)
    S = (W0 * u_a / P) * eta_e;
end

%% ==================== 计算所有影响因素 ====================
% 质量影响
S_m = arrayfun(@(m) calculate_range(params, 'm', m), params.m_range);
eta_norm = 0.85; % 整备质量时的效率
slope_eta = (params.eta_e - eta_norm) / (params.m_base - params.m_norm);
eta_e_range = slope_eta * (params.m_range - params.m_norm) + eta_norm;

% 滚动阻力影响
S_f = arrayfun(@(f) calculate_range(params, 'f', f), params.f_range);

% 风阻系数影响
S_Cd = arrayfun(@(Cd) calculate_range(params, 'Cd', Cd), params.Cd_range);

% 迎风面积影响
S_A = arrayfun(@(A) calculate_range(params, 'A', A), params.A_range);

%% ==================== 创建集成视图 (4合1) ====================
% 图形设置
fig = figure('Position', [100, 100, 1200, 900], 'Name', '续航里程影响因素分析', 'NumberTitle', 'off');
set(fig, 'Color', 'w');
colors = lines(4);  % 创建4种不同颜色

% 1. 质量影响 (左上) - 增加电机效率曲线
subplot(2, 2, 1);

% 绘制续航里程曲线 - 电机效率 @ 整车质量曲线
yyaxis left;
plot(params.m_range, S_m, 'LineWidth', 2, 'Color', colors(1, :));
hold on;

title('(a) 整车质量影响', 'FontSize', 12);
xlabel('整车质量 (kg)', 'FontSize', 10);
ylabel('续航里程 (km)', 'FontSize', 10);
grid on;
xlim([min(params.m_range), max(params.m_range)]);
ylim([min(S_m)-5, max(S_m)+5]);

% 绘制电机效率曲线
yyaxis right;
plot(params.m_range, eta_e_range*100, 'LineWidth', 2, 'Color', [0.8500, 0.3250, 0.0980]);
ylabel('电机效率 (%)', 'FontSize', 10);
ylim([min(eta_e_range)*100, max(eta_e_range)*100]);

% 添加图例
legend('续航里程', '电机效率', 'Location', 'southeast');

% 2. 滚动阻力影响 (右上) - 保持不变
subplot(2, 2, 2);
plot(params.f_range*1000, S_f, 'LineWidth', 2, 'Color', colors(2, :));
hold on;

title('(b) 滚动阻力影响', 'FontSize', 12);
xlabel('滚动阻力系数 (×10^{-3})', 'FontSize', 10);
ylabel('续航里程 (km)', 'FontSize', 10);
grid on;
xlim([min(params.f_range*1000), max(params.f_range*1000)]);
ylim([min(S_f)-5, max(S_f)+5]);

% 3. 空气阻力影响 (左下) - 保持不变
subplot(2, 2, 3);
plot(params.Cd_range, S_Cd, 'LineWidth', 2, 'Color', colors(3, :));
hold on;

title('(c) 空气阻力系数影响', 'FontSize', 12);
xlabel('空气阻力系数 (C_d)', 'FontSize', 10);
ylabel('续航里程 (km)', 'FontSize', 10);
grid on;
xlim([min(params.Cd_range), max(params.Cd_range)]);
ylim([min(S_Cd)-5, max(S_Cd)+5]);

% 4. 迎风面积影响 (右下) - 保持不变
subplot(2, 2, 4);
plot(params.A_range, S_A, 'LineWidth', 2, 'Color', colors(4, :));
hold on;

title('(d) 迎风面积影响', 'FontSize', 12);
xlabel('迎风面积 (m²)', 'FontSize', 10);
ylabel('续航里程 (km)', 'FontSize', 10);
grid on;
xlim([min(params.A_range), max(params.A_range)]);
ylim([min(S_A)-5, max(S_A)+5]);

%% ==================== 性能影响量化分析 ====================
% 创建影响因子表格
fprintf('\n===== 参数变化对续航里程的影响 =====\n');
fprintf('参数变化\t\t基准续航(km)\t新续航(km)\t变化率(%%)\n');

% 质量变化影响
m_test = 1600;
S_base = calculate_range(params);
S_new = calculate_range(params, 'm', m_test);
change = (S_new - S_base)/S_base * 100;
fprintf('质量 %d → %d kg\t%.1f\t\t%.1f\t\t%+.1f\n', params.m_base, m_test, S_base, S_new, change);

% 滚动阻力变化影响
f_test = 0.016;
S_new = calculate_range(params, 'f', f_test);
change = (S_new - S_base)/S_base * 100;
fprintf('阻力 %.3f → %.3f\t%.1f\t\t%.1f\t\t%+.1f\n', params.f_base, f_test, S_base, S_new, change);

% 风阻系数变化影响
Cd_test = 0.35;
S_new = calculate_range(params, 'Cd', Cd_test);
change = (S_new - S_base)/S_base * 100;
fprintf('风阻 %.2f → %.2f\t%.1f\t\t%.1f\t\t%+.1f\n', params.Cd_base, Cd_test, S_base, S_new, change);

% 迎风面积变化影响
A_test = 2.5;
S_new = calculate_range(params, 'A', A_test);
change = (S_new - S_base)/S_base * 100;
fprintf('面积 %.1f → %.1f m²\t%.1f\t\t%.1f\t\t%+.1f\n', params.A_base, A_test, S_base, S_new, change);
