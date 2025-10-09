#!/usr/bin/env python3
"""
文件监控与重命名脚本
持续监控当前目录下的新文件，并按顺序重命名指定后缀的文件
支持通过命令行参数指定文件后缀
"""

import os
import re
import time
import signal
import sys
import argparse
from pathlib import Path
from collections import deque
from threading import Lock, Thread
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class FileRenamer:
    def __init__(self, pattern, digit_count=3, flags=0):
        """
        初始化文件重命名器
        
        Args:
            pattern: 文件后缀正则表达式模式
            digit_count: 序号位数
            flags: 正则表达式标志
        """
        self.pattern = re.compile(pattern, flags)
        self.digit_count = digit_count
        self.counter = 0
        self.lock = Lock()  # 线程锁，防止并发问题
        self.processing_queue = deque()  # 处理队列
        self.processing = set()  # 正在处理的文件集合
        self.renamed_files = set()  # 记录已重命名的文件，避免重复处理
        
        # 初始化计数器：找到已存在文件的最大序号
        self._initialize_counter()
        
    def _initialize_counter(self):
        """初始化计数器，基于已存在的文件"""
        max_num = 0
        current_dir = Path.cwd()
        
        for file_path in current_dir.iterdir():
            if file_path.is_file():
                # 检查文件名是否符合序号格式
                match = re.match(r'^(\d+)', file_path.name)
                if match and self.pattern.search(file_path.name):
                    num = int(match.group(1))
                    max_num = max(max_num, num)
                    # 记录已存在的重命名文件
                    self.renamed_files.add(file_path.name)
        
        self.counter = max_num
        logger.info(f"计数器初始化为: {self.counter}")
        logger.info(f"已存在 {len(self.renamed_files)} 个重命名文件")
    
    def get_next_filename(self, original_ext):
        """获取下一个文件名"""
        with self.lock:
            self.counter += 1
            num_str = str(self.counter).zfill(self.digit_count)
            return f"{num_str}{original_ext}"
    
    def should_process(self, filename):
        """检查文件是否符合处理条件"""
        # 跳过已重命名的文件
        if filename in self.renamed_files:
            return False
        
        # 跳过已处理的文件
        if filename in self.processing:
            return False
            
        # 检查文件后缀是否符合要求且不是已编号的文件
        is_target_extension = self.pattern.search(filename) is not None
        is_already_numbered = re.match(r'^\d+', filename) is not None
        
        return is_target_extension and not is_already_numbered and not filename.startswith('.')
    
    def process_file(self, file_path):
        """
        处理单个文件
        
        Args:
            file_path: 文件路径对象
            
        Returns:
            bool: 是否成功处理
        """
        try:
            # 检查文件是否稳定（不再被修改）
            if not self._is_file_stable(file_path):
                return False
                
            # 获取文件后缀
            original_ext = file_path.suffix
            
            # 生成新文件名
            new_filename = self.get_next_filename(original_ext)
            new_filepath = file_path.parent / new_filename
            
            # 在重命名前记录，避免监控到重命名后的文件
            original_name = file_path.name
            self.renamed_files.add(new_filename)
            
            # 重命名文件
            file_path.rename(new_filepath)
            logger.info(f"重命名: {original_name} -> {new_filename}")
            
            # 从处理集合中移除原文件名
            if original_name in self.processing:
                self.processing.remove(original_name)
                
            return True
            
        except (OSError, IOError) as e:
            logger.warning(f"处理文件 {file_path.name} 时出错: {e}")
            # 出错时从处理集合中移除
            if file_path.name in self.processing:
                self.processing.remove(file_path.name)
            return False
    
    def _is_file_stable(self, file_path, max_attempts=5, delay=0.1):
        """
        检查文件是否稳定（不再被写入）
        
        Args:
            file_path: 文件路径
            max_attempts: 最大检查次数
            delay: 检查间隔
            
        Returns:
            bool: 文件是否稳定
        """
        last_size = -1
        for attempt in range(max_attempts):
            try:
                current_size = file_path.stat().st_size
                if current_size == last_size:
                    return True
                last_size = current_size
                time.sleep(delay)
            except OSError:
                time.sleep(delay)
                continue
        return False

class FileMonitorHandler(FileSystemEventHandler):
    """文件系统事件处理器"""
    
    def __init__(self, renamer):
        super().__init__()
        self.renamer = renamer
        self.processing_thread = None
        self.should_stop = False
        
    def on_created(self, event):
        """文件创建事件处理"""
        if not event.is_directory:
            self._handle_new_file(event.src_path)
    
    def on_moved(self, event):
        """文件移动事件处理"""
        if not event.is_directory:
            self._handle_new_file(event.dest_path)
    
    def _handle_new_file(self, file_path):
        """处理新文件"""
        path_obj = Path(file_path)
        
        # 检查文件是否符合处理条件
        if not self.renamer.should_process(path_obj.name):
            return
        
        # 避免重复处理
        if path_obj.name in self.renamer.processing:
            return
            
        # 添加到处理集合和队列
        self.renamer.processing.add(path_obj.name)
        self.renamer.processing_queue.append(path_obj)
        logger.debug(f"检测到新文件: {path_obj.name}")

