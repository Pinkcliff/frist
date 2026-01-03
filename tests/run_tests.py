# -*- coding: utf-8 -*-
"""
测试运行脚本
使用conda环境my_env运行所有单元测试
"""
import sys
import os
import unittest
import time

# 添加项目路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("开始运行单元测试")
    print("=" * 70)
    print(f"工作目录: {os.getcwd()}")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print("=" * 70)
    print()

    # 创建测试套件
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')

    # 创建测试运行器
    runner = unittest.TextTestRunner(verbosity=2)

    # 记录开始时间
    start_time = time.time()

    # 运行测试
    print("正在运行测试...\n")
    result = runner.run(suite)

    # 计算耗时
    elapsed_time = time.time() - start_time

    # 打印测试结果摘要
    print()
    print("=" * 70)
    print("测试结果摘要")
    print("=" * 70)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    print(f"耗时: {elapsed_time:.2f} 秒")
    print("=" * 70)

    # 返回退出码
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_module_name):
    """运行特定测试模块"""
    print(f"运行测试模块: {test_module_name}")
    print("=" * 70)

    try:
        # 导入测试模块
        module = __import__(test_module_name, fromlist=[''])

        # 加载测试
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)

        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return 0 if result.wasSuccessful() else 1

    except ImportError as e:
        print(f"错误: 无法导入测试模块 '{test_module_name}'")
        print(f"详细错误: {e}")
        return 1


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='运行单元测试')
    parser.add_argument(
        '--module', '-m',
        type=str,
        default=None,
        help='指定要运行的测试模块 (例如: test_dashboard)'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出所有可用的测试模块'
    )

    args = parser.parse_args()

    # 列出可用的测试模块
    if args.list:
        print("可用的测试模块:")
        print("-" * 40)
        test_files = [f for f in os.listdir(os.path.dirname(__file__))
                      if f.startswith('test_') and f.endswith('.py')]
        for test_file in sorted(test_files):
            module_name = test_file[:-3]  # 移除.py扩展名
            print(f"  - {module_name}")
        return 0

    # 运行特定模块或所有测试
    if args.module:
        return run_specific_test(args.module)
    else:
        return run_all_tests()


if __name__ == '__main__':
    sys.exit(main())
