#!/usr/bin/env python3
"""
文件监控与重命名脚本
"""

import re
import time
import signal
import argparse
import shutil
from pathlib import Path
from collections import deque, defaultdict
from threading import Lock, Thread, Event, Condition
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

class FileBuffer:
    """文件缓冲区 - 管理待处理文件"""
    
    def __init__(self, max_size=1000, batch_size=10, batch_timeout=0.5):
        """
        初始化文件缓冲区
        
        Args:
            max_size: 最大缓冲区大小
            batch_size: 批处理大小
            batch_timeout: 批处理超时时间(秒)
        """
        self.max_size = max_size
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.buffer = deque()
        self.lock = Lock()
        self.condition = Condition()
        self.processing_files = set()
        self.failed_files = defaultdict(int)  # 文件失败次数记录
        self.max_retries = 3
        
    def add_file(self, file_path):
        """添加文件到缓冲区"""
        with self.lock:
            if len(self.buffer) >= self.max_size:
                logger.warning("缓冲区已满，丢弃文件: %s", file_path.name)
                return False
                
            if file_path.name in self.processing_files:
                return False
                
            # 检查失败次数
            if self.failed_files[file_path.name] >= self.max_retries:
                logger.debug("文件 %s 已达到最大重试次数，跳过", file_path.name)
                return False
                
            self.buffer.append(file_path)
            self.processing_files.add(file_path.name)
            
            # 通知等待的消费者
            with self.condition:
                self.condition.notify_all()
                
            return True
    
    def get_batch(self, timeout=None):
        """获取一批文件进行处理"""
        if timeout is None:
            timeout = self.batch_timeout
            
        batch = []
        start_time = time.time()
        
        with self.condition:
            while len(batch) < self.batch_size and (time.time() - start_time) < timeout:
                with self.lock:
                    if self.buffer:
                        file_path = self.buffer.popleft()
                        batch.append(file_path)
                
                if len(batch) < self.batch_size:
                    # 等待新文件或超时
                    remaining_time = timeout - (time.time() - start_time)
                    if remaining_time > 0:
                        self.condition.wait(remaining_time)
        
        return batch
    
    def mark_success(self, filename):
        """标记文件处理成功"""
        with self.lock:
            if filename in self.processing_files:
                self.processing_files.remove(filename)
            if filename in self.failed_files:
                del self.failed_files[filename]
    
    def mark_failed(self, filename):
        """标记文件处理失败"""
        with self.lock:
            self.failed_files[filename] += 1
            if filename in self.processing_files:
                self.processing_files.remove(filename)
                
    def get_stats(self):
        """获取缓冲区统计信息"""
        with self.lock:
            return {
                'buffer_size': len(self.buffer),
                'processing_count': len(self.processing_files),
                'failed_files': dict(self.failed_files)
            }

