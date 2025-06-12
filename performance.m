%% 新能源汽车动力性能分析
clc; clear; close all;

%% ==================== 参数集中化配置 ====================
params = struct();
% 车辆参数
params.vehicle.m = 4200;           % 满载质量 (kg)
params.vehicle.g = 9.8;            % 重力加速度 (m/s^2)
params.vehicle.f = 0.015;          % 滚动阻力系数
params.vehicle.Cd = 0.38;          % 风阻系数
params.vehicle.A = 3.769;              % 迎风面积 (m^2)
params.vehicle.eta_t = 0.92;       % 传动效率
params.vehicle.r = 0.364;          % 车轮半径 (m)
params.vehicle.delta = 1.01;        % 质量转换系数

% 电机参数
params.motor.T_max = 600;          % 峰值转矩 (N·m)
params.motor.P_max = 156;           % 峰值功率 (kW)
params.motor.n_e = 2500;           % 额定转速 (rpm)
params.motor.n_max = 8000;        % 最高转速 (rpm)

% 传动系统参数
params.drivetrain.i_t = 7.11;     % 总传动比

% 目标车速参数
params.target.v_test = 50;        % 加速性能测试目标车速 (km/h)
params.target.v_grade = 30;        % 爬坡度测试目标车速 (km/h)

%% ==================== 行驶阻力计算 ====================
% 车速范围 (km/h)
v_kmh = linspace(0, 150, 1000); 

% 行驶阻力计算 (N)
F_roll = params.vehicle.m * params.vehicle.g * params.vehicle.f * ones(size(v_kmh));  % 滚动阻力
F_air = (params.vehicle.Cd * params.vehicle.A * v_kmh.^2) / 21.15;  % 空气阻力
F_res = F_roll + F_air;  % 总行驶阻力

% ==================== 电机驱动力计算 ====================
% 转速-车速关系 (rpm)
n = (v_kmh * params.drivetrain.i_t) ./ (0.377 * params.vehicle.r);

% 电机转矩特性 (分恒转矩区和恒功率区)
T_motor = zeros(size(n));
for i = 1:length(n)
    if n(i) <= params.motor.n_e
        T_motor(i) = params.motor.T_max;  % 恒转矩区
    elseif n(i) <= params.motor.n_max
        T_motor(i) = (params.motor.P_max * 1000) / (2 * pi * n(i) / 60);  % 恒功率区
    else
        T_motor(i) = 0;  % 超过最高转速
    end
end

% 驱动力计算 (N)
F_drive = (T_motor * params.drivetrain.i_t * params.vehicle.eta_t) / params.vehicle.r;

%% ==================== 最高车速分析 ====================
diff = F_drive - F_res;
idx_max = find(diff >= 0, 1, 'last');
v_max = v_kmh(idx_max);

%% ==================== 爬坡度分析 ====================
function grade = calculate_grade(F_drive, F_res, F_roll, params)
    F_available = F_drive - F_res + F_roll;  
    sin_alpha = F_available ./ (params.vehicle.m * params.vehicle.g);
    sin_alpha = min(max(sin_alpha, 0), 0.5); 
    grade = sin_alpha * 100; 
end

grade = calculate_grade(F_drive, F_res, F_roll, params);

% ==================== 加速性能分析 ====================
a = (F_drive - F_res) ./ (params.vehicle.delta * params.vehicle.m);
v_mps = v_kmh / 3.6;  % 转换为m/s
[~, idx_target] = min(abs(v_kmh - params.target.v_test));
dt = (v_mps(2) - v_mps(1)) ./ a(1:idx_target);
t_acc = cumsum(dt);
t_0_target = t_acc(end);

%% ==================== 绘图与结果输出 ====================
figure('Position', [50, 50, 1200, 900], 'Name', '新能源汽车综合性能分析', 'NumberTitle', 'off');
set(gcf, 'Color', 'w');

% 定义灰度颜色方案
gray_drive = [0 0 0];        % 黑色 - 驱动力
gray_roll = [0.4 0.4 0.4];   % 深灰 - 滚动阻力
gray_air = [0.6 0.6 0.6];    % 中灰 - 空气阻力
gray_res = [0.2 0.2 0.2];    % 黑灰 - 总阻力
gray_grade = [0.1 0.1 0.1];  % 深黑 - 爬坡度
gray_acc = [0 0 0];          % 黑色 - 加速度
gray_time = [0.4 0.4 0.4];   % 深灰 - 加速时间
gray_motor = [0.2 0.2 0.2];  % 黑灰 - 电机特性

% 1. 驱动力-阻力平衡图 (左上)
subplot(2, 2, 1);
plot(v_kmh, F_drive, 'Color', gray_drive, 'LineWidth', 1.5, 'LineStyle', '-');
hold on;
plot(v_kmh, F_roll, 'Color', gray_roll, 'LineWidth', 1.5, 'LineStyle', ':');
plot(v_kmh, F_air, 'Color', gray_air, 'LineWidth', 1.5, 'LineStyle', '-.');
plot(v_kmh, F_res, 'Color', gray_res, 'LineWidth', 1.5, 'LineStyle', '--');
plot([v_max, v_max], [0, max(F_drive)], 'k:', 'LineWidth', 1.5);  % 保持虚线
text(v_max-46, max(F_drive)*0.3, sprintf('最高车速: %.1f km/h', v_max),...
    'FontSize', 10, 'Color', 'k');  % 黑色文字

