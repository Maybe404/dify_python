#!/usr/bin/env python3
"""
调试answer字段内容
查看实际存储的数据格式
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.task import TaskResult

def debug_answer_content(task_id):
    """调试特定任务的answer内容"""
    app = create_app()
    
    with app.app_context():
        print(f"🔍 调试任务 {task_id} 的answer内容...")
        
        results = TaskResult.query.filter_by(task_id=task_id).all()
        
        if not results:
            print(f"❌ 任务 {task_id} 没有找到结果记录")
            return
        
        for result in results:
            print(f"\n📋 结果记录 {result.id}:")
            
            if result.answer:
                print(f"   answer字段长度: {len(result.answer)} 字符")
                print(f"   answer前100字符: {repr(result.answer[:100])}")
                
                # 尝试不同的解析方法
                print(f"\n🔧 尝试不同的解析方法:")
                
                # 1. 直接解析
                try:
                    data = json.loads(result.answer)
                    print(f"   ✅ 直接JSON解析成功: {type(data)}")
                    if isinstance(data, list):
                        print(f"      列表长度: {len(data)}")
                        if data:
                            print(f"      第一个元素类型: {type(data[0])}")
                            if isinstance(data[0], dict):
                                print(f"      第一个元素字段: {list(data[0].keys())}")
                except json.JSONDecodeError as e:
                    print(f"   ❌ 直接JSON解析失败: {e}")
                
                # 2. 移除markdown标记
                clean_text = result.answer.strip()
                if clean_text.startswith('```json'):
                    end_marker = clean_text.rfind('```')
                    if end_marker > 6:
                        clean_text = clean_text[7:end_marker].strip()
                        
                        print(f"   🧹 清理后长度: {len(clean_text)} 字符")
                        print(f"   🧹 清理后前100字符: {repr(clean_text[:100])}")
                        
                        try:
                            data = json.loads(clean_text)
                            print(f"   ✅ 清理后JSON解析成功: {type(data)}")
                            if isinstance(data, list):
                                print(f"      列表长度: {len(data)}")
                                if data:
                                    print(f"      第一个元素: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
                        except json.JSONDecodeError as e:
                            print(f"   ❌ 清理后JSON解析失败: {e}")
                
                # 3. 查看是否有其他特殊字符
                print(f"\n🔍 字符分析:")
                newline_char = '\n'
                carriage_char = '\r'
                tab_char = '\t'
                print(f"   包含换行符: {newline_char in result.answer}")
                print(f"   包含回车符: {carriage_char in result.answer}")
                print(f"   包含制表符: {tab_char in result.answer}")
                print(f"   以什么开始: {repr(result.answer[:20])}")
                print(f"   以什么结束: {repr(result.answer[-20:])}")
                
            else:
                print(f"   ❌ answer字段为空")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        debug_answer_content(sys.argv[1])
    else:
        print("请提供任务ID: python debug_answer_content.py <task_id>") 