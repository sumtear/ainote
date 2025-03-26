import asyncio
import hashlib
import json
import os
from os.path import dirname
from typing import Optional, List
from utils.prompts import get_prompts
from config.APIconfig import APIConfig
from openai import AsyncOpenAI
import time
from datetime import datetime, timedelta


class AIHandler:
    """
    AI API 处理器，用于生成缓存文件，向数据中心发送post请求
    """

    def __init__(self, api_key: str, api_base: str, provider: str = "deepseek"):
        if not api_key:
            raise ValueError("API密钥不能为空")

        self.provider = provider  # 定义访问模型
        self.config = APIConfig.get_config(provider=provider)  # 获取相关配置
        # self.client = AsyncOpenAI(api_key=api_key, api_base=api_base or self.config["api_base"])
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base or self.config["api_base"]
        )

        self.cache_dir = os.path.join(dirname(os.path.dirname(__file__)), "cache")
        self.cache_expiry = timedelta(days=7)  # 缓存七天过期
        self._init_cache()

        print(f"初始化AI处理器:{provider}")

    def _init_cache(self):
        """
        初始化缓存目录，在本地建立缓存文件
        """
        try:
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir)
                print(f"创建缓存目录:{self.cache_dir}")

        except Exception as e:
            print(f"缓存目录创建失败:{str(e)}")

    def _get_cache_path(self, prompt_hash: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{prompt_hash}.json")

    def _read_cache(self, prompt_hash: str) -> Optional[str]:
        """读取缓存文件"""
        try:
            cache_path = self._get_cache_path(prompt_hash)
            if not os.path.exists(cache_path):
                return None

            with open(cache_path, "r", encoding="utf-8") as file:
                cache_data = json.load(file)

            cache_time = datetime.fromtimestamp(cache_data["timestamp"])
            if datetime.now() - cache_time > self.cache_expiry:
                os.remove(cache_path)  # 删除过期缓存
                return None
            return cache_data["result"]

        except Exception as e:
            print(f"读取缓存失败:{str(e)}")
            return None

    def _save_cache(self, prompt_hash: str, result: str) -> None:
        """写入缓存"""
        try:
            cache_path = self._get_cache_path(prompt_hash)
            cache_data = {
                'timestamp': time.time(),
                'result': result
            }

            with open(cache_path, "w", encoding="utf-8") as file:
                json.dump(cache_data, file, ensure_ascii=False, indent=2)  # 不使用ascii编码，缩进为2

        except Exception as e:
            print(f"写入缓存失败:{e}")

    async def process_text(self, text: str, prompt_template: str) -> str:
        """处理单个文本块"""
        try:
            if not text or not prompt_template:
                raise ValueError("文本或者提示词不能为空")
            print(f"处理文本块，长度为:{len(text)}")

            prompt = prompt_template.format(text=text) # 格式化提示词

            result = await self.get_completion_with_cache(prompt)

            if not result:
                raise Exception("API返回结果为空")

            print(f"处理完成:结果长度={len(result)}")
            return result

        except Exception as e:
            raise Exception(f"处理文本失败:{str(e)}")

    def _calculate_hash(self, prompt: str, **kwargs) -> str:
        """计算提示词和参数的哈希值"""
        # 将所有参数组合成一个字符串
        params_str = json.dumps(kwargs, sort_keys=True)
        content = f"{prompt}|{params_str}|{self.provider}"
        return hashlib.md5(content.encode()).hexdigest()

    async def get_completion_with_cache(
            self,
            prompt: str,
            max_tokens: int = None,
            temperature: float = None
    ) -> str:
        try:
            cache_key = self._calculate_hash(prompt, max_tokens=max_tokens, temperature=temperature)
            cache_result = self._read_cache(cache_key)
            if cache_result is not None:
                print("使用缓存结果")
                return cache_result

            # 未检测到历史记录，调用API向大模型发送请求
            result = await self.get_completion(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )

            self._save_cache(cache_key, result)

            return result

        except Exception as e:
            print(f"API调用失败:{str(e)}")
            raise

    async def get_completion(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """API响应"""
        try:
            print(f"调用API：provider={self.provider}")  # 添加日记

            # 确保max_tokens的设置
            if self.provider == "deepseek":
                max_tokens = min(max_tokens or self.config["max_tokens"], 4096)
            # TODO elif

            # deepseek:https://platform.deepseek.com
            response = await self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature or self.config["temperature"]
            )
            result = response.choices[0].message.content
            print(f"API调用成功：结果长度为：{len(result)}")
            return result

        except Exception as e:
            # TODO 可以根据官方文档加入更多的错误反馈
            raise Exception(f"API调用失败，错误信息为：{str(e)}")

    async def summarize(
            self,
            chunks: List[str],
            mode: str
    ) -> str:
        """文本处理方法"""
        merged_chunk = []
        current_chunk = ""
        max_size = 3000 if self.provider == "deepseek" else 6000

        for chunk in chunks:
            if len(current_chunk) + len(chunk) < max_size:
                current_chunk += "\n\n" + chunk if current_chunk else chunk
            else:
                if current_chunk:
                    merged_chunk.append(current_chunk)

                current_chunk = chunk

        if current_chunk:
            merged_chunk.append(current_chunk)

        prompts = get_prompts()
        prompt_template = prompts["knowledge_graph_extraction_prompt"]

        total_chunks = len(chunks)
        processed = 0

        async def process_chunk(chunk: str) -> str:
            nonlocal processed
            prompt = f"{prompt_template}\n\n文本内容:\n{chunk}"
            result = await self.get_completion_with_cache(prompt)
            processed += 1
            # TODO
            if self.progress_callback:
                self.progress_callback(processed / total_chunks)
            return result

        # TODO 回来看
        try:
            chunk_summaries = await asyncio.gather(
                *[process_chunk(chunk) for chunk in chunks]
            )
        except Exception as e:
            raise Exception(f"处理文本块失败:{str(e)}")
        # 只有一个块直接返回
        if len(chunk_summaries) == 1:
            return chunk_summaries[0]

        # 合并多个块的总结
        try:
            return await self.merge_summaries(chunk_summaries, prompts["merge_prompt"])
        except Exception as e:
            raise Exception(f"总结失败: {str(e)}")

    async def merge_summaries(
            self,
            summaries: List[str],
            merge_prompt_template: str
    ) -> str:
        """合并策略"""
        if len(summaries) <= 2:
            combined_text = "\n\n".join(summaries)
            return await self._merge_batch(combined_text, merge_prompt_template)

        batch_size = 3
        while len(summaries) > 1:
            new_summaries = []
            # 遍历summaries列表，每次取batch_size个元素
            for i in range(0, len(summaries), batch_size):
                batch = summaries[i:i + batch_size]
                # 如果batch列表长度为1，则直接将元素添加到new_summaries列表中
                if len(batch) == 1:
                    new_summaries.append(batch[0])
                # 否则，将batch列表中的元素合并为一个字符串，并调用_merge_batch方法进行合并
                else:
                    combined_text = f"\n\n".join(batch)
                    merged = await self._merge_batch(combined_text, merge_prompt_template)
                    new_summaries.append(merged)
            summaries = new_summaries
        return summaries[0]

    async def _merge_batch(self, text: str, merge_prompt_template: str) -> str:
        """合并文本"""
        try:
            prompt = f"{merge_prompt_template}\n\n文本内容：\n{text}"
            return await self.get_completion_with_cache(
                prompt,
                max_tokens=min(4096, self.config["max_tokens"])
            )
        except Exception as e:
            raise Exception(f"合并文本失败:{str(e)}")
