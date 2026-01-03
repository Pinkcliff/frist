# -*- coding: utf-8 -*-
"""
批量风扇控制器

用于管理多个风扇控制器板（100个模块，每个16个风扇）
"""

import socket
import time
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import FanConfig
from .modbus_fan import ModbusFanController, setup_fan_logger


class MultiBoardConfig:
    """多板配置管理"""

    @staticmethod
    def generate_board_configs(
        base_ip: str = "192.168.2.",
        start_ip: int = 1,
        board_count: int = 100,
        fans_per_board: int = 16
    ) -> List[FanConfig]:
        """
        生成多个板子的配置

        Args:
            base_ip: 基础IP地址
            start_ip: 起始IP编号
            board_count: 板子数量
            fans_per_board: 每个板子的风扇数量

        Returns:
            List[FanConfig]: 板子配置列表
        """
        configs = []
        for i in range(board_count):
            ip_num = start_ip + i
            config = FanConfig(
                device_ip=f"{base_ip}{ip_num}",
                device_port=8234,
                slave_addr=1,
                fan_count=fans_per_board,
                start_register=0,
                pwm_min=0,
                pwm_max=1000,
                timeout=5.0,
            )
            configs.append(config)
        return configs

    @staticmethod
    def get_board_ip(board_index: int, base_ip: str = "192.168.2.", start_ip: int = 1) -> str:
        """获取指定板子的IP地址"""
        return f"{base_ip}{start_ip + board_index}"


