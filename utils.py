# -*- coding: utf-8 -*-
"""
复杂图文逻辑推理挑战赛 - 工具函数
包含图像处理、文本处理、特征提取等功能
"""

import base64
import re
import os
import pandas as pd
import numpy as np
from pathlib import Path
from config import FEATURE_CONFIG

def encode_image_to_base64(image_path):
    """
    将图像文件编码为base64字符串
    
    Args:
        image_path (str): 图像文件路径
        
    Returns:
        str: base64编码的图像数据，如果失败返回None
    """
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        print(f"图像编码失败 {image_path}: {e}")
        return None

def extract_text_features(text):
    """
    从文本中提取特征
    
    Args:
        text (str): 输入文本
        
    Returns:
        dict: 文本特征字典
    """
    if not text:
        return {
            'length': 0,
            'has_number': 0,
            'has_time': 0,
            'has_who': 0,
            'has_why': 0,
            'has_how': 0,
            'has_number_keyword': 0
        }
    
    features = {
        'length': len(text),
        'has_number': 1 if re.search(r'\d+', text) else 0
    }
    
    # 检查关键词
    keywords = FEATURE_CONFIG['question_keywords']
    for category, words in keywords.items():
        feature_name = f'has_{category}'
        features[feature_name] = 1 if any(word in text for word in words) else 0
    
    return features

def extract_description_features(description):
    """
    从图像描述中提取特征
    
    Args:
        description (str): 图像描述文本
        
    Returns:
        dict: 描述特征字典
    """
    if not description:
        return {
            'desc_length': 0,
            'desc_has_number': 0,
            'desc_has_person': 0,
            'desc_has_text': 0,
            'desc_has_color': 0,
            'desc_has_object': 0
        }
    
    features = {
        'desc_length': len(description),
        'desc_has_number': 1 if re.search(r'\d+', description) else 0
    }
    
    # 检查描述关键词
    keywords = FEATURE_CONFIG['description_keywords']
    for category, words in keywords.items():
        feature_name = f'desc_has_{category}'
        features[feature_name] = 1 if any(word in description for word in words) else 0
    
    return features

def extract_knowledge_graph_edges(description):
    """
    从描述中提取知识图谱边
    
    Args:
        description (str): 图像描述文本
        
    Returns:
        list: 知识图谱边列表 [(subject, predicate, object), ...]
    """
    if not description:
        return []
    
    edges = []
    
    # 提取数字关系
    numbers = re.findall(r'\d+(?:\.\d+)?', description)
    for num in numbers:
        edges.append(('图片', '包含数字', num))
    
    # 提取颜色关系
    colors = re.findall(r'(红色|蓝色|绿色|黄色|黑色|白色|灰色|紫色|橙色|粉色)', description)
    for color in colors:
        edges.append(('图片', '包含颜色', color))
    
    # 提取人物关系
    if any(word in description for word in ['人', '男', '女', '人物', '小孩', '成人']):
        edges.append(('图片', '包含', '人物'))
    
    # 提取文字关系
    if any(word in description for word in ['文字', '字', '文本', '标题']):
        edges.append(('图片', '包含', '文字'))
    
    # 提取表格关系
    if any(word in description for word in ['表格', '表', '图表']):
        edges.append(('图片', '包含', '表格'))
    
    # 提取按钮关系
    if '按钮' in description:
        edges.append(('图片', '包含', '按钮'))
    
    return edges

def calculate_jaccard_similarity(str1, str2):
    """
    计算两个字符串的Jaccard相似度
    
    Args:
        str1 (str): 字符串1
        str2 (str): 字符串2
        
    Returns:
        float: Jaccard相似度 (0-1)
    """
    if not str1 or not str2:
        return 0.0
    
    set1 = set(str1)
    set2 = set(str2)
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0

def create_feature_vector(question, description):
    """
    创建特征向量
    
    Args:
        question (str): 问题文本
        description (str): 图像描述
        
    Returns:
        dict: 特征向量字典
    """
    features = {}
    
    # 问题特征
    question_features = extract_text_features(question)
    features.update({f'question_{k}': v for k, v in question_features.items()})
    
    # 描述特征
    desc_features = extract_description_features(description)
    features.update(desc_features)
    
    # 知识图谱特征
    edges = extract_knowledge_graph_edges(description)
    features['kg_edge_count'] = len(edges)
    
    # 交互特征
    features['has_description'] = 1 if description else 0
    features['question_desc_length_ratio'] = (
        features['question_length'] / features['desc_length'] 
        if features['desc_length'] > 0 else 0
    )
    
    return features

def ensure_dir_exists(dir_path):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        dir_path (str): 目录路径
    """
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def load_csv_data(file_path):
    """
    加载CSV数据文件
    
    Args:
        file_path (str): CSV文件路径
        
    Returns:
        pd.DataFrame: 数据框，如果失败返回None
    """
    try:
        return pd.read_csv(file_path, encoding='utf-8')
    except Exception as e:
        print(f"加载CSV文件失败 {file_path}: {e}")
        return None

def save_csv_data(df, file_path):
    """
    保存数据框到CSV文件
    
    Args:
        df (pd.DataFrame): 数据框
        file_path (str): 输出文件路径
    """
    try:
        ensure_dir_exists(os.path.dirname(file_path))
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"数据已保存到: {file_path}")
    except Exception as e:
        print(f"保存CSV文件失败 {file_path}: {e}")

def validate_image_path(image_path, base_dir):
    """
    验证图像路径是否存在
    
    Args:
        image_path (str): 图像相对路径
        base_dir (str): 基础目录
        
    Returns:
        str: 完整的图像路径，如果不存在返回None
    """
    full_path = Path(base_dir) / image_path
    return str(full_path) if full_path.exists() else None

def clean_text(text):
    """
    清理文本，去除多余的空白字符
    
    Args:
        text (str): 输入文本
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""
    
    # 去除多余的空白字符
    text = re.sub(r'\s+', ' ', text.strip())
    return text