class FileRenamer:
    def __init__(self, pattern, digit_count=3, flags=0, temp_dir=".temp_rename", max_filename_length=255):
        """
        初始化文件重命名器
        
        Args:
            pattern: 文件后缀正则表达式模式
            digit_count: 序号位数
            flags: 正则表达式标志
            temp_dir: 临时目录名称
            max_filename_length: 最大文件名长度限制
        """
        self.pattern = re.compile(pattern, flags)
        self.digit_count = digit_count
        self.counter = 0
        self.counter_lock = Lock()  # 专门用于计数器的锁
        self.temp_dir = Path(temp_dir)
        self.max_filename_length = max_filename_length
        self.renamed_files_pattern = re.compile(r'^\d{' + str(digit_count) + r'}' + pattern)  # 精确匹配已重命名文件
        
        # 创建临时目录
        self.temp_dir.mkdir(exist_ok=True)
        
        # 初始化计数器：找到已存在文件的最大序号
        self._initialize_counter()
        
    def _initialize_counter(self):
        """初始化计数器，基于已存在的文件"""
        max_num = 0
        current_dir = Path.cwd()
        
        # 扫描当前目录所有文件
        for file_path in current_dir.iterdir():
            if file_path.is_file():
                # 使用精确匹配检查文件名是否符合序号格式
                if self.renamed_files_pattern.search(file_path.name):
                    try:
                        # 提取数字部分
                        num_str = file_path.stem  # 获取不带后缀的文件名
                        num = int(num_str)
                        max_num = max(max_num, num)
                    except ValueError:
                        # 如果不能转换为数字，跳过
                        continue
        
        self.counter = max_num
        logger.info(f"计数器初始化为: {self.counter}")
    
    def get_next_filename(self, original_ext):
        """获取下一个文件名"""
        with self.counter_lock:
            self.counter += 1
            num_str = str(self.counter).zfill(self.digit_count)
            return f"{num_str}{original_ext}"
    
    def should_process(self, filename):
        """检查文件是否符合处理条件"""
        # 跳过临时目录中的文件
        if str(self.temp_dir) in filename:
            return False
            
        # 检查文件名长度是否超过限制
        if len(filename) > self.max_filename_length:
            logger.warning(f"文件名过长，跳过处理: {filename} (长度: {len(filename)})")
            return False
            
        # 检查文件后缀是否符合要求
        if not self.pattern.search(filename):
            return False
            
        # 使用精确匹配检查是否已编号，而不是简单的数字开头
        # 只有符合 "数字+后缀" 格式的文件才被认为是已编号的
        if self.renamed_files_pattern.match(filename):
            logger.debug(f"文件已编号，跳过: {filename}")
            return False
            
        # 不是以点开头的隐藏文件
        if filename.startswith('.'):
            return False
            
        return True
    
    def process_files_batch(self, file_paths):
        """
        批量处理文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            dict: 处理结果 {文件路径: 成功/失败}
        """
        results = {}
        
        for file_path in file_paths:
            try:
                # 记录文件信息用于诊断
                file_info = self._get_file_info(file_path)
                logger.debug(f"处理文件: {file_info}")
                
                # 快速检查文件是否可访问
                if not self._is_file_accessible(file_path):
                    logger.warning(f"文件不可访问: {file_path.name}")
                    results[file_path] = False
                    continue
                    
                # 获取文件后缀
                original_ext = file_path.suffix
                
                # 生成新文件名
                new_filename = self.get_next_filename(original_ext)
                new_filepath = file_path.parent / new_filename
                
                # 检查新文件名长度
                if len(new_filename) > self.max_filename_length:
                    logger.error(f"新文件名过长，无法重命名: {new_filename} (长度: {len(new_filename)})")
                    results[file_path] = False
                    continue
                
                # 先将文件移动到临时目录，避免被重复检测
                temp_filepath = self.temp_dir / file_path.name
                try:
                    file_path.rename(temp_filepath)
                except (OSError, IOError) as e:
                    logger.warning(f"无法移动文件到临时目录 {file_path.name}: {e}")
                    results[file_path] = False
                    continue
                
                # 从临时目录重命名到目标位置
                try:
                    temp_filepath.rename(new_filepath)
                    logger.info(f"重命名: {file_path.name} -> {new_filename}")
                    results[file_path] = True
                except (OSError, IOError) as e:
                    logger.warning(f"无法从临时目录重命名文件 {file_path.name}: {e}")
                    # 尝试将文件移回原位置
                    try:
                        temp_filepath.rename(file_path)
                    except Exception as restore_error:
                        logger.error(f"恢复文件失败 {file_path.name}: {restore_error}")
                    results[file_path] = False
                    
            except Exception as e:
                logger.error(f"处理文件 {file_path.name} 时发生未知错误: {e}")
                results[file_path] = False
                
        return results
    
    def _is_file_accessible(self, file_path, max_attempts=2, delay=0.05):
        """
        快速检查文件是否可访问
        
        Args:
            file_path: 文件路径
            max_attempts: 最大尝试次数
            delay: 检查间隔
            
        Returns:
            bool: 文件是否可访问
        """
        for attempt in range(max_attempts):
            try:
                # 尝试以读写模式打开文件
                with open(file_path, 'rb'):
                    return True
            except (OSError, IOError) as e:
                logger.debug(f"文件访问失败 {file_path.name} (尝试 {attempt+1}/{max_attempts}): {e}")
                if attempt < max_attempts - 1:
                    time.sleep(delay)
        return False
    
    def _get_file_info(self, file_path):
        """
        获取文件信息用于诊断
        
        Args:
            file_path: 文件路径
            
        Returns:
            dict: 文件信息
        """
        try:
            stat = file_path.stat()
            return {
                'name': file_path.name,
                'name_length': len(file_path.name),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'exists': file_path.exists()
            }
        except Exception as e:
            return {
                'name': file_path.name,
                'name_length': len(file_path.name),
                'error': str(e)
            }

