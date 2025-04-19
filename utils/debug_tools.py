import os
import time
from utils.logger import logger

def is_dev_mode():
    """判断当前是否为开发模式"""
    return os.getenv("MIXLAB_ENV", "production").lower() == "development"

def profile_function(func):
    """装饰器：用于分析函数的执行时间（仅在开发模式下）"""
    def wrapper(*args, **kwargs):
        if not is_dev_mode():
            return func(*args, **kwargs)
            
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        
        logger.debug(f"函数性能: {func.__name__} 耗时 {elapsed_time:.4f} 秒")
        return result
        
    return wrapper

def memory_usage():
    """获取当前进程的内存使用情况（仅在开发模式下）"""
    if not is_dev_mode():
        return None
        
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        logger.debug(f"内存使用: {memory_mb:.2f} MB")
        return memory_mb
    except ImportError:
        logger.warning("无法获取内存使用信息：需要安装 psutil 库")
        return None
    except Exception as e:
        logger.error(f"获取内存使用信息失败: {str(e)}")
        return None

def debug_context(message):
    """创建一个上下文管理器，用于调试代码块执行时间（仅在开发模式下）"""
    class DebugContext:
        def __init__(self, message):
            self.message = message
            
        def __enter__(self):
            if is_dev_mode():
                self.start_time = time.time()
                logger.debug(f"开始执行: {self.message}")
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            if is_dev_mode():
                elapsed_time = time.time() - self.start_time
                if exc_type:
                    logger.error(f"错误执行: {self.message}, 耗时 {elapsed_time:.4f} 秒, 错误: {exc_type.__name__}: {exc_val}")
                else:
                    logger.debug(f"完成执行: {self.message}, 耗时 {elapsed_time:.4f} 秒")
    
    return DebugContext(message) 