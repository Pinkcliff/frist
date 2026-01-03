# -*- coding: utf-8 -*-
"""
Modbus风扇控制器

基于Modbus RTU协议的风扇速度控制实现
"""

import socket
import time
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from .config import FanConfig


def setup_fan_logger(log_file: str = None) -> logging.Logger:
    """
    设置风扇控制日志记录器

    Args:
        log_file: 日志文件路径，如果为None则使用默认路径

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger('FanController')
    logger.setLevel(logging.DEBUG)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 默认日志文件路径
    if log_file is None:
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'fan_control_{timestamp}.log')

    # 文件handler - 详细日志
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # 控制台handler - 重要信息
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # 添加handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 记录日志文件位置
    logger.info(f'='*80)
    logger.info(f'风扇控制日志文件: {log_file}')
    logger.info(f'='*80)

    return logger


# 全局日志记录器
_fan_logger = None


def get_fan_logger() -> logging.Logger:
    """获取风扇控制日志记录器"""
    global _fan_logger
    if _fan_logger is None:
        _fan_logger = setup_fan_logger()
    return _fan_logger


class ModbusCRC:
    """Modbus CRC校验计算"""

    @staticmethod
    def calculate(data: List[int]) -> List[int]:
        """计算Modbus CRC校验码"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return [crc & 0xFF, (crc >> 8) & 0xFF]