class FileMonitorHandler(FileSystemEventHandler):
    """文件系统事件处理器 - 修复已编号判断问题"""
    
    def __init__(self, file_buffer, renamer):
        super().__init__()
        self.file_buffer = file_buffer
        self.renamer = renamer
        self.should_stop = False
        self.recent_events = set()  # 近期事件集合，用于去重
        self.event_processor_thread = None
        self.process_event = Event()
        self.event_stats = defaultdict(int)  # 事件统计
        
    def on_created(self, event):
        """文件创建事件处理"""
        if not event.is_directory:
            self._handle_file_event(event.src_path, 'created')
    
    def on_moved(self, event):
        """文件移动事件处理"""
        if not event.is_directory:
            self._handle_file_event(event.dest_path, 'moved')
    
    def on_deleted(self, event):
        """文件删除事件处理"""
        if not event.is_directory:
            self.event_stats['deleted'] += 1
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if not event.is_directory:
            self.event_stats['modified'] += 1
    
    def _handle_file_event(self, file_path, event_type):
        """处理文件事件"""
        path_obj = Path(file_path)
        
        # 记录事件统计
        self.event_stats[event_type] += 1
        
        # 检查文件是否符合处理条件
        if not self.renamer.should_process(path_obj.name):
            # 记录被跳过的原因
            if len(path_obj.name) > self.renamer.max_filename_length:
                self.event_stats['skipped_too_long'] += 1
            elif not self.renamer.pattern.search(path_obj.name):
                self.event_stats['skipped_wrong_extension'] += 1
            elif self.renamer.renamed_files_pattern.match(path_obj.name):
                self.event_stats['skipped_already_numbered'] += 1
            elif path_obj.name.startswith('.'):
                self.event_stats['skipped_hidden'] += 1
            else:
                self.event_stats['skipped_other'] += 1
            return
        
        # 使用文件路径和大小作为去重键
        try:
            file_size = path_obj.stat().st_size
            event_key = f"{file_path}:{file_size}:{event_type}"
        except:
            event_key = f"{file_path}:{event_type}"
            
        # 去重检查
        if event_key in self.recent_events:
            self.event_stats['duplicate'] += 1
            return
            
        # 添加到近期事件集合
        self.recent_events.add(event_key)
        
        # 添加到缓冲区
        if self.file_buffer.add_file(path_obj):
            logger.debug(f"添加到缓冲区: {path_obj.name} (事件: {event_type})")
            self.event_stats['added_to_buffer'] += 1
        else:
            self.event_stats['buffer_rejected'] += 1
        
        # 定期清理近期事件集合
        if len(self.recent_events) > 1000:
            self.recent_events.clear()
        
    def start_event_cleaner(self):
        """启动事件清理线程"""
        self.event_processor_thread = Thread(target=self._clean_events, daemon=True)
        self.event_processor_thread.start()
        
    def _clean_events(self):
        """定期清理近期事件集合"""
        while not self.should_stop:
            time.sleep(10)  # 每10秒清理一次
            self.recent_events.clear()
    
    def get_event_stats(self):
        """获取事件统计"""
        return dict(self.event_stats)

