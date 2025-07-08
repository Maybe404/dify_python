#!/usr/bin/env python3
"""
强制修复特定任务的answer字段
使用新的JSON提取方法重新处理answer字段
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.task import TaskResult

def extract_json_from_text(text):
    """从文本中提取JSON内容，处理可能的markdown格式"""
    if not text or not isinstance(text, str):
        return text
    
    # 移除可能的markdown代码块标记
    text = text.strip()
    
    # 处理 ```json ... ``` 格式
    if text.startswith('```json'):
        # 查找结束标记
        end_marker = text.rfind('```')
        if end_marker > 6:  # 确保不是开始的```json
            text = text[7:end_marker].strip()  # 移除```json和结束的```
    elif text.startswith('```'):
        # 处理一般的代码块
        lines = text.split('\n')
        if len(lines) > 2 and lines[-1].strip() == '```':
            text = '\n'.join(lines[1:-1])
    
    return text

def force_fix_task_answer(task_id):
    """强制修复特定任务的answer字段"""
    app = create_app()
    
    with app.app_context():
        print(f"🔧 强制修复任务 {task_id} 的answer字段...")
        
        results = TaskResult.query.filter_by(task_id=task_id).all()
        
        if not results:
            print(f"❌ 任务 {task_id} 没有找到结果记录")
            return
        
        for result in results:
            print(f"\n📋 处理结果记录 {result.id}:")
            
            if result.answer:
                # 使用新的提取方法清理answer
                original_answer = result.answer
                cleaned_answer = extract_json_from_text(original_answer)
                
                print(f"   原始长度: {len(original_answer)} 字符")
                print(f"   清理后长度: {len(cleaned_answer)} 字符")
                
                # 验证清理后的JSON
                try:
                    parsed_data = json.loads(cleaned_answer)
                    if isinstance(parsed_data, list):
                        print(f"   ✅ JSON验证成功: {len(parsed_data)} 条记录")
                        
                        # 更新数据库
                        result.answer = cleaned_answer
                        db.session.commit()
                        print(f"   🎉 更新成功！")
                    else:
                        print(f"   ⚠️  清理后不是列表格式")
                except json.JSONDecodeError as e:
                    print(f"   ❌ 清理后JSON仍无法解析: {e}")
            else:
                print(f"   ⚠️  answer字段为空，跳过")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        force_fix_task_answer(sys.argv[1])
    else:
        print("请提供任务ID: python force_fix_answer.py <task_id>") 