class ModbusFanController:
    """Modbus风扇控制器

    提供风扇速度控制功能，支持单风扇和多风扇控制
    """

    def __init__(self, config: Optional[FanConfig] = None, enable_logging: bool = True):
        """
        初始化风扇控制器

        Args:
            config: 风扇配置，如果为None则使用默认配置
            enable_logging: 是否启用日志记录
        """
        self.config = config or FanConfig()
        self.sock: Optional[socket.socket] = None
        self.is_connected = False
        self.enable_logging = enable_logging

        # 获取日志记录器
        self.logger = get_fan_logger() if enable_logging else None

        # 统计信息
        self.stats = {
            'total_commands': 0,
            'success_commands': 0,
            'failed_commands': 0,
            'connection_errors': 0,
        }

        # 记录初始化
        if self.logger:
            self.logger.info('='*80)
            self.logger.info('ModbusFanController 初始化')
            self.logger.info(f'设备IP: {self.config.device_ip}:{self.config.device_port}')
            self.logger.info(f'风扇数量: {self.config.fan_count}')
            self.logger.info(f'从站地址: {self.config.slave_addr}')
            self.logger.info(f'寄存器起始: 0x{self.config.start_register:04X}')
            self.logger.info('='*80)

    def connect(self) -> bool:
        """
        连接到风扇控制器

        Returns:
            bool: 连接成功返回True，失败返回False
        """
        if self.logger:
            self.logger.info('-'*80)
            self.logger.info(f'尝试连接到风扇控制器: {self.config.device_ip}:{self.config.device_port}')

        try:
            # 关闭原有连接
            if self.sock:
                try:
                    self.sock.close()
                    if self.logger:
                        self.logger.debug('关闭原有连接')
                except:
                    pass

            # 创建新连接
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.config.timeout)
            self.sock.connect((self.config.device_ip, self.config.device_port))
            self.is_connected = True

            print(f"[OK] 成功连接到风扇控制器: {self.config.device_ip}:{self.config.device_port}")
            if self.logger:
                self.logger.info(f'[OK] 连接成功')
                self.logger.debug(f'Socket: {self.sock}')

            return True

        except ConnectionRefusedError as e:
            print(f"[ERROR] 连接失败: 设备拒绝连接（IP/端口错误或设备离线）")
            if self.logger:
                self.logger.error(f'连接被拒绝: {e}')
        except TimeoutError as e:
            print(f"[ERROR] 连接失败: 连接超时")
            if self.logger:
                self.logger.error(f'连接超时: {e}')
        except OSError as e:
            print(f"[ERROR] 连接失败: 网络错误 - {str(e)}")
            if self.logger:
                self.logger.error(f'网络错误: {e}')
        except Exception as e:
            print(f"[ERROR] 连接失败: 未知错误 - {str(e)}")
            if self.logger:
                self.logger.error(f'未知错误: {type(e).__name__}: {e}')

        self.is_connected = False
        self.stats['connection_errors'] += 1
        return False

    def disconnect(self):
        """断开连接"""
        if self.logger:
            self.logger.info('断开连接')

        if self.sock:
            try:
                self.sock.close()
                print(f"[DISCONNECT] 已断开连接")
                if self.logger:
                    self.logger.debug('Socket已关闭')
            except:
                pass
            finally:
                self.sock = None
                self.is_connected = False

    def _build_write_request(self, register_addr: int, value: int, func_code: int = 0x06) -> bytes:
        """
        构建写单个寄存器请求帧

        Args:
            register_addr: 寄存器地址
            value: 写入值
            func_code: 功能码（默认0x06写单个寄存器）

        Returns:
            bytes: 完整的Modbus RTU请求帧
        """
        frame = [
            self.config.slave_addr,
            func_code,
            (register_addr >> 8) & 0xFF,
            register_addr & 0xFF,
            (value >> 8) & 0xFF,
            value & 0xFF
        ]
        crc = ModbusCRC.calculate(frame)
        frame.extend(crc)
        return bytearray(frame)

    def _build_write_multiple_request(self, start_addr: int, values: List[int]) -> bytes:
        """
        构建写多个寄存器请求帧（功能码0x10）

        Args:
            start_addr: 起始寄存器地址
            values: 写入值列表

        Returns:
            bytes: 完整的Modbus RTU请求帧
        """
        reg_count = len(values)
        byte_count = reg_count * 2

        frame = [
            self.config.slave_addr,
            self.config.func_code_write_multiple,  # 0x10
            (start_addr >> 8) & 0xFF,
            start_addr & 0xFF,
            (reg_count >> 8) & 0xFF,
            reg_count & 0xFF,
            byte_count
        ]

        # 添加数据
        for value in values:
            frame.extend([
                (value >> 8) & 0xFF,
                value & 0xFF
            ])

        crc = ModbusCRC.calculate(frame)
        frame.extend(crc)
        return bytearray(frame)

    def _parse_response(self, response_bytes: bytes) -> Dict:
        """
        解析Modbus响应帧

        Args:
            response_bytes: 响应字节数据

        Returns:
            Dict: 解析结果，包含valid或error
        """
        response = list(response_bytes)

        if len(response) < 5:
            return {"error": "响应帧过短", "valid": False}

        # 提取CRC并验证
        received_crc = response[-2:]
        calculated_crc = ModbusCRC.calculate(response[:-2])

        if received_crc != calculated_crc:
            return {"error": f"CRC校验失败", "valid": False}

        slave_addr = response[0]
        func_code = response[1]

        # 检查异常响应
        if func_code & 0x80:
            exception_code = response[2]
            error_messages = {
                0x01: "非法功能码",
                0x02: "非法数据地址",
                0x03: "非法数据值",
                0x04: "从站设备故障",
            }
            return {
                "error": error_messages.get(exception_code, f"未知错误（代码: 0x{exception_code:02X}）"),
                "valid": False
            }

        return {
            "slave_addr": slave_addr,
            "func_code": func_code,
            "valid": True
        }

    def _send_command(self, request: bytes) -> Dict:
        """
        发送命令并接收响应

        Args:
            request: 请求数据

        Returns:
            Dict: 响应结果
        """
        if not self.is_connected or not self.sock:
            return {"error": "未连接", "valid": False}

        try:
            # 发送请求
            self.sock.sendall(request)

            # 接收响应
            response_bytes = b""
            start_time = time.time()

            while True:
                chunk = self.sock.recv(1024)
                if chunk:
                    response_bytes += chunk

                    # 写单个寄存器响应固定8字节
                    if len(response_bytes) >= 8:
                        break

                # 超时判断
                if time.time() - start_time > self.config.timeout:
                    return {"error": "接收超时", "valid": False}
                time.sleep(0.01)

            # 解析响应
            return self._parse_response(response_bytes)

        except socket.timeout:
            return {"error": "通信超时", "valid": False}
        except ConnectionResetError:
            self.is_connected = False
            return {"error": "连接被重置", "valid": False}
        except OSError as e:
            self.is_connected = False
            return {"error": f"网络错误: {str(e)}", "valid": False}
        except Exception as e:
            return {"error": f"未知错误: {str(e)}", "valid": False}

    def set_fan_speed(self, fan_index: int, speed_percent: float) -> bool:
        """
        设置单个风扇速度

        Args:
            fan_index: 风扇索引（0-based）
            speed_percent: 速度百分比（0.0-100.0）

        Returns:
            bool: 成功返回True，失败返回False
        """
        # 参数验证
        if not self.config.validate_fan_index(fan_index):
            error_msg = f"风扇索引无效: {fan_index}"
            print(f"[ERROR] {error_msg}")
            if self.logger:
                self.logger.error(error_msg)
            return False

        speed_percent = max(0.0, min(100.0, speed_percent))

        # 转换为PWM值
        pwm_value = int((speed_percent / 100.0) * self.config.pwm_max)

        # 构建请求
        reg_addr = self.config.get_register_address(fan_index)
        request = self._build_write_request(reg_addr, pwm_value)

        # 详细日志
        if self.logger:
            self.logger.debug('-' * 60)
            self.logger.info(f'设置风扇 #{fan_index + 1} 速度')
            self.logger.debug(f'  风扇索引: {fan_index} (0-based)')
            self.logger.debug(f'  速度百分比: {speed_percent:.2f}%')
            self.logger.debug(f'  PWM值: {pwm_value}')
            self.logger.debug(f'  寄存器地址: 0x{reg_addr:04X}')
            self.logger.debug(f'  请求帧: {" ".join(f"{b:02X}" for b in request)}')

        # 发送命令
        result = self._send_command(request)

        self.stats['total_commands'] += 1

        if result.get('valid'):
            self.stats['success_commands'] += 1
            print(f"[OK] 风扇#{fan_index + 1}: 速度设置为 {speed_percent:.1f}% (PWM: {pwm_value})")
            if self.logger:
                self.logger.info(f'  [OK] 成功: 风扇#{fan_index + 1} -> {speed_percent:.1f}% (PWM: {pwm_value})')
            return True
        else:
            self.stats['failed_commands'] += 1
            error_msg = result.get('error', '未知错误')
            print(f"[ERROR] 风扇#{fan_index + 1}: 设置失败 - {error_msg}")
            if self.logger:
                self.logger.error(f'  [ERROR] 失败: {error_msg}')
            return False

    def set_all_fans_speed(self, speed_percent: float) -> bool:
        """
        设置所有风扇为相同速度

        Args:
            speed_percent: 速度百分比（0.0-100.0）

        Returns:
            bool: 成功返回True，失败返回False
        """
        speed_percent = max(0.0, min(100.0, speed_percent))
        pwm_value = int((speed_percent / 100.0) * self.config.pwm_max)

        # 构建PWM值列表
        pwm_values = [pwm_value] * self.config.fan_count

        # 使用写多个寄存器功能
        start_addr = self.config.start_register
        request = self._build_write_multiple_request(start_addr, pwm_values)

        # 详细日志
        if self.logger:
            self.logger.debug('=' * 60)
            self.logger.info(f'设置所有风扇速度')
            self.logger.debug(f'  速度百分比: {speed_percent:.2f}%')
            self.logger.debug(f'  PWM值: {pwm_value} (所有{self.config.fan_count}个风扇)')
            self.logger.debug(f'  起始地址: 0x{start_addr:04X}')
            self.logger.debug(f'  PWM列表: {pwm_values[:5]}...' if len(pwm_values) > 5 else f'  PWM列表: {pwm_values}')
            self.logger.debug(f'  请求长度: {len(request)} 字节')

        # 发送命令
        result = self._send_command(request)

        self.stats['total_commands'] += 1

        if result.get('valid'):
            self.stats['success_commands'] += 1
            print(f"[OK] 所有风扇: 速度设置为 {speed_percent:.1f}% (PWM: {pwm_value})")
            if self.logger:
                self.logger.info(f'  [OK] 成功: 所有{self.config.fan_count}个风扇 -> {speed_percent:.1f}% (PWM: {pwm_value})')
                # 记录每个风扇的详细信息
                for i in range(self.config.fan_count):
                    self.logger.debug(f'    风扇#{i+1}: 寄存器0x{start_addr+i:04X} = PWM:{pwm_value} ({speed_percent:.1f}%)')
            return True
        else:
            self.stats['failed_commands'] += 1
            error_msg = result.get('error', '未知错误')
            print(f"[ERROR] 所有风扇: 设置失败 - {error_msg}")
            if self.logger:
                self.logger.error(f'  [ERROR] 失败: {error_msg}')
            return False

    def set_fans_speed_individual(self, speed_list: List[float]) -> bool:
        """
        分别设置每个风扇的速度

        Args:
            speed_list: 速度百分比列表，长度应为fan_count

        Returns:
            bool: 成功返回True，失败返回False
        """
        if len(speed_list) != self.config.fan_count:
            error_msg = f"速度列表长度不匹配: 期望{self.config.fan_count}，实际{len(speed_list)}"
            print(f"[ERROR] {error_msg}")
            if self.logger:
                self.logger.error(error_msg)
            return False

        # 转换为PWM值列表
        pwm_values = []
        for i, speed in enumerate(speed_list):
            speed = max(0.0, min(100.0, speed))
            pwm_value = int((speed / 100.0) * self.config.pwm_max)
            pwm_values.append(pwm_value)

        # 使用写多个寄存器功能
        start_addr = self.config.start_register
        request = self._build_write_multiple_request(start_addr, pwm_values)

        # 详细日志
        if self.logger:
            self.logger.debug('=' * 60)
            self.logger.info(f'分别设置每个风扇速度')
            self.logger.debug(f'  风扇数量: {self.config.fan_count}')
            self.logger.debug(f'  起始地址: 0x{start_addr:04X}')
            self.logger.debug(f'  请求长度: {len(request)} 字节')
            # 记录每个风扇的设置信息
            for i, (speed, pwm) in enumerate(zip(speed_list, pwm_values)):
                reg_addr = start_addr + i
                self.logger.debug(f'  风扇#{i+1}: {speed:.1f}% -> PWM:{pwm} -> 寄存器0x{reg_addr:04X}')

        # 发送命令
        result = self._send_command(request)

        self.stats['total_commands'] += 1

        if result.get('valid'):
            self.stats['success_commands'] += 1
            speed_str = ", ".join([f"{s:.1f}%" for s in speed_list])
            print(f"[OK] 分别设置风扇: [{speed_str}]")
            if self.logger:
                self.logger.info(f'  [OK] 成功: 分别设置{self.config.fan_count}个风扇')
                # 汇总显示
                for i, (speed, pwm) in enumerate(zip(speed_list, pwm_values)):
                    reg_addr = start_addr + i
                    self.logger.info(f'    风扇#{i+1:2d} -> {speed:5.1f}% (PWM:{pwm:4d}, 寄存器:0x{reg_addr:04X})')
            return True
        else:
            self.stats['failed_commands'] += 1
            error_msg = result.get('error', '未知错误')
            print(f"[ERROR] 分别设置失败 - {error_msg}")
            if self.logger:
                self.logger.error(f'  [ERROR] 失败: {error_msg}')
            return False

    def set_fans_speed_dict(self, speed_dict: Dict[int, float]) -> bool:
        """
        通过字典设置指定风扇的速度

        Args:
            speed_dict: 风扇索引到速度的映射，如 {0: 50.0, 5: 75.0}

        Returns:
            bool: 成功返回True，失败返回False
        """
        success_count = 0
        fail_count = 0

        for fan_index, speed in speed_dict.items():
            if self.set_fan_speed(fan_index, speed):
                success_count += 1
            else:
                fail_count += 1

        print(f"📊 设置结果: 成功{success_count}个，失败{fail_count}个")
        return fail_count == 0

    def stop_all_fans(self) -> bool:
        """
        停止所有风扇

        Returns:
            bool: 成功返回True，失败返回False
        """
        return self.set_all_fans_speed(0.0)

    def set_all_fans_max(self) -> bool:
        """
        设置所有风扇为最大速度

        Returns:
            bool: 成功返回True，失败返回False
        """
        return self.set_all_fans_speed(100.0)

    def get_statistics(self) -> Dict:
        """
        获取统计信息

        Returns:
            Dict: 统计信息字典
        """
        return self.stats.copy()

    def print_statistics(self):
        """打印统计信息"""
        print("\n" + "="*60)
        print("风扇控制统计")
        print("="*60)
        print(f"总命令数: {self.stats['total_commands']}")
        print(f"成功命令: {self.stats['success_commands']}")
        print(f"失败命令: {self.stats['failed_commands']}")
        print(f"连接错误: {self.stats['connection_errors']}")

        if self.stats['total_commands'] > 0:
            success_rate = (self.stats['success_commands'] / self.stats['total_commands']) * 100
            print(f"成功率: {success_rate:.1f}%")
        print("="*60 + "\n")

        # 同样记录到日志
        if self.logger:
            self.logger.info('='*60)
            self.logger.info('风扇控制统计')
            self.logger.info(f'总命令数: {self.stats["total_commands"]}')
            self.logger.info(f'成功命令: {self.stats["success_commands"]}')
            self.logger.info(f'失败命令: {self.stats["failed_commands"]}')
            self.logger.info(f'连接错误: {self.stats["connection_errors"]}')
            if self.stats['total_commands'] > 0:
                success_rate = (self.stats['success_commands'] / self.stats['total_commands']) * 100
                self.logger.info(f'成功率: {success_rate:.1f}%')
            self.logger.info('='*60)

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()


# 便捷函数
def quick_control_fan(fan_index: int, speed: float, device_ip: str = "192.168.2.1") -> bool:
    """
    快速控制单个风扇

    Args:
        fan_index: 风扇索引
        speed: 速度百分比
        device_ip: 设备IP

    Returns:
        bool: 成功返回True
    """
    config = FanConfig(device_ip=device_ip)
    with ModbusFanController(config) as controller:
        return controller.set_fan_speed(fan_index, speed)


def quick_control_all_fans(speed: float, device_ip: str = "192.168.2.1") -> bool:
    """
    快速控制所有风扇

    Args:
        speed: 速度百分比
        device_ip: 设备IP

    Returns:
        bool: 成功返回True
    """
    config = FanConfig(device_ip=device_ip)
    with ModbusFanController(config) as controller:
        return controller.set_all_fans_speed(speed)
