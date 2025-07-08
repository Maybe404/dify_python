#!/usr/bin/env python3
"""
修复任务结果数据中的answer字段
从full_response.data.outputs中提取数据到answer字段
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

def fix_answer_fields():
    """修复answer字段为空的TaskResult记录"""
    app = create_app()
    
    with app.app_context():
        print("🔍 开始检查需要修复的任务结果...")
        
        # 查找answer为空但full_response有数据的记录
        records_to_fix = TaskResult.query.filter(
            TaskResult.answer.is_(None),
            TaskResult.full_response.isnot(None)
        ).all()
        
        print(f"📋 找到 {len(records_to_fix)} 条需要修复的记录")
        
        fixed_count = 0
        error_count = 0
        
        for record in records_to_fix:
            try:
                print(f"\n🔧 处理记录 {record.id} (任务: {record.task_id})")
                
                # 解析full_response
                full_data = json.loads(record.full_response)
                
                # 提取answer内容
                answer_content = None
                data_source = None
                
                # 尝试从不同位置提取数据
                outputs = None
                if 'data' in full_data and 'outputs' in full_data['data']:
                    outputs = full_data['data']['outputs']
                    data_source = "data.outputs"
                elif 'outputs' in full_data:
                    outputs = full_data['outputs']
                    data_source = "outputs"
                
                if outputs:
                    # 尝试从不同字段提取内容
                    for field_name in ['审查意见', 'answer', 'result', 'content']:
                        if field_name in outputs:
                            if isinstance(outputs[field_name], str):
                                # 处理可能的markdown格式
                                answer_content = extract_json_from_text(outputs[field_name])
                                print(f"   ✅ 从 {data_source}.{field_name} 提取到数据")
                                break
                            elif outputs[field_name]:  # 非空的其他类型
                                answer_content = json.dumps(outputs[field_name], ensure_ascii=False)
                                print(f"   ✅ 从 {data_source}.{field_name} 提取到数据（JSON序列化）")
                                break
                    
                    # 如果上述字段都没有，尝试获取第一个有效的字符串字段
                    if not answer_content:
                        for key, value in outputs.items():
                            if isinstance(value, str) and value.strip():
                                answer_content = extract_json_from_text(value)
                                print(f"   ✅ 从 {data_source}.{key} 提取到数据")
                                break
                
                if answer_content:
                    # 更新记录
                    record.answer = answer_content
                    db.session.commit()
                    fixed_count += 1
                    print(f"   🎉 修复成功！内容长度: {len(answer_content)} 字符")
                    
                    # 验证修复后的数据（对于分页类型）
                    if record.task and record.task.task_type in ['standard_review', 'standard_recommendation', 'standard_compliance']:
                        try:
                            parsed_data = json.loads(answer_content)
                            if isinstance(parsed_data, list):
                                print(f"   📊 分页数据验证成功: {len(parsed_data)} 条记录")
                            else:
                                print(f"   ⚠️  数据不是列表格式，但已修复answer字段")
                        except json.JSONDecodeError:
                            print(f"   ⚠️  answer内容不是有效JSON，但已修复字段")
                else:
                    print(f"   ❌ 未能从full_response中提取到有效数据")
                    error_count += 1
                    
            except Exception as e:
                print(f"   💥 处理记录 {record.id} 时出错: {str(e)}")
                error_count += 1
        
        print(f"\n📈 修复完成统计:")
        print(f"   ✅ 成功修复: {fixed_count} 条")
        print(f"   ❌ 处理失败: {error_count} 条")
        print(f"   📊 总计处理: {len(records_to_fix)} 条")

def verify_specific_task(task_id):
    """验证特定任务的修复情况"""
    app = create_app()
    
    with app.app_context():
        print(f"🔍 检查任务 {task_id} 的结果...")
        
        results = TaskResult.query.filter_by(task_id=task_id).all()
        
        if not results:
            print(f"❌ 任务 {task_id} 没有找到结果记录")
            return
        
        for result in results:
            print(f"\n📋 结果记录 {result.id}:")
            print(f"   answer字段: {'有数据' if result.answer else '空'}")
            if result.answer:
                print(f"   answer长度: {len(result.answer)} 字符")
                
                # 如果是支持分页的任务类型，尝试解析
                if result.task and result.task.task_type in ['standard_review', 'standard_recommendation', 'standard_compliance']:
                    try:
                        parsed_data = json.loads(result.answer)
                        if isinstance(parsed_data, list):
                            print(f"   📊 分页数据: {len(parsed_data)} 条记录")
                            if parsed_data:
                                first_item = parsed_data[0]
                                required_fields = ['sn', 'issueLocation', 'originalText', 'issueDescription', 'recommendedModification']
                                missing_fields = [field for field in required_fields if field not in first_item]
                                if missing_fields:
                                    print(f"   ⚠️  缺少字段: {missing_fields}")
                                else:
                                    print(f"   ✅ 数据格式验证通过")
                        else:
                            print(f"   ⚠️  数据不是列表格式")
                    except json.JSONDecodeError:
                        print(f"   ❌ JSON解析失败")
            
            print(f"   full_response: {'有数据' if result.full_response else '空'}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        if len(sys.argv) > 2:
            # 验证特定任务
            verify_specific_task(sys.argv[2])
        else:
            print("请提供任务ID: python fix_answer_field.py verify <task_id>")
    else:
        # 修复所有记录
        fix_answer_fields() 