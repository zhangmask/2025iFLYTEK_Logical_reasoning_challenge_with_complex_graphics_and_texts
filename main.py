# -*- coding: utf-8 -*-
"""
复杂图文逻辑推理挑战赛 - 两阶段推理主程序
第一阶段：使用讯飞视觉模型理解图像
第二阶段：使用讯飞文本模型进行推理
"""

import os
import json
import time
import requests
import pandas as pd
from tqdm import tqdm
from datetime import datetime

from config import XUNFEI_CONFIG, DATA_PATHS, MODEL_CONFIG, VISION_MODEL_CONFIG, TEXT_MODEL_CONFIG
from utils import *

class XunfeiVisionAPI:
    """
    讯飞视觉模型API客户端 (xqwen2d5s32bvl)
    """
    
    def __init__(self):
        self.api_key = VISION_MODEL_CONFIG['api_key']
        self.api_url = VISION_MODEL_CONFIG['api_url']
        self.model_id = VISION_MODEL_CONFIG['model_id']
        
    def understand_image(self, image_base64, question):
        """
        使用视觉模型理解图像
        
        Args:
            image_base64 (str): base64编码的图像
            question (str): 问题文本
            
        Returns:
            str: 图像理解结果，失败返回None
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 构建详细的提示词，要求模型进行深度图像理解
        prompt = f"""
请仔细观察这张图片，并进行详细的分析和理解：

1. 图片内容描述：
   - 详细描述图片中的所有可见元素（文字、数字、图形、颜色、人物、物体等）
   - 分析图片的布局和结构
   - 识别图片中的关键信息

2. 逻辑关系分析：
   - 分析图片中各元素之间的关系
   - 识别可能的逻辑模式或规律
   - 理解图片要表达的含义

3. 问题相关性：
   问题：{question}
   - 分析问题与图片内容的关联性
   - 识别回答问题所需的关键信息
   - 进行初步的逻辑推理

请提供详细、准确的分析结果，这将用于后续的推理过程。
"""
        
        data = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        try:
            print(f"正在调用视觉API: {self.api_url}/chat/completions")
            print(f"使用模型: {self.model_id}")
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            print(f"API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    print(f"API响应格式错误: {result}")
                    return "图像理解失败"
            else:
                print(f"API调用失败，状态码: {response.status_code}")
                response_text = response.text
                print(f"响应内容: {response_text[:200]}...")  # 只打印前200字符
                
                # 检查是否是内容审核错误
                if "相关法律法规" in response_text or "内容审核" in response_text:
                    print("遇到内容审核限制，跳过此图片")
                    return "内容审核限制，无法处理此图片"
                
                return "图像理解失败"
                
        except Exception as e:
            print(f"视觉API调用异常: {str(e)}")
            return "API调用异常，无法处理此图片"

class XunfeiTextAPI:
    """
    讯飞文本模型API客户端 (xopgptoss120b)
    """
    
    def __init__(self):
        self.api_key = TEXT_MODEL_CONFIG['api_key']
        self.api_url = TEXT_MODEL_CONFIG['api_url']
        self.model_id = TEXT_MODEL_CONFIG['model_id']
        
    def reason_with_text(self, image_understanding, question):
        """
        基于图像理解结果进行文本推理
        
        Args:
            image_understanding (str): 第一阶段的图像理解结果
            question (str): 问题文本
            
        Returns:
            str: 推理结果答案，失败返回None
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 构建推理提示词
        prompt = f"""
基于以下图像理解结果，请回答问题：

图像理解结果：
{image_understanding}

问题：{question}

请根据图像理解结果中的信息，进行逻辑推理并给出准确答案。

要求：
1. 仔细分析图像理解结果中的关键信息
2. 结合问题进行逻辑推理
3. 给出简洁明确的答案
4. 只输出最终答案，不要解释过程

答案：
"""
        
        data = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        try:
            print(f"正在调用文本API: {self.api_url}/chat/completions")
            print(f"使用模型: {self.model_id}")
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            print(f"API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content'].strip()
                    # 清理答案，只保留核心内容
                    if '答案：' in answer:
                        answer = answer.split('答案：')[-1].strip()
                    return answer
                else:
                    print(f"文本推理API响应格式错误: {result}")
                    return "A"  # 默认返回A
            else:
                print(f"文本推理API调用失败，状态码: {response.status_code}")
                response_text = response.text
                print(f"响应内容: {response_text[:200]}...")  # 只打印前200字符
                
                # 检查是否是内容审核错误
                if "相关法律法规" in response_text or "内容审核" in response_text:
                    print("遇到内容审核限制，返回默认答案")
                
                return "A"  # 默认返回A
                
        except Exception as e:
            print(f"文本API调用异常: {str(e)}")
            return "A"  # 默认返回A

class TwoStageReasoner:
    """
    两阶段推理器
    """
    
    def __init__(self):
        self.vision_api = XunfeiVisionAPI()
        self.text_api = XunfeiTextAPI()
        
    def stage1_vision_understanding(self, df, image_dir):
        """
        第一阶段：视觉理解
        
        Args:
            df (pd.DataFrame): 数据框
            image_dir (str): 图像目录
            
        Returns:
            dict: {id: understanding_result}
        """
        understanding_results = {}
        intermediate_file = os.path.join(DATA_PATHS['intermediate_dir'], 'vision_understanding.txt')
        
        # 确保中间结果目录存在
        ensure_dir_exists(DATA_PATHS['intermediate_dir'])
        
        print("第一阶段：开始视觉理解...")
        
        with open(intermediate_file, 'w', encoding='utf-8') as f:
            f.write(f"视觉理解结果 - {datetime.now()}\n")
            f.write("=" * 50 + "\n\n")
            
            for idx, row in tqdm(df.iterrows(), total=len(df), desc="视觉理解"):
                image_path = validate_image_path(row['image'], image_dir)
                
                if not image_path:
                    result = f"错误：图像文件不存在 - {row['image']}"
                    understanding_results[row['id']] = result
                    f.write(f"ID: {row['id']}\n")
                    f.write(f"图像: {row['image']}\n")
                    f.write(f"问题: {row['question']}\n")
                    f.write(f"理解结果: {result}\n")
                    f.write("-" * 30 + "\n\n")
                    continue
                
                # 编码图像
                image_base64 = encode_image_to_base64(image_path)
                if not image_base64:
                    result = "错误：图像编码失败"
                    understanding_results[row['id']] = result
                    f.write(f"ID: {row['id']}\n")
                    f.write(f"图像: {row['image']}\n")
                    f.write(f"问题: {row['question']}\n")
                    f.write(f"理解结果: {result}\n")
                    f.write("-" * 30 + "\n\n")
                    continue
                
                # 调用视觉API
                understanding = self.vision_api.understand_image(image_base64, row['question'])
                
                # 保存结果（无论成功失败都保存）
                understanding_results[row['id']] = understanding
                f.write(f"ID: {row['id']}\n")
                f.write(f"图像: {row['image']}\n")
                f.write(f"问题: {row['question']}\n")
                f.write(f"理解结果: {understanding}\n")
                f.write("-" * 30 + "\n\n")
                
                # 检查是否有问题
                if "失败" in understanding or "限制" in understanding or "异常" in understanding:
                    print(f"图像 {row['id']} 处理有问题: {understanding[:50]}...")
                
                # API调用间隔
                time.sleep(MODEL_CONFIG['api_delay'])
                
                # 实时刷新文件
                f.flush()
        
        print(f"第一阶段完成，结果已保存到: {intermediate_file}")
        return understanding_results
    
    def stage2_text_reasoning(self, df, understanding_results):
        """
        第二阶段：文本推理
        
        Args:
            df (pd.DataFrame): 数据框
            understanding_results (dict): 第一阶段的理解结果
            
        Returns:
            pd.DataFrame: 预测结果
        """
        predictions = []
        
        print("第二阶段：开始文本推理...")
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="文本推理"):
            understanding = understanding_results.get(row['id'], "无图像理解结果")
            
            if understanding.startswith("错误："):
                # 如果第一阶段失败，使用默认答案
                answer = "A"  # 默认答案
            else:
                # 调用文本推理API
                answer = self.text_api.reason_with_text(understanding, row['question'])
                
                if not answer:
                    answer = "A"  # 默认答案
            
            predictions.append({
                'id': row['id'],
                'answer': answer
            })
            
            # API调用间隔
            time.sleep(MODEL_CONFIG['api_delay'])
        
        return pd.DataFrame(predictions)

