class APIConfig:
    # 并发设置
    MAX_CONCURRENT = 5  # 最大并发数
    MAX_RETRIES = 3  # 最大重试次数
    RETRY_DELAY = 0.5  # 重试间隔时间，单位：（second）

    # TODO openai设置

    # deepseek设置,deepseek使用openai包
    DEEPSEEK_MODEL = 'deepseek-chat'  # 定义deepseek模型名称
    DEEPSEEK_TEMPERATURE = 1.0  # 定义温度参数
    DEEPSEEK_MAX_TOKENS = 4096  # 定义最大token

    def get_config( provider: str) -> dict:
        """获取API配置"""
        if provider == 'deepseek':
            return {
                "model": APIConfig.DEEPSEEK_MODEL,
                "temperature": APIConfig.DEEPSEEK_TEMPERATURE,
                "max_tokens": APIConfig.DEEPSEEK_MAX_TOKENS,
                "api_base": "https://api.deepseek.com/v1"
            }
        # TODO elif provider == "openai":