class BatchFileProcessor:
    """批量文件处理器"""
    
    def __init__(self, file_buffer, renamer, num_workers=3):
        self.file_buffer = file_buffer
        self.renamer = renamer
        self.num_workers = num_workers
        self.workers = []
        self.should_stop = False
        self.stats = {
            'processed': 0,
            'succeeded': 0,
            'failed': 0,
            'batches': 0
        }
        self.stats_lock = Lock()
        
    def start(self):
        """启动处理线程"""
        for i in range(self.num_workers):
            worker = Thread(target=self._process_batches, daemon=True, name=f"BatchProcessor-{i}")
            worker.start()
            self.workers.append(worker)
        
    def _process_batches(self):
        """处理文件批次"""
        while not self.should_stop:
            # 获取一批文件
            batch = self.file_buffer.get_batch()
            
            if not batch:
                continue
                
            # 处理批次
            results = self.renamer.process_files_batch(batch)
            
            # 更新结果
            for file_path, success in results.items():
                if success:
                    self.file_buffer.mark_success(file_path.name)
                    with self.stats_lock:
                        self.stats['succeeded'] += 1
                else:
                    self.file_buffer.mark_failed(file_path.name)
                    with self.stats_lock:
                        self.stats['failed'] += 1
            
            # 更新统计
            with self.stats_lock:
                self.stats['processed'] += len(batch)
                self.stats['batches'] += 1
            
            logger.debug(f"处理批次: {len(batch)} 个文件, 成功: {sum(results.values())}")
    
    def get_stats(self):
        """获取处理统计"""
        with self.stats_lock:
            return self.stats.copy()

class StatsReporter:
    """统计报告器"""
    
    def __init__(self, file_buffer, batch_processor, event_handler, report_interval=10):
        self.file_buffer = file_buffer
        self.batch_processor = batch_processor
        self.event_handler = event_handler
        self.report_interval = report_interval
        self.should_stop = False
        self.reporter_thread = None
        
    def start(self):
        """启动统计报告线程"""
        self.reporter_thread = Thread(target=self._report_stats, daemon=True)
        self.reporter_thread.start()
        
    def _report_stats(self):
        """定期报告统计信息"""
        while not self.should_stop:
            time.sleep(self.report_interval)
            
            buffer_stats = self.file_buffer.get_stats()
            processor_stats = self.batch_processor.get_stats()
            event_stats = self.event_handler.get_event_stats()
            
            # 基础统计
            logger.info(
                f"统计 - 缓冲区: {buffer_stats['buffer_size']}, "
                f"处理中: {buffer_stats['processing_count']}, "
                f"已处理: {processor_stats['processed']}, "
                f"成功: {processor_stats['succeeded']}, "
                f"失败: {processor_stats['failed']}, "
                f"批次: {processor_stats['batches']}"
            )
            
            # 事件统计（调试模式）
            if logger.getEffectiveLevel() <= logging.DEBUG:
                logger.debug(
                    f"事件统计 - 创建: {event_stats.get('created', 0)}, "
                    f"移动: {event_stats.get('moved', 0)}, "
                    f"删除: {event_stats.get('deleted', 0)}, "
                    f"修改: {event_stats.get('modified', 0)}, "
                    f"添加到缓冲区: {event_stats.get('added_to_buffer', 0)}, "
                    f"缓冲区拒绝: {event_stats.get('buffer_rejected', 0)}, "
                    f"重复事件: {event_stats.get('duplicate', 0)}"
                )
                
                # 跳过原因统计
                if any(key.startswith('skipped_') for key in event_stats):
                    logger.debug(
                        f"跳过统计 - 文件名过长: {event_stats.get('skipped_too_long', 0)}, "
                        f"扩展名不符: {event_stats.get('skipped_wrong_extension', 0)}, "
                        f"已编号: {event_stats.get('skipped_already_numbered', 0)}, "
                        f"隐藏文件: {event_stats.get('skipped_hidden', 0)}, "
                        f"其他: {event_stats.get('skipped_other', 0)}"
                    )

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
        help="要监控的文件后缀，例如: jpg, png, gif 等。支持多个后缀，用逗号分隔，如: jpg,png,gif"
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
    parser.add_argument(
        "-w", "--workers", 
        type=int, 
        default=3,
        help="处理线程数量，默认是 3"
    )
    parser.add_argument(
        "-t", "--temp-dir", 
        default=".temp_rename",
        help="临时目录名称，默认是 .temp_rename"
    )
    parser.add_argument(
        "--buffer-size", 
        type=int, 
        default=1000,
        help="缓冲区大小，默认是 1000"
    )
    parser.add_argument(
        "--batch-size", 
        type=int, 
        default=10,
        help="批处理大小，默认是 10"
    )
    parser.add_argument(
        "--batch-timeout", 
        type=float, 
        default=0.5,
        help="批处理超时时间(秒)，默认是 0.5"
    )
    parser.add_argument(
        "--max-filename-length", 
        type=int, 
        default=255,
        help="最大文件名长度限制，默认是 255"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="启用调试模式，显示更详细的日志"
    )
    
    return parser.parse_args()