def main():
    """
    主函数 - 两阶段推理流程
    """
    print("=== 复杂图文逻辑推理挑战赛 - 两阶段推理 ===")
    
    # 初始化推理器
    reasoner = TwoStageReasoner()
    
    # 加载训练数据（用于第一阶段理解，可选）
    print("\n1. 加载训练数据...")
    train_df = load_csv_data(DATA_PATHS['train_csv'])
    if train_df is not None:
        print(f"训练数据: {len(train_df)} 条")
        
        # 可选：对部分训练数据进行视觉理解以验证流程
        print("\n2. 处理部分训练数据（验证流程）...")
        train_sample = train_df.head(5)  # 只处理5条验证流程
        train_understanding = reasoner.stage1_vision_understanding(
            train_sample, DATA_PATHS['image_dir']
        )
        print("训练数据视觉理解完成")
    
    # 加载测试数据
    print("\n3. 加载测试数据...")
    test_df = load_csv_data(DATA_PATHS['test_csv'])
    if test_df is None:
        print("测试数据加载失败")
        return
    
    print(f"测试数据: {len(test_df)} 条")
    
    # 第一阶段：视觉理解
    print("\n4. 第一阶段：视觉理解...")
    understanding_results = reasoner.stage1_vision_understanding(
        test_df, DATA_PATHS['image_dir']
    )
    
    # 第二阶段：文本推理
    print("\n5. 第二阶段：文本推理...")
    predictions_df = reasoner.stage2_text_reasoning(test_df, understanding_results)
    
    # 保存结果
    ensure_dir_exists(DATA_PATHS['output_dir'])
    output_path = os.path.join(DATA_PATHS['output_dir'], 'submission.csv')
    save_csv_data(predictions_df, output_path)
    
    print(f"\n两阶段推理完成！结果已保存到: {output_path}")
    print(f"预测样本数: {len(predictions_df)}")
    
    # 显示预测结果示例
    print("\n预测结果示例:")
    print(predictions_df.head(10))
    
    # 统计答案分布
    print("\n答案分布:")
    print(predictions_df['answer'].value_counts())

if __name__ == "__main__":
    main()