xlabel('车速 (km/h)', 'FontSize', 10);
ylabel('力 (N)', 'FontSize', 10);
title('(a) 驱动力-阻力平衡图', 'FontSize', 12);
legend('电机驱动力', '滚动阻力', '空气阻力', '总行驶阻力', '最高车速',...
       'TextColor','k');  % 黑色图例文本
grid on;
set(gca, 'FontSize', 10, 'XColor','k','YColor','k');  % 黑色坐标轴
xlim([0, max(v_kmh)]);
ylim([0, max(F_drive)*1.1]);

% 2. 车速-爬坡度曲线 (右上)
subplot(2, 2, 2);
plot(v_kmh, grade, 'Color', gray_grade, 'LineWidth', 1.5, 'Marker', 'o', 'MarkerSize', 3);
hold on;
plot([params.target.v_grade, params.target.v_grade], [0, 50], 'k:', 'LineWidth', 1.5);
plot([0, max(v_kmh)], [20, 20], 'k-.', 'LineWidth', 1.5);  % 改为黑色点划线

% 获取并显示关键爬坡度值
idx_grade = find(v_kmh >= params.target.v_grade, 1);
actual_grade = grade(idx_grade);
text_str1 = sprintf('设计要求: %d%%@%dkm/h', 20, params.target.v_grade);
text_str2 = sprintf('实际值: %.1f%%', actual_grade);

text(64, 22, text_str1, 'FontSize', 10, 'Color', 'k');
text(32, 28, text_str2, 'FontSize', 10, 'Color', 'k'); % 黑色文字

xlabel('车速 (km/h)', 'FontSize', 10);
ylabel('爬坡度 (%)', 'FontSize', 10);
title('(b) 车速-爬坡度性能曲线', 'FontSize', 12);
grid on;
set(gca, 'FontSize', 10, 'XColor','k','YColor','k');
xlim([0, max(v_kmh)]);
ylim([0, min(max(grade)*1.2, 50)]);

% 3. 车速-加速度曲线 (左下)
subplot(2, 2, 3);
yyaxis left;
line_acc = plot(v_kmh, a, 'Color', gray_acc, 'LineWidth', 1.5, 'LineStyle', '-');
ylabel('加速度 (m/s²)', 'FontSize', 10);
ylim([0, max(a)*1.1]);
set(gca, 'YColor', 'k');  % 左侧Y轴黑色

yyaxis right;
line_time = plot(v_kmh(1:idx_target), t_acc, 'Color', gray_time, 'LineWidth', 1.5, 'LineStyle', '--');
ylabel('加速时间 (s)', 'FontSize', 10);
set(gca, 'YColor', 'k');  % 右侧Y轴黑色

text(10, t_0_target*0.8, sprintf('0-%dkm/h: %.1f s', params.target.v_test, t_0_target),...
    'FontSize', 10, 'BackgroundColor', 'w', 'Color', 'k');  % 白底黑字

xlabel('车速 (km/h)', 'FontSize', 10);
title('(c) 车速-加速度性能曲线', 'FontSize', 12);
grid on;
set(gca, 'FontSize', 10);
legend([line_acc, line_time], {'加速度', '加速时间'}, 'Location', 'northeast', 'TextColor','k');
xlim([0, 100]);

% 4. 电机转矩-转速特性 (右下)
subplot(2, 2, 4);
plot(n, T_motor, 'Color', gray_motor, 'LineWidth', 1.5, 'Marker', '+');
hold on;
% 标注额定转速和最高转速
plot([params.motor.n_e, params.motor.n_e], [0, params.motor.T_max], 'k:', 'LineWidth', 1.5);
text(400, params.motor.T_max*0.8, sprintf('额定转速: %d rpm', params.motor.n_e),...
    'FontSize', 10, 'Color', 'k');
plot([params.motor.n_max, params.motor.n_max], [0, min(T_motor)], 'k-.', 'LineWidth', 1.5);
text(5900, params.motor.T_max*0.28, sprintf('最高转速: %d rpm', params.motor.n_max),...
    'FontSize', 10, 'Color', 'k');

xlabel('电机转速 (rpm)', 'FontSize', 12);
ylabel('电机转矩 (N·m)', 'FontSize', 12);
title('(d) 电机转矩-转速特性', 'FontSize', 14);
grid on;
set(gca, 'FontSize', 12, 'XColor','k','YColor','k');
ylim([0, params.motor.T_max*1.1]);


%% 性能分析结果输出
fprintf('===== 车辆性能分析结果 =====\n');
fprintf('最高车速: %.1f km/h (设计指标: 100 km/h)\n', v_max);
fprintf('0-%dkm/h加速时间: %.1f s\n', params.target.v_test, t_0_target);
fprintf('%dkm/h最大爬坡度: %.1f%%\n', params.target.v_grade, grade(find(v_kmh>=params.target.v_grade,1)));
