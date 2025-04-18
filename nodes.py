# 文件名：nodes.py
import json
import os
import random
import time

class PromptComposerNode:
    @classmethod
    def INPUT_TYPES(cls):
        base_dir = os.path.dirname(__file__)
        config_path = os.path.join(base_dir, "config", "prompt_config.txt")
        group_path = os.path.join(base_dir, "config", "prompt_group.txt")

        with open(config_path, "r", encoding="utf-8") as f:
            prompt_config = json.load(f)
        with open(group_path, "r", encoding="utf-8") as f:
            prompt_group = json.load(f)

        dynamic_inputs = {}
        for key, default_idx in prompt_config.items():
            group = prompt_group.get(key, [])
            options = ["-1:随机"] + [f"{idx}:{v}" if v else f"{idx}:(空)" 
                                    for idx, v in enumerate(group)]
            
            try:
                default = options[default_idx + 1] if default_idx != -1 else options[0]
            except:
                default = options[0]

            dynamic_inputs[key] = (options, {"default": default})

        return {"required": dynamic_inputs}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt")
    FUNCTION = "process"
    CATEGORY = "Prompt"
    # 添加这一行，表示节点需要每次都重新执行
    IS_CHANGED = True

    def process(self, **kwargs):
        # 生成纳秒级随机种子
        random.seed(int(time.time() * 1e9) % 0xFFFFFFFF)
        
        base_dir = os.path.dirname(__file__)
        group_path = os.path.join(base_dir, "config", "prompt_group.txt")
        with open(group_path, "r", encoding="utf-8") as f:
            prompt_group = json.load(f)

        # 统一处理所有参数
        processed_values = {
            key: self._process_param(key, value, prompt_group)
            for key, value in kwargs.items()
        }

        # 构建提示词
        positive = self._build_positive_prompt(processed_values, prompt_group)
        negative = self._build_negative_prompt(processed_values, prompt_group)

        return (
            self._clean_prompt(positive),
            self._clean_prompt(negative)
        )

    def _process_param(self, key, value_str, prompt_group):
        """统一处理每个参数"""
        selected = self._parse_selection(value_str)
        group = prompt_group.get(key, [])
        
        # 处理随机选择
        if selected == -1:
            valid_indices = [i for i, v in enumerate(group) if v.strip()]
            return random.choice(valid_indices) if valid_indices else -1
        return selected if 0 <= selected < len(group) else -1

    def _build_positive_prompt(self, values, prompt_group):
        """构建正面提示词"""
        if values["套装"] > 0:
            return self._get_group_value("套装", values["套装"], prompt_group)
        
        # 处理颜色提示词（独立逻辑）
        color_prompt = None
        if values["颜色"]>0:
            color_prompt=self._get_group_value("颜色", values["颜色"], prompt_group)
        
        # 处理材质提示词（独立逻辑）
        material_prompt = None
        if values["材质"]>0:
            material_prompt=self._get_group_value("材质", values["材质"], prompt_group)

        parts = []
        for key in list(values.keys()):
            if key in ["套装", "负面提示词", "颜色", "材质"]:
                continue
            
            value = self._get_group_value(key, values[key], prompt_group)
            if value:
                if (key == "上装" or key == "下装" ) and values["服装"] > 0:  # 服装不为空（>0），则忽略上装和下装
                    continue

                if (key == "服装" or  key == "上装") and values[key] >1:#服装或者上装不为空（0）不为裸（1），就加上颜色和材质
                    if material_prompt:    
                        value = f"{material_prompt}_" + value
                    if color_prompt:
                        value = f"{color_prompt}_" + value
                parts.append(value)
        
        return ",".join(parts)

    def _build_negative_prompt(self, values, prompt_group):
        """构建负面提示词"""
        return self._get_group_value("负面提示词", values["负面提示词"], prompt_group)

    def _parse_selection(self, selection_str):
        """解析选择值"""
        try:
            return int(selection_str.split(":")[0])
        except:
            return -1

    def _get_group_value(self, key, index, prompt_group):
        """安全获取分组值"""
        if index == -1:
            return ""
        group = prompt_group.get(key, [])
        return group[index].strip() if 0 <= index < len(group) else ""

    def _clean_prompt(self, text):
        """清理提示词格式"""
        return text.strip().strip(",").replace(" ,", ",").replace(",,", ",")

NODE_CLASS_MAPPINGS = {
    "PromptComposer": PromptComposerNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptComposer": "🎲 Prompt Composer"
}