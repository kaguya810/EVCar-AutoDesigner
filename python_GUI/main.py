import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

plt.rcParams["font.sans-serif"]=["SimSun"] #设置字体
plt.rcParams["axes.unicode_minus"]=False #正常显示负号

class MotorDesignTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.set_default_values()

    def setup_ui(self):
        main_layout = QHBoxLayout()

        # 左侧参数输入区域
        param_group = QGroupBox("车辆与电机参数")
        param_layout = QFormLayout()

        # 车辆基本参数输入
        self.vehicle_params = {}
        param_layout.addRow(QLabel("<b>车辆基本参数</b>"))
        self.vehicle_params['m'] = QDoubleSpinBox()
        self.vehicle_params['m'].setRange(1000, 10000)
        param_layout.addRow("满载质量 (kg):", self.vehicle_params['m'])

        self.vehicle_params['g'] = QDoubleSpinBox()
        self.vehicle_params['g'].setRange(9.0, 10.0)
        self.vehicle_params['g'].setSingleStep(0.1)
        param_layout.addRow("重力加速度 (m/s²):", self.vehicle_params['g'])

        self.vehicle_params['f'] = QDoubleSpinBox()
        self.vehicle_params['f'].setRange(0.001, 0.1)
        self.vehicle_params['f'].setSingleStep(0.001)
        param_layout.addRow("滚动阻力系数:", self.vehicle_params['f'])

        self.vehicle_params['Cd'] = QDoubleSpinBox()
        self.vehicle_params['Cd'].setRange(0.1, 1.0)
        self.vehicle_params['Cd'].setSingleStep(0.01)
        param_layout.addRow("空气阻力系数:", self.vehicle_params['Cd'])

        self.vehicle_params['A'] = QDoubleSpinBox()
        self.vehicle_params['A'].setRange(1.0, 10.0)
        self.vehicle_params['A'].setSingleStep(0.1)
        param_layout.addRow("迎风面积 (m²):", self.vehicle_params['A'])

        self.vehicle_params['eta_t'] = QDoubleSpinBox()
        self.vehicle_params['eta_t'].setRange(0.5, 1.0)
        self.vehicle_params['eta_t'].setSingleStep(0.01)
        param_layout.addRow("机械传动效率:", self.vehicle_params['eta_t'])

        self.vehicle_params['rho_a'] = QDoubleSpinBox()
        self.vehicle_params['rho_a'].setRange(1.0, 1.5)
        self.vehicle_params['rho_a'].setSingleStep(0.01)
        param_layout.addRow("空气密度 (kg/m³):", self.vehicle_params['rho_a'])

        self.vehicle_params['delta'] = QDoubleSpinBox()
        self.vehicle_params['delta'].setRange(1.0, 1.5)
        self.vehicle_params['delta'].setSingleStep(0.01)
        param_layout.addRow("质量转换系数:", self.vehicle_params['delta'])

        # 性能指标参数输入
        param_layout.addRow(QLabel("<b>性能指标参数</b>"))
        self.vehicle_params['u_max'] = QDoubleSpinBox()
        self.vehicle_params['u_max'].setRange(50, 200)
        self.vehicle_params['u_max'].setSingleStep(5)
        param_layout.addRow("最高车速 (km/h):", self.vehicle_params['u_max'])

        self.vehicle_params['u_p'] = QDoubleSpinBox()
        self.vehicle_params['u_p'].setRange(10, 100)
        self.vehicle_params['u_p'].setSingleStep(5)
        param_layout.addRow("爬坡车速 (km/h):", self.vehicle_params['u_p'])

        self.vehicle_params['alpha_max'] = QDoubleSpinBox()
        self.vehicle_params['alpha_max'].setRange(5, 30)
        self.vehicle_params['alpha_max'].setSingleStep(1)
        param_layout.addRow("最大坡度角 (%):", self.vehicle_params['alpha_max'])

        self.vehicle_params['u_m_kph'] = QDoubleSpinBox()
        self.vehicle_params['u_m_kph'].setRange(30, 100)
        self.vehicle_params['u_m_kph'].setSingleStep(5)
        param_layout.addRow("加速末速 (km/h):", self.vehicle_params['u_m_kph'])

        self.vehicle_params['t_a'] = QDoubleSpinBox()
        self.vehicle_params['t_a'].setRange(1, 30)
        self.vehicle_params['t_a'].setSingleStep(1)
        param_layout.addRow("加速时间 (s):", self.vehicle_params['t_a'])

        # 电机设计参数输入
        param_layout.addRow(QLabel("<b>电机设计参数</b>"))
        self.vehicle_params['n_b'] = QSpinBox()
        self.vehicle_params['n_b'].setRange(1000, 10000)
        self.vehicle_params['n_b'].setSingleStep(100)
        param_layout.addRow("电机额定转速 (rpm):", self.vehicle_params['n_b'])

        self.vehicle_params['n_max_design'] = QSpinBox()
        self.vehicle_params['n_max_design'].setRange(1000, 15000)
        self.vehicle_params['n_max_design'].setSingleStep(100)
        param_layout.addRow("设计最高转速 (rpm):", self.vehicle_params['n_max_design'])

        param_group.setLayout(param_layout)

        # 右侧结果区域
        result_group = QGroupBox("电机选型结果")
        result_layout = QVBoxLayout()

        # 计算结果文本区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)

        # 电机参数输入
        motor_param_group = QGroupBox("电机参数")
        motor_layout = QFormLayout()

        self.motor_params = {}
        self.motor_params['model'] = QComboBox()
        self.motor_params['model'].addItems(['SD290高压版', 'Model S电机', '其他型号'])
        motor_layout.addRow("电机型号:", self.motor_params['model'])

        self.motor_params['P_e'] = QDoubleSpinBox()
        self.motor_params['P_e'].setRange(10, 300)
        motor_layout.addRow("额定功率 (kW):", self.motor_params['P_e'])

        self.motor_params['P_emax'] = QDoubleSpinBox()
        self.motor_params['P_emax'].setRange(20, 500)
        motor_layout.addRow("峰值功率 (kW):", self.motor_params['P_emax'])

        self.motor_params['n_e'] = QSpinBox()
        self.motor_params['n_e'].setRange(1000, 10000)
        motor_layout.addRow("额定转速 (rpm):", self.motor_params['n_e'])

        self.motor_params['n_max'] = QSpinBox()
        self.motor_params['n_max'].setRange(1000, 15000)
        motor_layout.addRow("最高转速 (rpm):", self.motor_params['n_max'])

        self.motor_params['T_max'] = QDoubleSpinBox()
        self.motor_params['T_max'].setRange(100, 1000)
        motor_layout.addRow("峰值转矩 (N·m):", self.motor_params['T_max'])

        self.motor_params['voltage'] = QDoubleSpinBox()
        self.motor_params['voltage'].setRange(100, 1000)
        motor_layout.addRow("电压 (V):", self.motor_params['voltage'])

        motor_param_group.setLayout(motor_layout)

        # 按钮
        self.calculate_btn = QPushButton("计算电机需求")
        self.calculate_btn.clicked.connect(self.calculate)

        # 添加到右侧布局
        result_layout.addWidget(motor_param_group)
        result_layout.addWidget(self.calculate_btn)

        result_group.setLayout(result_layout)

        # 添加左右区域
        main_layout.addWidget(param_group, 1)
        main_layout.addWidget(result_group, 2)

        self.setLayout(main_layout)

    def set_default_values(self):
        # 设置默认值
        self.vehicle_params['m'].setValue(4200)
        self.vehicle_params['g'].setValue(9.8)
        self.vehicle_params['f'].setValue(0.015)
        self.vehicle_params['Cd'].setValue(0.38)
        self.vehicle_params['A'].setValue(3.769)
        self.vehicle_params['eta_t'].setValue(0.92)
        self.vehicle_params['rho_a'].setValue(1.2258)
        self.vehicle_params['delta'].setValue(1.01)
        self.vehicle_params['u_max'].setValue(120)
        self.vehicle_params['u_p'].setValue(30)
        self.vehicle_params['alpha_max'].setValue(20)
        self.vehicle_params['u_m_kph'].setValue(50)
        self.vehicle_params['t_a'].setValue(9)
        self.vehicle_params['n_b'].setValue(2500)
        self.vehicle_params['n_max_design'].setValue(4500)

        # 设置电机默认值
        self.motor_params['model'].setCurrentIndex(0)
        self.motor_params['P_e'].setValue(58.0)
        self.motor_params['P_emax'].setValue(158.0)
        self.motor_params['n_e'].setValue(2500)
        self.motor_params['n_max'].setValue(8000)
        self.motor_params['T_max'].setValue(600.0)
        self.motor_params['voltage'].setValue(650.0)

    def calculate(self):
        # 收集参数
        params = {}
        for key, widget in self.vehicle_params.items():
            if isinstance(widget, QDoubleSpinBox):
                params[key] = widget.value()
            elif isinstance(widget, QSpinBox):
                params[key] = widget.value()

        # 转换角度为弧度
        params['alpha_max'] = np.deg2rad(params['alpha_max'])

        # 计算中间变量
        sin_alpha = np.sin(params['alpha_max'])
        cos_alpha = np.cos(params['alpha_max'])

        # 计算基速车速
        u_b_kmh = (params['u_max'] * params['n_b']) / params['n_max_design']
        u_b = u_b_kmh * (1000 / 3600)

        if (params['u_m_kph'] * (1000 / 3600) < u_b):
            u_b = 0

        # 1. 最高车速功率计算
        rolling_force = params['m'] * params['g'] * params['f']
        air_force_max = (params['Cd'] * params['A'] * params['u_max'] ** 2) / 21.15
        total_force_max = rolling_force + air_force_max
        coeff_p1 = params['u_max'] / (3600 * params['eta_t'])
        P_m1 = coeff_p1 * total_force_max

        # 2. 最大爬坡度功率计算
        grade_force = params['m'] * params['g'] * (params['f'] * cos_alpha + sin_alpha)
        air_force_grade = (params['Cd'] * params['A'] * params['u_p'] ** 2) / 21.15
        total_force_grade = grade_force + air_force_grade
        coeff_p2 = params['u_p'] / (3600 * params['eta_t'])
        P_m2 = coeff_p2 * total_force_grade

        # 3. 加速性能功率计算
        u_m = params['u_m_kph'] * (1000 / 3600)
        rolling_term = (2 / 3) * params['m'] * params['g'] * params['f'] * u_m
        air_term = (params['rho_a'] * params['Cd'] * params['A'] * u_m ** 3) / 5
        accel_term = params['delta'] * params['m'] * (u_m ** 2 + u_b ** 2) / (2 * params['t_a'])
        total_power = rolling_term + air_term + accel_term
        coeff_p3 = 1 / (1000 * params['eta_t'])
        P_m3 = coeff_p3 * total_power

        # 电机功率需求
        P_e_min = P_m1
        P_emax_min = max([P_m1, P_m2, P_m3])

        # 获取电机参数
        motor_model = self.motor_params['model'].currentText()
        motor_values = {key: widget.value() for key, widget in self.motor_params.items() if key != 'model'}

        # 显示结果
        result = f"===== 电机需求功率 =====\n"
        result += f"P_m1 (最高车速): {P_m1:.2f} kW\n"
        result += f"P_m2 (最大爬坡): {P_m2:.2f} kW\n"
        result += f"P_m3 (加速性能): {P_m3:.2f} kW\n"
        result += f"额定功率需求: ≥ {P_e_min:.2f} kW\n"
        result += f"峰值功率需求: ≥ {P_emax_min:.2f} kW\n\n"

        result += f"===== 电机选型结果 =====\n"
        result += f"型号: {motor_model}\n"
        result += f"额定功率: {motor_values['P_e']:.2f} kW\n"
        result += f"峰值功率: {motor_values['P_emax']:.2f} kW\n"
        result += f"额定转速: {motor_values['n_e']:.2f} rpm\n"
        result += f"最高转速: {motor_values['n_max']:.2f} rpm\n"
        result += f"峰值转矩: {motor_values['T_max']:.2f} N·m\n"
        result += f"电压: {motor_values['voltage']:.2f} V\n\n"

        # 检查是否满足需求
        result += f"===== 选型验证 =====\n"
        if motor_values['P_e'] >= P_e_min:
            result += "✓ 额定功率满足需求\n"
        else:
            result += "✗ 额定功率不足！请选择更大功率的电机\n"

        if motor_values['P_emax'] >= P_emax_min:
            result += "✓ 峰值功率满足需求\n"
        else:
            result += "✗ 峰值功率不足！请选择更大功率的电机\n"

        self.result_text.setText(result)


class BatteryDesignTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.set_default_values()

    def setup_ui(self):
        main_layout = QHBoxLayout()

        # 左侧参数输入区域
        param_group = QGroupBox("电池系统参数")
        param_layout = QFormLayout()

        # 电池单体参数
        param_layout.addRow(QLabel("<b>电池单体参数</b>"))
        self.params = {}
        self.params['battery_V_s'] = QDoubleSpinBox()
        self.params['battery_V_s'].setRange(2.0, 5.0)
        self.params['battery_V_s'].setSingleStep(0.1)
        param_layout.addRow("单体电压 (V):", self.params['battery_V_s'])

        self.params['battery_C_s'] = QDoubleSpinBox()
        self.params['battery_C_s'].setRange(1.0, 10.0)
        self.params['battery_C_s'].setSingleStep(0.1)
        param_layout.addRow("单体容量 (Ah):", self.params['battery_C_s'])

        self.params['battery_E_s'] = QDoubleSpinBox()
        self.params['battery_E_s'].setRange(5.0, 50.0)
        self.params['battery_E_s'].setSingleStep(0.5)
        param_layout.addRow("单体能量 (Wh):", self.params['battery_E_s'])

        self.params['battery_m_s'] = QDoubleSpinBox()
        self.params['battery_m_s'].setRange(0.01, 0.5)
        self.params['battery_m_s'].setSingleStep(0.01)
        param_layout.addRow("单体质量 (kg):", self.params['battery_m_s'])

        self.params['battery_model'] = QComboBox()
        self.params['battery_model'].addItems(['亿纬锂能50E 21700', '宁德时代 NMC', '比亚迪 LFP'])
        param_layout.addRow("电池型号:", self.params['battery_model'])

        # 电机参数
        param_layout.addRow(QLabel("<b>电机参数</b>"))
        self.params['motor_U_e'] = QDoubleSpinBox()
        self.params['motor_U_e'].setRange(100, 1000)
        self.params['motor_U_e'].setSingleStep(10)
        param_layout.addRow("电机额定电压 (V):", self.params['motor_U_e'])

        self.params['motor_P_emax'] = QDoubleSpinBox()
        self.params['motor_P_emax'].setRange(50, 500)
        self.params['motor_P_emax'].setSingleStep(10)
        param_layout.addRow("电机峰值功率 (kW):", self.params['motor_P_emax'])

        self.params['motor_eta_e'] = QDoubleSpinBox()
        self.params['motor_eta_e'].setRange(0.7, 0.99)
        self.params['motor_eta_e'].setSingleStep(0.01)
        param_layout.addRow("电机效率:", self.params['motor_eta_e'])

        self.params['motor_eta_ec'] = QDoubleSpinBox()
        self.params['motor_eta_ec'].setRange(0.7, 0.99)
        self.params['motor_eta_ec'].setSingleStep(0.01)
        param_layout.addRow("控制器效率:", self.params['motor_eta_ec'])

        # 车辆参数
        param_layout.addRow(QLabel("<b>车辆参数</b>"))
        self.params['vehicle_S'] = QDoubleSpinBox()
        self.params['vehicle_S'].setRange(100, 1000)
        self.params['vehicle_S'].setSingleStep(10)
        param_layout.addRow("续驶里程 (km):", self.params['vehicle_S'])

        self.params['vehicle_u'] = QDoubleSpinBox()
        self.params['vehicle_u'].setRange(30, 120)
        self.params['vehicle_u'].setSingleStep(5)
        param_layout.addRow("匀速车速 (km/h):", self.params['vehicle_u'])

        self.params['vehicle_m'] = QDoubleSpinBox()
        self.params['vehicle_m'].setRange(1000, 10000)
        self.params['vehicle_m'].setSingleStep(100)
        param_layout.addRow("满载质量 (kg):", self.params['vehicle_m'])

        self.params['vehicle_g'] = QDoubleSpinBox()
        self.params['vehicle_g'].setRange(9.0, 10.0)
        self.params['vehicle_g'].setSingleStep(0.1)
        param_layout.addRow("重力加速度 (m/s²):", self.params['vehicle_g'])

        self.params['vehicle_f'] = QDoubleSpinBox()
        self.params['vehicle_f'].setRange(0.001, 0.1)
        self.params['vehicle_f'].setSingleStep(0.001)
        param_layout.addRow("滚动阻力系数:", self.params['vehicle_f'])

        self.params['vehicle_Cd'] = QDoubleSpinBox()
        self.params['vehicle_Cd'].setRange(0.1, 1.0)
        self.params['vehicle_Cd'].setSingleStep(0.01)
        param_layout.addRow("空气阻力系数:", self.params['vehicle_Cd'])

        self.params['vehicle_A'] = QDoubleSpinBox()
        self.params['vehicle_A'].setRange(1.0, 10.0)
        self.params['vehicle_A'].setSingleStep(0.1)
        param_layout.addRow("迎风面积 (m²):", self.params['vehicle_A'])

        self.params['vehicle_eta_t'] = QDoubleSpinBox()
        self.params['vehicle_eta_t'].setRange(0.5, 1.0)
        self.params['vehicle_eta_t'].setSingleStep(0.01)
        param_layout.addRow("传动效率:", self.params['vehicle_eta_t'])

        # 系统参数
        param_layout.addRow(QLabel("<b>系统参数</b>"))
        self.params['system_DOD'] = QDoubleSpinBox()
        self.params['system_DOD'].setRange(0.5, 1.0)
        self.params['system_DOD'].setSingleStep(0.01)
        param_layout.addRow("放电深度 (DOD):", self.params['system_DOD'])

        param_group.setLayout(param_layout)

        # 右侧结果区域
        result_group = QGroupBox("电池组设计结果")
        result_layout = QVBoxLayout()

        # 计算结果文本区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)

        # 按钮
        self.calculate_btn = QPushButton("计算电池组参数")
        self.calculate_btn.clicked.connect(self.calculate)
        result_layout.addWidget(self.calculate_btn)

        # 添加图表
        fig, self.battery_plot = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvas(fig)
        result_layout.addWidget(self.canvas)

        result_group.setLayout(result_layout)

        # 添加左右区域
        main_layout.addWidget(param_group, 1)
        main_layout.addWidget(result_group, 2)

        self.setLayout(main_layout)

    def set_default_values(self):
        # 设置默认值
        self.params['battery_V_s'].setValue(3.6)
        self.params['battery_C_s'].setValue(5.0)
        self.params['battery_E_s'].setValue(18.25)
        self.params['battery_m_s'].setValue(0.0678)
        self.params['battery_model'].setCurrentIndex(0)

        self.params['motor_U_e'].setValue(650)
        self.params['motor_P_emax'].setValue(100.0)
        self.params['motor_eta_e'].setValue(0.90)
        self.params['motor_eta_ec'].setValue(0.95)

        self.params['vehicle_S'].setValue(200)
        self.params['vehicle_u'].setValue(60)
        self.params['vehicle_m'].setValue(4200)
        self.params['vehicle_g'].setValue(9.8)
        self.params['vehicle_f'].setValue(0.015)
        self.params['vehicle_Cd'].setValue(0.38)
        self.params['vehicle_A'].setValue(3.769)
        self.params['vehicle_eta_t'].setValue(0.92)

        self.params['system_DOD'].setValue(0.90)

    def calculate(self):
        # 收集参数
        p = {}
        for key, widget in self.params.items():
            if isinstance(widget, QDoubleSpinBox):
                p[key] = widget.value()
            elif isinstance(widget, QComboBox):
                p[key] = widget.currentText()

        # 1. 串联数目计算
        n_s = np.ceil(p['motor_U_e'] / p['battery_V_s'])
        U_pack = n_s * p['battery_V_s']

        # 2. 匀速行驶功率计算
        F_f = p['vehicle_m'] * p['vehicle_g'] * p['vehicle_f']
        F_w = (p['vehicle_Cd'] * p['vehicle_A'] * p['vehicle_u'] ** 2) / 21.15
        F_total = F_f + F_w
        P_req = (F_total * p['vehicle_u']) / (3600 * p['vehicle_eta_t'])
        P_batt = P_req / (p['motor_eta_e'] * p['motor_eta_ec'])

        # 3. 续驶里程能量计算
        t = p['vehicle_S'] / p['vehicle_u']
        E_total = P_batt * t * 1000
        E_batt = E_total / p['system_DOD']

        # 4. 并联数目计算 (能量需求)
        n_p_energy = np.ceil(E_batt / (n_s * p['battery_E_s']))

        # 5. 峰值功率校核
        P_s = p['battery_V_s'] * p['battery_C_s'] * 3
        P_bmax = (P_s * n_s * n_p_energy) / 1000
        P_demand = p['motor_P_emax'] / (p['motor_eta_e'] * p['motor_eta_ec'])

        # 功率不满足时重新计算
        if P_bmax < P_demand:
            n_p_power = np.ceil(P_demand * 1000 / (P_s * n_s * p['motor_eta_e'] * p['motor_eta_ec']))
            n_p = max(n_p_energy, n_p_power)
        else:
            n_p = n_p_energy

        # 6. 电池组参数计算
        N_total = n_s * n_p
        C_pack = p['battery_C_s'] * n_p
        E_pack = N_total * p['battery_E_s'] / 1000
        m_pack = N_total * p['battery_m_s']

        # 7. 续驶里程验证
        E_usable = E_pack * 1000 * p['system_DOD']
        t_actual = E_usable / (P_batt * 1000)
        S_actual = p['vehicle_u'] * t_actual

        # 显示结果
        result = f"===== 电池组参数 =====\n"
        result += f"电池型号: {p['battery_model']}\n"
        result += f"串联数目: {int(n_s)} 节\n"
        result += f"并联数目: {int(n_p)} 组\n"
        result += f"总电池数: {int(N_total)} 节\n"
        result += f"总电压: {U_pack:.2f} V\n"
        result += f"总容量: {C_pack:.2f} Ah\n"
        result += f"总能量: {E_pack:.2f} kWh\n"
        result += f"总质量: {m_pack:.2f} kg\n\n"

        result += f"===== 性能验证 =====\n"
        result += f"匀速需求功率: {P_req:.2f} kW\n"
        result += f"电池输出功率: {P_batt:.2f} kW\n"
        result += f"峰值功率需求: {P_demand:.2f} kW\n"
        result += f"电池组输出功率: {(P_s * n_s * n_p) / 1000:.2f} kW\n"

        if S_actual >= p['vehicle_S']:
            result += f"实际续驶里程: {S_actual:.2f} km > {p['vehicle_S']:.0f} km (满足要求)\n"
        else:
            result += f"实际续驶里程: {S_actual:.2f} km < {p['vehicle_S']:.0f} km (不满足要求)\n"

        self.result_text.setText(result)

        # 更新图表
        self.update_plot(n_s, n_p, E_pack, m_pack)

    def update_plot(self, n_s, n_p, E_pack, m_pack):
        # 清除之前的图表
        self.battery_plot.clear()

        # 创建饼图显示电池组成
        sizes = [n_s, n_p]
        labels = [f'串联电池数: {int(n_s)}', f'并联电池组: {int(n_p)}']
        colors = ['#ff9999', '#66b3ff']

        self.battery_plot.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                              startangle=90, shadow=True)
        self.battery_plot.axis('equal')  # 确保饼图是圆的
        self.battery_plot.set_title('电池组组成')

        # 在图表下方添加文本信息
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        textstr = f'总能量: {E_pack:.2f} kWh\n总质量: {m_pack:.2f} kg'
        self.battery_plot.text(0.5, -0.15, textstr, transform=self.battery_plot.transAxes,
                               fontsize=10, verticalalignment='top', horizontalalignment='center',
                               bbox=props)

        # 重绘图表
        self.canvas.draw()


class DrivetrainDesignTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.set_default_values()

    def setup_ui(self):
        main_layout = QHBoxLayout()

        # 左侧参数输入区域
        param_group = QGroupBox("传动系统参数")
        param_layout = QFormLayout()

        # 基础参数
        self.params = {}
        param_layout.addRow(QLabel("<b>基础参数</b>"))
        self.params['m'] = QDoubleSpinBox()
        self.params['m'].setRange(1000, 10000)
        param_layout.addRow("满载质量 (kg):", self.params['m'])

        self.params['g'] = QDoubleSpinBox()
        self.params['g'].setRange(9.0, 10.0)
        self.params['g'].setSingleStep(0.1)
        param_layout.addRow("重力加速度 (m/s²):", self.params['g'])

        self.params['f'] = QDoubleSpinBox()
        self.params['f'].setRange(0.001, 0.1)
        self.params['f'].setSingleStep(0.001)
        param_layout.addRow("滚动阻力系数:", self.params['f'])

        self.params['alpha_max'] = QDoubleSpinBox()
        self.params['alpha_max'].setRange(5, 30)
        self.params['alpha_max'].setSingleStep(1)
        param_layout.addRow("最大坡度角 (%):", self.params['alpha_max'])

        self.params['r'] = QDoubleSpinBox()
        self.params['r'].setRange(0.1, 1.0)
        self.params['r'].setSingleStep(0.01)
        param_layout.addRow("车轮半径 (m):", self.params['r'])

        self.params['T_max'] = QDoubleSpinBox()
        self.params['T_max'].setRange(100, 1000)
        param_layout.addRow("电机峰值转矩 (N·m):", self.params['T_max'])

        self.params['eta_t'] = QDoubleSpinBox()
        self.params['eta_t'].setRange(0.5, 1.0)
        self.params['eta_t'].setSingleStep(0.01)
        param_layout.addRow("传动效率:", self.params['eta_t'])

        self.params['n_max'] = QSpinBox()
        self.params['n_max'].setRange(1000, 15000)
        param_layout.addRow("电机最高转速 (rpm):", self.params['n_max'])

        self.params['u_max'] = QDoubleSpinBox()
        self.params['u_max'].setRange(50, 200)
        param_layout.addRow("最高车速 (km/h):", self.params['u_max'])

        self.params['i_t'] = QDoubleSpinBox()
        self.params['i_t'].setRange(1, 20)
        param_layout.addRow("目标总传动比:", self.params['i_t'])

        self.params['i0'] = QDoubleSpinBox()
        self.params['i0'].setRange(1, 10)
        param_layout.addRow("设计主减速比:", self.params['i0'])

        # 齿轮通用参数
        param_layout.addRow(QLabel("<b>齿轮通用参数</b>"))
        self.params['KA'] = QDoubleSpinBox()
        self.params['KA'].setRange(5, 15)
        param_layout.addRow("中心距系数:", self.params['KA'])

        self.params['eta_g'] = QDoubleSpinBox()
        self.params['eta_g'].setRange(0.5, 1.0)
        self.params['eta_g'].setSingleStep(0.01)
        param_layout.addRow("减速器效率:", self.params['eta_g'])

        self.params['kc'] = QDoubleSpinBox()
        self.params['kc'].setRange(5, 15)
        param_layout.addRow("齿宽系数:", self.params['kc'])

        param_group.setLayout(param_layout)

        # 右侧结果区域
        result_group = QGroupBox("传动系统设计结果")
        result_layout = QVBoxLayout()

        # 计算结果文本区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)

        # 按钮
        self.calculate_btn = QPushButton("计算传动系统参数")
        self.calculate_btn.clicked.connect(self.calculate)
        result_layout.addWidget(self.calculate_btn)

        # 图表区域
        fig, self.gear_plot = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvas(fig)
        result_layout.addWidget(self.canvas)

        result_group.setLayout(result_layout)

        # 添加左右区域
        main_layout.addWidget(param_group, 1)
        main_layout.addWidget(result_group, 2)

        self.setLayout(main_layout)

    def set_default_values(self):
        # 设置默认值
        self.params['m'].setValue(4200)
        self.params['g'].setValue(9.8)
        self.params['f'].setValue(0.015)
        self.params['alpha_max'].setValue(20)
        self.params['r'].setValue(0.364)
        self.params['T_max'].setValue(600)
        self.params['eta_t'].setValue(0.92)
        self.params['n_max'].setValue(8000)
        self.params['u_max'].setValue(120)
        self.params['i_t'].setValue(7.0)
        self.params['i0'].setValue(4.0)
        self.params['KA'].setValue(9.0)
        self.params['eta_g'].setValue(0.96)
        self.params['kc'].setValue(7.0)

    def calculate(self):
        # 收集参数
        p = {}
        for key, widget in self.params.items():
            if isinstance(widget, QDoubleSpinBox):
                p[key] = widget.value()
            elif isinstance(widget, QSpinBox):
                p[key] = widget.value()

        # 转换角度为弧度
        p['alpha_max'] = np.deg2rad(p['alpha_max'])

        # ========== 1. 传动比需求范围计算 ==========
        F_grade = p['m'] * p['g'] * (p['f'] * np.cos(p['alpha_max']) + np.sin(p['alpha_max']))
        i_t_min = (F_grade * p['r']) / (p['T_max'] * p['eta_t'])
        i_t_max = 0.377 * (p['n_max'] * p['r']) / p['u_max']

        # 目标总传动比设定
        ig = p['i_t'] / p['i0']

        # ========== 2. 第一级变速器设计 ==========
        # 辅助函数：中心距标准化
        def round_to_standard(value):
            std_series = list(range(50, 201, 5))  # 50-200的5mm间隔系列
            return min(std_series, key=lambda x: abs(x - value))

        A1 = p['KA'] * (p['T_max'] * ig * p['eta_g']) ** (1 / 3)
        A1 = round_to_standard(A1)

        # 这里简化了齿轮设计计算
        beta_actual1_deg = 25  # 示例值
        z1 = 17
        z2 = int(z1 * ig)
        d1 = 80.0
        d2 = 160.0

        # ========== 3. 第二级主减速器设计 ==========
        beta_actual2_deg = 20  # 示例值
        z3 = 14
        z4 = int(z3 * p['i0'])
        d3 = 60.0
        d4 = 240.0

        # ========== 4. 轴径设计 ==========
        d_in = 4.3 * (p['T_max']) ** (1 / 3)
        d_mid = 0.54 * A1
        d_half = 0.211 * (p['T_max'] * 1000) ** (1 / 3)

        # ========== 5. 结果输出 ==========
        result = "======== 传动系统设计结果 ========\n"
        result += f"实际总传动比: {ig * p['i0']:.2f}\n"
        result += f"需求范围: {i_t_min:.2f} - {i_t_max:.2f}\n"
        result += f"设计主减速比 i0: {p['i0']:.2f}\n"
        result += f"设计变速器传动比 ig: {ig:.2f}\n\n"

        result += "===== 第一级变速器设计 =====\n"
        result += f"中心距: {A1} mm\n"
        result += f"小齿轮齿数: {z1}\n"
        result += f"大齿轮齿数: {z2}\n"
        result += f"螺旋角: {beta_actual1_deg:.2f}°\n"
        result += f"小齿轮分度圆直径: {d1:.2f} mm\n"
        result += f"大齿轮分度圆直径: {d2:.2f} mm\n\n"

        result += "===== 第二级主减速器设计 =====\n"
        result += f"小齿轮齿数: {z3}\n"
        result += f"大齿轮齿数: {z4}\n"
        result += f"螺旋角: {beta_actual2_deg:.2f}°\n"
        result += f"小齿轮分度圆直径: {d3:.2f} mm\n"
        result += f"大齿轮分度圆直径: {d4:.2f} mm\n\n"

        result += "===== 轴径设计 =====\n"
        result += f"输入轴直径: {d_in:.2f} mm\n"
        result += f"中间轴直径: {d_mid:.2f} mm\n"
        result += f"半轴直径: {d_half:.2f} mm\n"

        self.result_text.setText(result)

        # 更新图表
        self.update_plot(d1, d2, d3, d4)

    def update_plot(self, d1, d2, d3, d4):
        # 清除之前的图表
        for ax in self.gear_plot:
            ax.clear()

        # 第一级变速器齿轮图示
        self.plot_gear(self.gear_plot[0], d1, d2, "第一级变速器")

        # 第二级主减速器齿轮图示
        self.plot_gear(self.gear_plot[1], d3, d4, "第二级主减速器")

        # 重绘图表
        self.canvas.draw()

    def plot_gear(self, ax, d1, d2, title):
        # 绘制两个齿轮
        circle1 = plt.Circle((0, 0), d1 / 2, fill=False, edgecolor='blue', linewidth=2)
        circle2 = plt.Circle(((d1 + d2) / 2, 0), d2 / 2, fill=False, edgecolor='red', linewidth=2)
        ax.add_patch(circle1)
        ax.add_patch(circle2)

        # 添加齿形示意
        ax.plot([0, d1 / 2], [0, d1 / 2], 'b-')
        ax.plot([(d1 + d2) / 2, (d1 + d2) / 2 + d2 / 2], [0, d2 / 2], 'r-')

        ax.set_title(title)
        ax.set_aspect('equal', 'box')
        ax.set_xlim(-d1 / 2 - 10, (d1 + d2) / 2 + d2 / 2 + 10)
        ax.set_ylim(-max(d1, d2) / 2 - 10, max(d1, d2) / 2 + 10)
        ax.grid(True)
        ax.set_xticks([])
        ax.set_yticks([])


class PerformanceAnalysisTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.set_default_values()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # 参数输入区域
        param_group = QGroupBox("性能分析参数")
        param_layout = QHBoxLayout()

        # 车辆参数列
        vehicle_group = QGroupBox("车辆参数")
        vehicle_layout = QFormLayout()
        self.vehicle_params = {}

        self.vehicle_params['m'] = QDoubleSpinBox()
        self.vehicle_params['m'].setRange(1000, 10000)
        vehicle_layout.addRow("满载质量 (kg):", self.vehicle_params['m'])

        self.vehicle_params['g'] = QDoubleSpinBox()
        self.vehicle_params['g'].setRange(9.0, 10.0)
        self.vehicle_params['g'].setSingleStep(0.1)
        vehicle_layout.addRow("重力加速度 (m/s²):", self.vehicle_params['g'])

        self.vehicle_params['f'] = QDoubleSpinBox()
        self.vehicle_params['f'].setRange(0.001, 0.1)
        self.vehicle_params['f'].setSingleStep(0.001)
        vehicle_layout.addRow("滚动阻力系数:", self.vehicle_params['f'])

        self.vehicle_params['Cd'] = QDoubleSpinBox()
        self.vehicle_params['Cd'].setRange(0.1, 1.0)
        self.vehicle_params['Cd'].setSingleStep(0.01)
        vehicle_layout.addRow("风阻系数:", self.vehicle_params['Cd'])

        self.vehicle_params['A'] = QDoubleSpinBox()
        self.vehicle_params['A'].setRange(1.0, 10.0)
        self.vehicle_params['A'].setSingleStep(0.1)
        vehicle_layout.addRow("迎风面积 (m²):", self.vehicle_params['A'])

        self.vehicle_params['eta_t'] = QDoubleSpinBox()
        self.vehicle_params['eta_t'].setRange(0.5, 1.0)
        self.vehicle_params['eta_t'].setSingleStep(0.01)
        vehicle_layout.addRow("传动效率:", self.vehicle_params['eta_t'])

        self.vehicle_params['r'] = QDoubleSpinBox()
        self.vehicle_params['r'].setRange(0.1, 1.0)
        self.vehicle_params['r'].setSingleStep(0.001)
        vehicle_layout.addRow("车轮半径 (m):", self.vehicle_params['r'])

        self.vehicle_params['delta'] = QDoubleSpinBox()
        self.vehicle_params['delta'].setRange(1.0, 1.5)
        self.vehicle_params['delta'].setSingleStep(0.01)
        vehicle_layout.addRow("质量转换系数:", self.vehicle_params['delta'])

        vehicle_group.setLayout(vehicle_layout)

        # 电机参数列
        motor_group = QGroupBox("电机参数")
        motor_layout = QFormLayout()
        self.motor_params = {}

        self.motor_params['T_max'] = QDoubleSpinBox()
        self.motor_params['T_max'].setRange(100, 1000)
        motor_layout.addRow("峰值转矩 (N·m):", self.motor_params['T_max'])

        self.motor_params['P_max'] = QDoubleSpinBox()
        self.motor_params['P_max'].setRange(50, 500)
        motor_layout.addRow("峰值功率 (kW):", self.motor_params['P_max'])

        self.motor_params['n_e'] = QSpinBox()
        self.motor_params['n_e'].setRange(1000, 10000)
        motor_layout.addRow("额定转速 (rpm):", self.motor_params['n_e'])

        self.motor_params['n_max'] = QSpinBox()
        self.motor_params['n_max'].setRange(1000, 15000)
        motor_layout.addRow("最高转速 (rpm):", self.motor_params['n_max'])

        motor_group.setLayout(motor_layout)

        # 传动系统参数列
        drivetrain_group = QGroupBox("传动系统参数")
        drivetrain_layout = QFormLayout()
        self.drivetrain_params = {}

        self.drivetrain_params['i_t'] = QDoubleSpinBox()
        self.drivetrain_params['i_t'].setRange(1, 20)
        self.drivetrain_params['i_t'].setSingleStep(0.01)
        drivetrain_layout.addRow("总传动比:", self.drivetrain_params['i_t'])

        self.drivetrain_params['v_test'] = QDoubleSpinBox()
        self.drivetrain_params['v_test'].setRange(30, 100)
        drivetrain_layout.addRow("加速测试车速 (km/h):", self.drivetrain_params['v_test'])

        self.drivetrain_params['v_grade'] = QDoubleSpinBox()
        self.drivetrain_params['v_grade'].setRange(10, 60)
        drivetrain_layout.addRow("爬坡测试车速 (km/h):", self.drivetrain_params['v_grade'])

        drivetrain_group.setLayout(drivetrain_layout)

        # 添加参数组
        param_layout.addWidget(vehicle_group)
        param_layout.addWidget(motor_group)
        param_layout.addWidget(drivetrain_group)
        param_group.setLayout(param_layout)

        # 分析按钮
        self.analyze_btn = QPushButton("分析车辆性能")
        self.analyze_btn.clicked.connect(self.analyze)

        # 图表区域
        self.fig, self.ax = plt.subplots(2, 2, figsize=(12, 10))
        self.canvas = FigureCanvas(self.fig)

        # 结果文本区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        # 添加组件
        main_layout.addWidget(param_group)
        main_layout.addWidget(self.analyze_btn)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(self.result_text)

        self.setLayout(main_layout)

    def set_default_values(self):
        # 设置车辆参数默认值
        self.vehicle_params['m'].setValue(4200)
        self.vehicle_params['g'].setValue(9.8)
        self.vehicle_params['f'].setValue(0.015)
        self.vehicle_params['Cd'].setValue(0.38)
        self.vehicle_params['A'].setValue(3.769)
        self.vehicle_params['eta_t'].setValue(0.92)
        self.vehicle_params['r'].setValue(0.364)
        self.vehicle_params['delta'].setValue(1.01)

        # 设置电机参数默认值
        self.motor_params['T_max'].setValue(600)
        self.motor_params['P_max'].setValue(156)
        self.motor_params['n_e'].setValue(2500)
        self.motor_params['n_max'].setValue(8000)

        # 设置传动系统参数默认值
        self.drivetrain_params['i_t'].setValue(7.11)
        self.drivetrain_params['v_test'].setValue(50)
        self.drivetrain_params['v_grade'].setValue(30)

    def analyze(self):
        # 收集参数
        params = {}
        for group in [self.vehicle_params, self.motor_params, self.drivetrain_params]:
            for key, widget in group.items():
                if isinstance(widget, QDoubleSpinBox):
                    params[key] = widget.value()
                elif isinstance(widget, QSpinBox):
                    params[key] = widget.value()

        # ==================== 行驶阻力计算 ====================
        v_kmh = np.linspace(0, 150, 1000)

        # 行驶阻力计算 (N)
        F_roll = params['m'] * params['g'] * params['f'] * np.ones_like(v_kmh)
        F_air = (params['Cd'] * params['A'] * v_kmh ** 2) / 21.15
        F_res = F_roll + F_air

        # ==================== 电机驱动力计算 ====================
        n = (v_kmh * params['i_t']) / (0.377 * params['r'])

        T_motor = np.zeros_like(n)
        for i in range(len(n)):
            if n[i] <= params['n_e']:
                T_motor[i] = params['T_max']  # 恒转矩区
            elif n[i] <= params['n_max']:
                # 恒功率区
                T_motor[i] = (params['P_max'] * 1000) / (2 * np.pi * n[i] / 60)
            else:
                T_motor[i] = 0

        # 驱动力计算 (N)
        F_drive = (T_motor * params['i_t'] * params['eta_t']) / params['r']

        # ==================== 最高车速分析 ====================
        diff = F_drive - F_res
        idx_max = np.where(diff >= 0)[0][-1]
        v_max = v_kmh[idx_max]

        # ==================== 爬坡度分析 ====================
        def calculate_grade(F_drive, F_res, F_roll, params):
            F_available = F_drive - F_res + F_roll
            sin_alpha = F_available / (params['m'] * params['g'])
            sin_alpha = np.clip(sin_alpha, 0, 0.5)
            return sin_alpha * 100

        grade = calculate_grade(F_drive, F_res, F_roll, params)

        # ==================== 加速性能分析 ====================
        a = (F_drive - F_res) / (params['delta'] * params['m'])
        v_mps = v_kmh / 3.6
        idx_target = np.argmin(np.abs(v_kmh - params['v_test']))
        dt = (v_mps[1] - v_mps[0]) / a[:idx_target]
        t_acc = np.cumsum(dt)
        t_0_target = t_acc[-1]

        # ==================== 绘图 ====================
        self.plot_performance(v_kmh, F_drive, F_roll, F_air, F_res, v_max,
                              grade, params['v_grade'],
                              a, t_acc, t_0_target, params['v_test'],
                              n, T_motor, params)

        # 性能分析结果输出
        result = "===== 车辆性能分析结果 =====\n"
        result += f"最高车速: {v_max:.1f} km/h\n"
        result += f"0-{params['v_test']}km/h加速时间: {t_0_target:.1f} s\n"

        grade_value = grade[np.argmin(np.abs(v_kmh - params['v_grade']))]
        result += f"{params['v_grade']}km/h最大爬坡度: {grade_value:.1f}%\n"

        self.result_text.setText(result)

    def plot_performance(self, v_kmh, F_drive, F_roll, F_air, F_res, v_max,
                         grade, v_grade, a, t_acc, t_0_target, v_test,
                         n, T_motor, params):
        # 清除之前的图表
        for ax_row in self.ax:
            for ax in ax_row:
                ax.clear()

        # 1. 驱动力-阻力平衡图 (左上)
        ax = self.ax[0][0]
        ax.plot(v_kmh, F_drive, 'k-', linewidth=1.5, label='电机驱动力')
        ax.plot(v_kmh, F_roll, color='#666666', linestyle=':', linewidth=1.5, label='滚动阻力')
        ax.plot(v_kmh, F_air, color='#999999', linestyle='-.', linewidth=1.5, label='空气阻力')
        ax.plot(v_kmh, F_res, color='#333333', linestyle='--', linewidth=1.5, label='总行驶阻力')
        ax.axvline(x=v_max, color='k', linestyle=':', linewidth=1.5)
        ax.text(v_max - 46, max(F_drive) * 0.3, f'最高车速: {v_max:.1f} km/h', fontsize=10)
        ax.set_xlabel('车速 (km/h)')
        ax.set_ylabel('力 (N)')
        ax.set_title('(a) 驱动力-阻力平衡图')
        ax.legend()
        ax.grid(True)
        ax.set_xlim(0, max(v_kmh))
        ax.set_ylim(0, max(F_drive) * 1.1)

        # 2. 车速-爬坡度曲线 (右上)
        ax = self.ax[0][1]
        ax.plot(v_kmh, grade, 'k-o', markersize=3, linewidth=1.5)
        ax.axvline(x=v_grade, color='k', linestyle=':', linewidth=1.5)
        ax.axhline(y=20, color='k', linestyle='-.', linewidth=1.5)

        idx_grade = np.argmin(np.abs(v_kmh - v_grade))
        actual_grade = grade[idx_grade]
        ax.text(64, 22, f'设计要求: 20%@{v_grade}km/h', fontsize=10)
        ax.text(32, 28, f'实际值: {actual_grade:.1f}%', fontsize=10)

        ax.set_xlabel('车速 (km/h)')
        ax.set_ylabel('爬坡度 (%)')
        ax.set_title('(b) 车速-爬坡度性能曲线')
        ax.grid(True)
        ax.set_xlim(0, max(v_kmh))
        ax.set_ylim(0, min(max(grade) * 1.2, 50))

        # 3. 车速-加速度曲线 (左下)
        ax = self.ax[1][0]
        ax2 = ax.twinx()

        ax.plot(v_kmh[:len(a)], a, 'k-', linewidth=1.5, label='加速度')
        ax2.plot(v_kmh[:len(t_acc)], t_acc, color='#666666', linestyle='--', linewidth=1.5, label='加速时间')

        ax.set_xlabel('车速 (km/h)')
        ax.set_ylabel('加速度 (m/s²)')
        ax2.set_ylabel('加速时间 (s)')
        ax.set_title('(c) 车速-加速度性能曲线')
        ax.grid(True)

        # 组合图例
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc='upper right')

        ax.set_xlim(0, 100)

        # 4. 电机转矩-转速特性 (右下)
        ax = self.ax[1][1]
        ax.plot(n, T_motor, 'k-+', linewidth=1.5)
        ax.axvline(x=params['n_e'], color='k', linestyle=':', linewidth=1.5)
        ax.text(400, params['T_max'] * 0.8, f'额定转速: {params["n_e"]} rpm', fontsize=10)
        ax.axvline(x=params['n_max'], color='k', linestyle='-.', linewidth=1.5)
        ax.text(5900, params['T_max'] * 0.28, f'最高转速: {params["n_max"]} rpm', fontsize=10)
        ax.set_xlabel('电机转速 (rpm)')
        ax.set_ylabel('电机转矩 (N·m)')
        ax.set_title('(d) 电机转矩-转速特性')
        ax.grid(True)
        ax.set_ylim(0, params['T_max'] * 1.1)

        # 调整布局
        self.fig.tight_layout()

        # 重绘图表
        self.canvas.draw()


class RangeAnalysisTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.set_default_values()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # 参数输入区域
        param_group = QGroupBox("续驶里程分析参数")
        param_layout = QFormLayout()

        # 基础固定参数
        self.params = {}
        self.params['u_a'] = QDoubleSpinBox()
        self.params['u_a'].setRange(30, 120)
        self.params['u_a'].setSingleStep(5)
        param_layout.addRow("巡航车速 (km/h):", self.params['u_a'])

        self.params['eta_t'] = QDoubleSpinBox()
        self.params['eta_t'].setRange(0.5, 1.0)
        self.params['eta_t'].setSingleStep(0.01)
        param_layout.addRow("传动效率:", self.params['eta_t'])

        self.params['eta_e'] = QDoubleSpinBox()
        self.params['eta_e'].setRange(0.5, 1.0)
        self.params['eta_e'].setSingleStep(0.01)
        param_layout.addRow("电机效率:", self.params['eta_e'])

        self.params['g'] = QDoubleSpinBox()
        self.params['g'].setRange(9.0, 10.0)
        self.params['g'].setSingleStep(0.1)
        param_layout.addRow("重力加速度 (m/s²):", self.params['g'])

        self.params['W0'] = QDoubleSpinBox()
        self.params['W0'].setRange(10, 200)
        self.params['W0'].setSingleStep(5)
        param_layout.addRow("电池总能量 (kWh):", self.params['W0'])

        # 基准参数
        param_layout.addRow(QLabel("<b>基准参数</b>"))
        self.params['m_base'] = QDoubleSpinBox()
        self.params['m_base'].setRange(1000, 10000)
        param_layout.addRow("满载质量 (kg):", self.params['m_base'])

        self.params['m_norm'] = QDoubleSpinBox()
        self.params['m_norm'].setRange(1000, 10000)
        param_layout.addRow("整备质量 (kg):", self.params['m_norm'])

        self.params['f_base'] = QDoubleSpinBox()
        self.params['f_base'].setRange(0.001, 0.1)
        self.params['f_base'].setSingleStep(0.001)
        param_layout.addRow("滚动阻力系数:", self.params['f_base'])

        self.params['Cd_base'] = QDoubleSpinBox()
        self.params['Cd_base'].setRange(0.1, 1.0)
        self.params['Cd_base'].setSingleStep(0.01)
        param_layout.addRow("空气阻力系数:", self.params['Cd_base'])

        self.params['A_base'] = QDoubleSpinBox()
        self.params['A_base'].setRange(1.0, 10.0)
        self.params['A_base'].setSingleStep(0.1)
        param_layout.addRow("迎风面积 (m²):", self.params['A_base'])

        param_group.setLayout(param_layout)

        # 分析按钮
        self.analyze_btn = QPushButton("分析续驶里程影响因素")
        self.analyze_btn.clicked.connect(self.analyze)

        # 图表区域
        self.fig, self.ax = plt.subplots(2, 2, figsize=(12, 10))
        self.canvas = FigureCanvas(self.fig)

        # 结果文本区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        # 添加组件
        main_layout.addWidget(param_group)
        main_layout.addWidget(self.analyze_btn)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(self.result_text)

        self.setLayout(main_layout)

    def set_default_values(self):
        # 设置默认值
        self.params['u_a'].setValue(60)
        self.params['eta_t'].setValue(0.92)
        self.params['eta_e'].setValue(0.92)
        self.params['g'].setValue(9.8)
        self.params['W0'].setValue(68.74)
        self.params['m_base'].setValue(4250)
        self.params['m_norm'].setValue(2980)
        self.params['f_base'].setValue(0.015)
        self.params['Cd_base'].setValue(0.38)
        self.params['A_base'].setValue(3.769)

    def calculate_range(self, params, m=None, f=None, Cd=None, A=None):
        # 使用默认值或指定值
        u_a = params['u_a']
        eta_e = params['eta_e']
        eta_t = params['eta_t']
        g = params['g']
        W0 = params['W0']

        m_val = m if m is not None else params['m_base']
        f_val = f if f is not None else params['f_base']
        Cd_val = Cd if Cd is not None else params['Cd_base']
        A_val = A if A is not None else params['A_base']

        # 行驶阻力功率计算 (kW)
        rolling_term = m_val * g * f_val
        air_term = (Cd_val * A_val * u_a ** 2) / 21.15
        P = (u_a / (3600 * eta_t)) * (rolling_term + air_term)

        # 续航里程计算 (km)
        return (W0 * u_a / P) * eta_e

    def analyze(self):
        # 收集参数
        params = {}
        for key, widget in self.params.items():
            if isinstance(widget, QDoubleSpinBox):
                params[key] = widget.value()

        # 分析范围参数
        m_range = np.linspace(params['m_norm'], params['m_base'], 100)
        f_range = np.linspace(0.008, 0.018, 100)
        Cd_range = np.linspace(0.25, 0.45, 100)
        A_range = np.linspace(1.5, 3.5, 100)

        # 计算所有影响因素
        S_m = np.array([self.calculate_range(params, m=m) for m in m_range])
        eta_norm = 0.85  # 整备质量时的效率
        slope_eta = (params['eta_e'] - eta_norm) / (params['m_base'] - params['m_norm'])
        eta_e_range = slope_eta * (m_range - params['m_norm']) + eta_norm

        S_f = np.array([self.calculate_range(params, f=f) for f in f_range])
        S_Cd = np.array([self.calculate_range(params, Cd=Cd) for Cd in Cd_range])
        S_A = np.array([self.calculate_range(params, A=A) for A in A_range])

        # 绘图
        self.plot_influence(m_range, S_m, eta_e_range,
                            f_range, S_f,
                            Cd_range, S_Cd,
                            A_range, S_A)

        # 性能影响量化分析
        S_base = self.calculate_range(params)
        m_test = 1600
        S_new = self.calculate_range(params, m=m_test)
        m_change = (S_new - S_base) / S_base * 100

        f_test = 0.016
        S_new = self.calculate_range(params, f=f_test)
        f_change = (S_new - S_base) / S_base * 100

        Cd_test = 0.35
        S_new = self.calculate_range(params, Cd=Cd_test)
        Cd_change = (S_new - S_base) / S_base * 100

        A_test = 2.5
        S_new = self.calculate_range(params, A=A_test)
        A_change = (S_new - S_base) / S_base * 100

        result = "===== 参数变化对续航里程的影响 =====\n"
        result += "参数变化\t\t基准续航(km)\t新续航(km)\t变化率(%)\n"
        result += f"质量 {params['m_base']:.0f} → {m_test:.0f} kg\t{S_base:.1f}\t\t{S_new:.1f}\t\t{m_change:+.1f}\n"

        S_new = self.calculate_range(params, f=f_test)
        result += f"阻力 {params['f_base']:.3f} → {f_test:.3f}\t{S_base:.1f}\t\t{S_new:.1f}\t\t{f_change:+.1f}\n"

        S_new = self.calculate_range(params, Cd=Cd_test)
        result += f"风阻 {params['Cd_base']:.2f} → {Cd_test:.2f}\t{S_base:.1f}\t\t{S_new:.1f}\t\t{Cd_change:+.1f}\n"

        S_new = self.calculate_range(params, A=A_test)
        result += f"面积 {params['A_base']:.1f} → {A_test:.1f} m²\t{S_base:.1f}\t\t{S_new:.1f}\t\t{A_change:+.1f}\n"

        self.result_text.setText(result)

        # 重绘图表
        self.canvas.draw()

    def plot_influence(self, m_range, S_m, eta_e_range,
                       f_range, S_f,
                       Cd_range, S_Cd,
                       A_range, S_A):
        # 清除之前的图表
        for ax_row in self.ax:
            for ax in ax_row:
                ax.clear()

        # 1. 整车质量影响 (左上)
        ax = self.ax[0][0]
        ax2 = ax.twinx()

        ax.plot(m_range, S_m, 'k-', linewidth=2)
        ax2.plot(m_range, eta_e_range * 100, color='#666666', linestyle='-.', linewidth=2)

        ax.set_xlabel('整车质量 (kg)')
        ax.set_ylabel('续航里程 (km)', color='k')
        ax2.set_ylabel('电机效率 (%)', color='#666666')
        ax.set_title('(a) 整车质量影响')
        ax.grid(True)

        # 2. 滚动阻力影响 (右上)
        ax = self.ax[0][1]
        ax.plot(f_range * 1000, S_f, 'k--', linewidth=2)
        ax.set_xlabel('滚动阻力系数 (×10^{-3})')
        ax.set_ylabel('续航里程 (km)')
        ax.set_title('(b) 滚动阻力影响')
        ax.grid(True)

        # 3. 空气阻力影响 (左下)
        ax = self.ax[1][0]
        ax.plot(Cd_range, S_Cd, color='#333333', linestyle=':', linewidth=2)
        ax.set_xlabel('空气阻力系数 (C_d)')
        ax.set_ylabel('续航里程 (km)')
        ax.set_title('(c) 空气阻力系数影响')
        ax.grid(True)

        # 4. 迎风面积影响 (右下)
        ax = self.ax[1][1]
        ax.plot(A_range, S_A, color='#999999', linewidth=2)
        ax.set_xlabel('迎风面积 (m²)')
        ax.set_ylabel('续航里程 (km)')
        ax.set_title('(d) 迎风面积影响')
        ax.grid(True)

        # 调整布局
        self.fig.tight_layout()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("新能源汽车动力系统设计软件")
        self.setGeometry(100, 70, 800, 1300)
        self.setWindowIcon(QIcon('app_icon.ico'))

        # 创建选项卡
        self.tabs = QTabWidget()
        self.tabs.addTab(MotorDesignTab(), "电机选型设计")
        self.tabs.addTab(BatteryDesignTab(), "电池系统设计")
        self.tabs.addTab(DrivetrainDesignTab(), "传动系统设计")
        self.tabs.addTab(PerformanceAnalysisTab(), "动力性能分析")
        self.tabs.addTab(RangeAnalysisTab(), "续驶里程分析")

        # 添加状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")

        # 设置中央部件
        self.setCentralWidget(self.tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('app_icon.ico'))
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