def create_pattern_from_extension(extension, ignore_case=False):
    """
    根据文件后缀创建正则表达式模式
    
    Args:
        extension: 文件后缀，如 "jpg", "png" 等
        ignore_case: 是否忽略大小写
        
    Returns:
        tuple: (pattern, flags)
    """
    # 处理多个后缀的情况，如 "jpg,png,gif"
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
    
    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("启用调试模式")
    
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
    print("文件监控重命名脚本 - 修复已编号判断问题")
    print(f"监控文件模式: {pattern}")
    print(f"序号位数: {args.digits}")
    print(f"处理线程数: {args.workers}")
    print(f"缓冲区大小: {args.buffer_size}")
    print(f"批处理大小: {args.batch_size}")
    print(f"批处理超时: {args.batch_timeout}秒")
    print(f"最大文件名长度: {args.max_filename_length}")
    print(f"临时目录: {args.temp_dir}")
    print("按 Ctrl+C 退出")
    print("=" * 50)
    
    # 初始化组件
    graceful_exiter = GracefulExiter()
    
    # 创建文件缓冲区和重命名器
    file_buffer = FileBuffer(
        max_size=args.buffer_size,
        batch_size=args.batch_size,
        batch_timeout=args.batch_timeout
    )
    
    renamer = FileRenamer(
        pattern=pattern, 
        digit_count=args.digits, 
        flags=flags,
        temp_dir=args.temp_dir,
        max_filename_length=args.max_filename_length
    )
    
    # 创建监控处理器
    event_handler = FileMonitorHandler(file_buffer, renamer)
    event_handler.start_event_cleaner()
    
    # 创建批处理器
    batch_processor = BatchFileProcessor(
        file_buffer, 
        renamer, 
        num_workers=args.workers
    )
    batch_processor.start()
    
    # 创建统计报告器
    stats_reporter = StatsReporter(file_buffer, batch_processor, event_handler)
    stats_reporter.start()
    
    # 创建文件监控器
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=False)
    observer.start()
    
    try:
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
        batch_processor.should_stop = True
        stats_reporter.should_stop = True
        observer.stop()
        observer.join()
        
        # 清理临时目录
        if renamer.temp_dir.exists():
            try:
                # 先将临时目录中的文件移回原位置
                for temp_file in renamer.temp_dir.iterdir():
                    if temp_file.is_file():
                        try:
                            original_path = Path.cwd() / temp_file.name
                            temp_file.rename(original_path)
                            logger.info(f"恢复文件: {temp_file.name}")
                        except Exception as e:
                            logger.warning(f"恢复文件 {temp_file.name} 失败: {e}")
                
                shutil.rmtree(renamer.temp_dir)
                logger.info(f"已清理临时目录: {renamer.temp_dir}")
            except Exception as e:
                logger.warning(f"清理临时目录时出错: {e}")
                
        # 输出最终统计
        final_stats = batch_processor.get_stats()
        event_stats = event_handler.get_event_stats()
        
        logger.info(
            f"最终统计 - 已处理: {final_stats['processed']}, "
            f"成功: {final_stats['succeeded']}, "
            f"失败: {final_stats['failed']}, "
            f"批次: {final_stats['batches']}"
        )
        
        # 输出事件统计
        logger.info(
            f"事件统计 - 创建: {event_stats.get('created', 0)}, "
            f"移动: {event_stats.get('moved', 0)}, "
            f"添加到缓冲区: {event_stats.get('added_to_buffer', 0)}"
        )
        
        # 输出跳过统计
        if any(key.startswith('skipped_') for key in event_stats):
            logger.info(
                f"跳过统计 - 文件名过长: {event_stats.get('skipped_too_long', 0)}, "
                f"扩展名不符: {event_stats.get('skipped_wrong_extension', 0)}, "
                f"已编号: {event_stats.get('skipped_already_numbered', 0)}, "
                f"隐藏文件: {event_stats.get('skipped_hidden', 0)}"
            )
        
        logger.info("监控已停止")

if __name__ == "__main__":
    main()