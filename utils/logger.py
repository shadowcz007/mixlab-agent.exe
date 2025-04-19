import os
import logging
import sys
from datetime import datetime
import colorama

# 初始化colorama以支持Windows终端中的颜色
colorama.init()

class ColoredFormatter(logging.Formatter):
    """为不同级别的日志添加不同颜色"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': colorama.Fore.CYAN,
        'INFO': colorama.Fore.GREEN,
        'WARNING': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED,
        'CRITICAL': colorama.Fore.RED + colorama.Style.BRIGHT
    }
    
    def format(self, record):
        # 保存原始格式
        format_orig = self._style._fmt
        
        # 根据日志级别添加颜色
        if record.levelname in self.COLORS:
            # 为INFO级别提供一个更简洁的格式
            if record.levelname == 'INFO':
                self._style._fmt = f"{self.COLORS[record.levelname]}%(message)s{colorama.Style.RESET_ALL}"
            else:
                self._style._fmt = f"{self.COLORS[record.levelname]}%(asctime)s - %(name)s - %(levelname)s - %(message)s{colorama.Style.RESET_ALL}"
                
        # 调用原始format方法
        result = logging.Formatter.format(self, record)
        
        # 恢复原始格式
        self._style._fmt = format_orig
        
        return result

class Logger:
    def __init__(self, name="mixlab-agent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 判断是否为开发环境
        self.is_dev = os.getenv("MIXLAB_ENV", "production").lower() == "development"
        
        # 清除现有的handlers（防止重复）
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 创建控制台处理程序
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if self.is_dev else logging.INFO)
        
        # 设置彩色格式
        formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # 添加处理程序
        self.logger.addHandler(console_handler)
        
        # 可选：添加文件处理程序（仅在开发环境）
        if self.is_dev:
            log_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(log_dir, exist_ok=True)
            file_handler = logging.FileHandler(
                os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
            )
            file_handler.setLevel(logging.DEBUG)
            # 文件中使用普通格式（无颜色）
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """仅在开发环境中记录调试信息"""
        if self.is_dev:
            self.logger.debug(message)
    
    def info(self, message):
        """记录一般信息"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告信息"""
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误信息"""
        self.logger.error(message)
    
    def critical(self, message):
        """记录严重错误信息"""
        self.logger.critical(message)
    
    def result(self, message):
        """记录重要结果（使用INFO级别，但有特殊格式）"""
        formatted_message = f"▶ 结果: {message}"
        self.logger.info(formatted_message)

# 创建默认日志记录器实例
logger = Logger() 