# -*- coding: utf-8 -*-
"""
复杂图文逻辑推理挑战赛 - 配置文件
包含iFLYTEK API认证信息和系统参数
"""

# iFLYTEK API配置
XUNFEI_CONFIG = {
    'app_id': 'your_app_id',
    'api_key': 'your_api_key', 
    'api_secret': 'your_api_secret',
    'base_url': 'wss://spark-api.xf-yun.com/v3.5/chat',
    'domain': 'generalv3.5',
    'temperature': 0.5,
    'max_tokens': 4096
}

# 新的讯飞视觉模型配置
VISION_MODEL_CONFIG = {
    'model_id': 'xqwen2d5s32bvl',
    'resource_id': '0',
    'app_id': '5e0dd074',
    'api_key': 'sk-iBuVfdtBDgb27dhAE25f548fD77a47B086D94dFdBc8a775c',
    'api_url': 'https://maas-api.cn-huabei-1.xf-yun.com/v1',
    'service_name': 'zzs',
    'temperature': 0.1,
    'max_tokens': 2048
}

# 新的讯飞文本模型配置
TEXT_MODEL_CONFIG = {
    'model_id': 'xopgptoss120b',
    'resource_id': '0',
    'app_id': '5e0dd074',
    'api_key': 'sk-iBuVfdtBDgb27dhAE25f548fD77a47B086D94dFdBc8a775c',
    'api_url': 'https://maas-api.cn-huabei-1.xf-yun.com/v1',
    'service_name': 'hinemusk',
    'temperature': 0.1,
    'max_tokens': 1024
}

# 数据路径配置
DATA_PATHS = {
    'train_csv': 'train.csv',
    'test_csv': 'test.csv',
    'sample_submit_csv': 'sample_submit.csv',
    'image_dir': '图像数据集',
    'output_dir': 'output',
    'model_dir': 'models',
    'intermediate_dir': 'intermediate_results',  # 中间结果存储目录
    'vision_results_file': 'vision_understanding.txt'  # 视觉理解结果文件
}

# 模型配置
MODEL_CONFIG = {
    'batch_size': 5,  # API调用批次大小
    'api_delay': 1.0,  # API调用间隔(秒)
    'timeout': 30,  # API超时时间(秒)
    'max_retries': 3,  # 最大重试次数
    'random_state': 42  # 随机种子
}

# 特征工程配置
FEATURE_CONFIG = {
    'question_keywords': {
        'time': ['时间', '日期', '何时', '什么时候', '年', '月', '日'],
        'who': ['谁', '哪个', '哪位', '人'],
        'why': ['为何', '为什么', '原因'],
        'how': ['如何', '怎么', '怎样'],
        'number': ['多少', '几个', '数量']
    },
    'description_keywords': {
        'person': ['人', '男', '女', '人物', '小孩', '成人'],
        'text': ['文字', '字', '文本', '标题', '数字'],
        'color': ['红色', '蓝色', '绿色', '黄色', '黑色', '白色', '灰色', '紫色', '橙色', '粉色'],
        'object': ['表格', '图表', '按钮', '图片', '照片']
    }
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/app.log'
}