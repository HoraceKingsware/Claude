"""
配置管理模块
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
    """配置管理类"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置

        Args:
            config_path: 配置文件路径
        """
        # 加载环境变量
        load_dotenv()

        # 加载配置文件
        self.config_path = Path(config_path)
        self._config = self._load_config()

        # 从环境变量覆盖敏感信息
        self._override_from_env()

    def _load_config(self) -> Dict[str, Any]:
        """加载YAML配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _override_from_env(self):
        """从环境变量覆盖配置"""
        # 登录信息
        if os.getenv('MEITUAN_USERNAME'):
            self._config['login']['username'] = os.getenv('MEITUAN_USERNAME')
        if os.getenv('MEITUAN_PASSWORD'):
            self._config['login']['password'] = os.getenv('MEITUAN_PASSWORD')

        # Claude API密钥
        if os.getenv('ANTHROPIC_API_KEY'):
            if 'claude' not in self._config['captcha']:
                self._config['captcha']['claude'] = {}
            self._config['captcha']['claude']['api_key'] = os.getenv('ANTHROPIC_API_KEY')

    def get(self, *keys, default=None):
        """
        获取配置值

        Args:
            *keys: 配置键路径，如 'browser', 'type'
            default: 默认值

        Returns:
            配置值
        """
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @property
    def login_url(self) -> str:
        """获取登录URL"""
        return self.get('login', 'url')

    @property
    def username(self) -> str:
        """获取用户名"""
        return self.get('login', 'username', default='')

    @property
    def password(self) -> str:
        """获取密码"""
        return self.get('login', 'password', default='')

    @property
    def browser_type(self) -> str:
        """获取浏览器类型"""
        return self.get('browser', 'type', default='chromium')

    @property
    def headless(self) -> bool:
        """是否无头模式"""
        return self.get('browser', 'headless', default=False)

    @property
    def viewport(self) -> Dict[str, int]:
        """获取视口大小"""
        return self.get('browser', 'viewport', default={'width': 1920, 'height': 1080})

    @property
    def user_data_dir(self) -> str:
        """获取用户数据目录"""
        return self.get('browser', 'user_data_dir', default='./browser_data')

    @property
    def stealth_mode(self) -> bool:
        """是否启用隐身模式"""
        return self.get('anti_crawler', 'stealth_mode', default=True)

    @property
    def random_user_agent(self) -> bool:
        """是否随机User-Agent"""
        return self.get('anti_crawler', 'random_user_agent', default=True)

    @property
    def delay_range(self) -> Dict[str, float]:
        """获取延迟范围"""
        return self.get('anti_crawler', 'delay_range', default={'min': 1.0, 'max': 3.0})

    @property
    def human_behavior(self) -> bool:
        """是否模拟人类行为"""
        return self.get('anti_crawler', 'human_behavior', default=True)

    @property
    def captcha_provider(self) -> str:
        """验证码识别提供商"""
        return self.get('captcha', 'provider', default='claude')

    @property
    def claude_config(self) -> Dict[str, Any]:
        """Claude配置"""
        return self.get('captcha', 'claude', default={})

    @property
    def log_level(self) -> str:
        """日志级别"""
        return self.get('logging', 'level', default='INFO')

    @property
    def log_file(self) -> str:
        """日志文件路径"""
        return self.get('logging', 'file', default='./logs/meituan_login.log')