class BatchFanController:
    """批量风扇控制器

    管理多个风扇控制器板，支持批量操作和并行控制
    """

    def __init__(
        self,
        board_configs: List[FanConfig] = None,
        enable_logging: bool = True,
        log_file: str = None
    ):
        """
        初始化批量风扇控制器

        Args:
            board_configs: 板子配置列表，如果为None则生成100个默认配置
            enable_logging: 是否启用日志
            log_file: 自定义日志文件路径
        """
        # 生成默认配置（100个板子）
        if board_configs is None:
            board_configs = MultiBoardConfig.generate_board_configs(
                base_ip="192.168.2.",
                start_ip=1,
                board_count=100,
                fans_per_board=16
            )

        self.board_configs = board_configs
        self.board_count = len(board_configs)
        self.enable_logging = enable_logging

        # 为每个板子创建控制器
        self.controllers: List[ModbusFanController] = []
        for i, config in enumerate(board_configs):
            controller = ModbusFanController(config, enable_logging=False)
            controller.board_id = i + 1  # 板子编号（1-100）
            self.controllers.append(controller)

        # 批量日志记录器
        if enable_logging:
            if log_file is None:
                log_dir = os.path.join(os.path.dirname(__file__), 'logs')
                os.makedirs(log_dir, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                log_file = os.path.join(log_dir, f'batch_fan_control_{timestamp}.log')

            self.batch_logger = setup_fan_logger(log_file)
            self.batch_logger.info('='*80)
            self.batch_logger.info(f'批量风扇控制器初始化')
            self.batch_logger.info(f'板子数量: {self.board_count}')
            self.batch_logger.info(f'每个板子风扇数: {board_configs[0].fan_count if board_configs else 16}')
            self.batch_logger.info(f'总风扇数: {self.board_count * (board_configs[0].fan_count if board_configs else 16)}')
            self.batch_logger.info(f'IP范围: {board_configs[0].device_ip} - {board_configs[-1].device_ip}')
            self.batch_logger.info('='*80)
        else:
            self.batch_logger = None

        # 统计信息
        self.stats = {
            'total_boards': self.board_count,
            'connected_boards': 0,
            'failed_boards': 0,
            'total_commands': 0,
            'success_commands': 0,
            'failed_commands': 0,
        }

    def connect_all(self, max_workers: int = 10) -> Dict[int, bool]:
        """
        连接所有板子

        Args:
            max_workers: 最大并行连接数

        Returns:
            Dict[int, bool]: 板子编号到连接结果的映射
        """
        if self.batch_logger:
            self.batch_logger.info('-'*80)
            self.batch_logger.info(f'开始连接所有{self.board_count}个板子（并行数={max_workers}）')

        results = {}

        def connect_board(controller: ModbusFanController) -> Tuple[int, bool]:
            """连接单个板子"""
            board_id = controller.board_id
            ip = controller.config.device_ip
            success = controller.connect()
            if self.batch_logger:
                if success:
                    self.batch_logger.info(f'  板子#{board_id:3d} ({ip}): [OK] 连接成功')
                else:
                    self.batch_logger.error(f'  板子#{board_id:3d} ({ip}): [ERROR] 连接失败')
            return (board_id, success)

        # 并行连接
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(connect_board, ctrl) for ctrl in self.controllers]

            for future in as_completed(futures):
                board_id, success = future.result()
                results[board_id] = success
                if success:
                    self.stats['connected_boards'] += 1
                else:
                    self.stats['failed_boards'] += 1

        # 统计
        if self.batch_logger:
            self.batch_logger.info(f'连接完成: 成功{self.stats["connected_boards"]}/{self.board_count}, 失败{self.stats["failed_boards"]}')

        return results

    def disconnect_all(self):
        """断开所有板子的连接"""
        if self.batch_logger:
            self.batch_logger.info('断开所有板子连接')

        for controller in self.controllers:
            controller.disconnect()

        if self.batch_logger:
            self.batch_logger.info('所有板子已断开')

    def set_all_boards_speed(self, speed_percent: float, max_workers: int = 10) -> Dict[int, bool]:
        """
        设置所有板子的风扇为相同速度

        Args:
            speed_percent: 速度百分比
            max_workers: 最大并行数

        Returns:
            Dict[int, bool]: 板子编号到操作结果的映射
        """
        if self.batch_logger:
            self.batch_logger.debug('='*80)
            self.batch_logger.info(f'设置所有板子风扇速度: {speed_percent:.1f}%')

        results = {}

        def set_board_speed(controller: ModbusFanController) -> Tuple[int, bool]:
            """设置单个板子的风扇速度"""
            board_id = controller.board_id
            success = controller.set_all_fans_speed(speed_percent)
            self.stats['total_commands'] += 1
            if success:
                self.stats['success_commands'] += 1
            else:
                self.stats['failed_commands'] += 1
            return (board_id, success)

        # 并行执行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(set_board_speed, ctrl) for ctrl in self.controllers]

            for future in as_completed(futures):
                board_id, success = future.result()
                results[board_id] = success

        # 记录结果
        success_count = sum(1 for s in results.values() if s)
        if self.batch_logger:
            self.batch_logger.info(f'  结果: 成功{success_count}/{len(results)}个板子')

        return results

    def set_board_speed_individual(self, board_index: int, speed_list: List[float]) -> bool:
        """
        设置指定板子的每个风扇速度

        Args:
            board_index: 板子索引（0-99）
            speed_list: 速度列表

        Returns:
            bool: 成功返回True
        """
        if not 0 <= board_index < len(self.controllers):
            if self.batch_logger:
                self.batch_logger.error(f'板子索引无效: {board_index}')
            return False

        controller = self.controllers[board_index]
        board_id = controller.board_id

        if self.batch_logger:
            self.batch_logger.info(f'设置板子#{board_id}风扇速度')

        success = controller.set_fans_speed_individual(speed_list)

        self.stats['total_commands'] += 1
        if success:
            self.stats['success_commands'] += 1
        else:
            self.stats['failed_commands'] += 1

        return success

    def set_all_boards_individual(self, speed_matrix: List[List[float]], max_workers: int = 10) -> Dict[int, bool]:
        """
        分别设置每个板子的风扇速度

        Args:
            speed_matrix: 速度矩阵，speed_matrix[i]是第i个板子的速度列表
            max_workers: 最大并行数

        Returns:
            Dict[int, bool]: 板子编号到操作结果的映射
        """
        if len(speed_matrix) != len(self.controllers):
            if self.batch_logger:
                self.batch_logger.error(f'速度矩阵大小不匹配: 期望{len(self.controllers)}, 实际{len(speed_matrix)}')
            return {}

        if self.batch_logger:
            self.batch_logger.info(f'分别设置所有板子的风扇速度')

        results = {}

        def set_board(controller: ModbusFanController, speeds: List[float]) -> Tuple[int, bool]:
            """设置单个板子"""
            board_id = controller.board_id
            success = controller.set_fans_speed_individual(speeds)
            self.stats['total_commands'] += 1
            if success:
                self.stats['success_commands'] += 1
            else:
                self.stats['failed_commands'] += 1
            return (board_id, success)

        # 并行执行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(set_board, ctrl, speeds)
                for ctrl, speeds in zip(self.controllers, speed_matrix)
            ]

            for future in as_completed(futures):
                board_id, success = future.result()
                results[board_id] = success

        return results

    def stop_all_boards(self, max_workers: int = 10) -> Dict[int, bool]:
        """
        停止所有板子的风扇

        Args:
            max_workers: 最大并行数

        Returns:
            Dict[int, bool]: 板子编号到操作结果的映射
        """
        return self.set_all_boards_speed(0.0, max_workers)

    def get_board_status(self, board_index: int) -> Dict:
        """
        获取指定板子的状态

        Args:
            board_index: 板子索引（0-99）

        Returns:
            Dict: 板子状态信息
        """
        if not 0 <= board_index < len(self.controllers):
            return {'error': '板子索引无效'}

        controller = self.controllers[board_index]
        return {
            'board_id': controller.board_id,
            'ip': controller.config.device_ip,
            'fan_count': controller.config.fan_count,
            'is_connected': controller.is_connected,
            'stats': controller.get_statistics(),
        }

    def get_all_status(self) -> List[Dict]:
        """
        获取所有板子的状态

        Returns:
            List[Dict]: 所有板子的状态信息
        """
        return [self.get_board_status(i) for i in range(len(self.controllers))]

    def print_batch_statistics(self):
        """打印批量统计信息"""
        print("\n" + "="*80)
        print("批量风扇控制统计")
        print("="*80)
        print(f"板子总数: {self.stats['total_boards']}")
        print(f"已连接: {self.stats['connected_boards']}")
        print(f"连接失败: {self.stats['failed_boards']}")
        print(f"总命令数: {self.stats['total_commands']}")
        print(f"成功命令: {self.stats['success_commands']}")
        print(f"失败命令: {self.stats['failed_commands']}")

        if self.stats['total_commands'] > 0:
            success_rate = (self.stats['success_commands'] / self.stats['total_commands']) * 100
            print(f"成功率: {success_rate:.1f}%")
        print("="*80 + "\n")

        # 同时记录到日志
        if self.batch_logger:
            self.batch_logger.info('='*80)
            self.batch_logger.info('批量风扇控制统计')
            self.batch_logger.info(f'板子总数: {self.stats["total_boards"]}')
            self.batch_logger.info(f'已连接: {self.stats["connected_boards"]}')
            self.batch_logger.info(f'连接失败: {self.stats["failed_boards"]}')
            self.batch_logger.info(f'总命令数: {self.stats["total_commands"]}')
            self.batch_logger.info(f'成功命令: {self.stats["success_commands"]}')
            self.batch_logger.info(f'失败命令: {self.stats["failed_commands"]}')
            if self.stats['total_commands'] > 0:
                success_rate = (self.stats['success_commands'] / self.stats['total_commands']) * 100
                self.batch_logger.info(f'成功率: {success_rate:.1f}%')
            self.batch_logger.info('='*80)

    def __enter__(self):
        """上下文管理器入口"""
        self.connect_all()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect_all()


# 便捷函数
def create_batch_controller(
    board_count: int = 100,
    base_ip: str = "192.168.2.",
    start_ip: int = 1,
    fans_per_board: int = 16
) -> BatchFanController:
    """
    创建批量风扇控制器

    Args:
        board_count: 板子数量
        base_ip: 基础IP地址
        start_ip: 起始IP编号
        fans_per_board: 每个板子的风扇数量

    Returns:
        BatchFanController: 批量控制器实例
    """
    configs = MultiBoardConfig.generate_board_configs(
        base_ip=base_ip,
        start_ip=start_ip,
        board_count=board_count,
        fans_per_board=fans_per_board
    )
    return BatchFanController(configs)