class FileProcessor:
    """文件处理线程"""
    
    def __init__(self, renamer, handler):
        self.renamer = renamer
        self.handler = handler
        self.thread = None
        
    def start(self):
        """启动处理线程"""
        self.thread = Thread(target=self._process_files, daemon=True)
        self.thread.start()
        
    def _process_files(self):
        """处理文件队列"""
        while not self.handler.should_stop:
            if self.renamer.processing_queue:
                file_path = self.renamer.processing_queue.popleft()
                
                if file_path.exists():
                    success = self.renamer.process_file(file_path)
                    if not success:
                        # 处理失败，重新加入队列（限制重试次数）
                        if file_path.name in self.renamer.processing:
                            # 简单重试逻辑，实际中可能需要更复杂的重试机制
                            time.sleep(0.5)
                            if file_path.exists():
                                self.renamer.processing_queue.append(file_path)
                else:
                    # 文件不存在，从集合中移除
                    if file_path.name in self.renamer.processing:
                        self.renamer.processing.remove(file_path.name)
            else:
                time.sleep(0.1)  # 队列为空时短暂休眠

class GracefulExiter:
    """优雅退出处理器"""
    
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    
    def exit_gracefully(self, signum, frame):
        """处理退出信号"""
        logger.info("接收到退出信号，正在关闭...")
        self.shutdown = True

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="文件监控与重命名脚本")
    parser.add_argument(
        "-e", "--extension", 
        required=True,
        help="要监控的文件后缀，例如: cpp, txt, jpg, png 等。支持多个后缀，用逗号分隔，如: cpp,c,h"
    )
    parser.add_argument(
        "-d", "--digits", 
        type=int, 
        default=3,
        help="序号的位数，默认是 3"
    )
    parser.add_argument(
        "-i", "--ignore-case", 
        action="store_true",
        help="是否忽略文件后缀的大小写"
    )
    parser.add_argument(
        "-p", "--pattern", 
        help="直接指定正则表达式模式，覆盖 --extension 参数"
    )
    
    return parser.parse_args()

def create_pattern_from_extension(extension, ignore_case=False):
    """
    根据文件后缀创建正则表达式模式
    
    Args:
        extension: 文件后缀，如 "cpp", "txt" 等
        ignore_case: 是否忽略大小写
        
    Returns:
        tuple: (pattern, flags)
    """
    # 处理多个后缀的情况，如 "cpp,c,h" 或 "jpg|png|gif"
    if ',' in extension:
        extensions = extension.split(',')
        pattern_parts = [f"\\.{ext.strip()}$" for ext in extensions]
        pattern = f"({'|'.join(pattern_parts)})"
    elif '|' in extension:
        # 如果用户已经使用了 | 分隔符，直接使用
        extensions = extension.split('|')
        pattern_parts = [f"\\.{ext.strip()}$" for ext in extensions]
        pattern = f"({'|'.join(pattern_parts)})"
    else:
        # 单个后缀
        pattern = f"\\.{extension}$"
    
    flags = re.IGNORECASE if ignore_case else 0
    
    return pattern, flags

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 创建正则表达式模式
    if args.pattern:
        # 使用用户直接提供的正则表达式
        pattern = args.pattern
        flags = re.IGNORECASE if args.ignore_case else 0
        logger.info(f"使用自定义正则表达式: {pattern}")
    else:
        # 根据文件后缀创建正则表达式
        pattern, flags = create_pattern_from_extension(args.extension, args.ignore_case)
        logger.info(f"监控文件后缀: {args.extension}")
    
    if args.ignore_case:
        logger.info("启用忽略大小写")
    
    print("=" * 50)
    print("文件监控重命名脚本")
    print(f"监控文件模式: {pattern}")
    print(f"序号位数: {args.digits}")
    print("按 Ctrl+C 退出")
    print("=" * 50)
    
    # 初始化组件
    graceful_exiter = GracefulExiter()
    renamer = FileRenamer(pattern=pattern, digit_count=args.digits, flags=flags)
    event_handler = FileMonitorHandler(renamer)
    file_processor = FileProcessor(renamer, event_handler)
    observer = Observer()
    
    try:
        # 启动文件监控
        observer.schedule(event_handler, '.', recursive=False)
        observer.start()
        
        # 启动文件处理线程
        file_processor.start()
        
        logger.info("文件监控已启动，正在监控当前目录...")
        
        # 主循环
        while not graceful_exiter.shutdown:
            time.sleep(0.5)
            
    except Exception as e:
        logger.error(f"发生错误: {e}")
    finally:
        # 清理资源
        logger.info("正在停止监控...")
        event_handler.should_stop = True
        observer.stop()
        observer.join()
        logger.info("监控已停止")

if __name__ == "__main__":
    main()