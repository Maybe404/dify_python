#!/usr/bin/env python3
"""
验证分页查询和Excel导出接口支持的任务类型是否一致
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def extract_supported_types_from_code():
    """从代码中提取支持的任务类型"""
    
    # 从TaskService中提取分页查询支持的类型
    task_service_file = "app/services/task_service.py"
    paginated_types = None
    
    try:
        with open(task_service_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 查找pagination_supported_types
        for line in content.split('\n'):
            line = line.strip()
            if 'pagination_supported_types' in line and '=' in line:
                # 提取类型列表
                start = line.find('[')
                end = line.find(']')
                if start != -1 and end != -1:
                    types_str = line[start+1:end]
                    # 移除引号和空格，分割类型
                    types = [t.strip().strip("'\"") for t in types_str.split(',') if t.strip()]
                    paginated_types = types
                    break
    except Exception as e:
        print(f"❌ 读取TaskService文件失败: {e}")
        return None, None
    
    # 从模型中提取所有定义的任务类型
    task_model_file = "app/models/task.py"
    all_task_types = None
    
    try:
        with open(task_model_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 查找任务类型枚举定义
        for line in content.split('\n'):
            line = line.strip()
            if 'task_type = db.Column(db.Enum(' in line:
                # 提取枚举值
                start = line.find('(') + 1
                end = line.find(')', start)
                if start != -1 and end != -1:
                    types_str = line[start:end]
                    # 移除引号和空格，分割类型
                    types = []
                    for part in types_str.split(','):
                        part = part.strip().strip("'\"")
                        if part and not part.startswith('standard_') == False:
                            if part.startswith('standard_'):
                                types.append(part)
                    all_task_types = types
                    break
    except Exception as e:
        print(f"❌ 读取Task模型文件失败: {e}")
        return None, None
    
    return paginated_types, all_task_types

def check_documentation_consistency():
    """检查文档中的任务类型描述是否一致"""
    api_doc_file = "docs/api.md"
    
    try:
        with open(api_doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找分页查询接口的支持类型
        paginated_section_types = []
        excel_section_types = []
        
        lines = content.split('\n')
        in_paginated_section = False
        in_excel_section = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 检测分页查询接口段落
            if 'results/paginated' in line and '接口' in line:
                in_paginated_section = True
                in_excel_section = False
                continue
            
            # 检测Excel导出接口段落
            if 'results/export-excel' in line and '接口' in line:
                in_excel_section = True
                in_paginated_section = False
                continue
            
            # 如果遇到新的接口段落，重置状态
            if '### ' in line or '## ' in line:
                if not ('结果' in line or 'Excel' in line or 'paginated' in line):
                    in_paginated_section = False
                    in_excel_section = False
            
            # 提取支持的任务类型
            if line.startswith('- `standard_') and line.endswith('`'):
                task_type = line.split('`')[1]
                if in_paginated_section:
                    paginated_section_types.append(task_type)
                elif in_excel_section:
                    excel_section_types.append(task_type)
        
        return paginated_section_types, excel_section_types
        
    except Exception as e:
        print(f"❌ 读取API文档失败: {e}")
        return None, None

def main():
    """主函数"""
    print("="*60)
    print("任务类型一致性验证工具")
    print("="*60)
    
    # 检查代码中的定义
    print("\n🔍 检查代码中的任务类型定义...")
    paginated_types, all_task_types = extract_supported_types_from_code()
    
    if paginated_types:
        print(f"✅ 分页查询支持的类型: {paginated_types}")
    else:
        print("❌ 无法提取分页查询支持的类型")
        
    if all_task_types:
        print(f"✅ 模型中定义的所有任务类型: {all_task_types}")
    else:
        print("❌ 无法提取模型中的任务类型")
    
    # 检查文档中的描述
    print("\n📖 检查API文档中的类型描述...")
    doc_paginated_types, doc_excel_types = check_documentation_consistency()
    
    if doc_paginated_types:
        print(f"✅ 文档中分页查询支持的类型: {doc_paginated_types}")
    else:
        print("❌ 无法提取文档中分页查询的支持类型")
        
    if doc_excel_types:
        print(f"✅ 文档中Excel导出支持的类型: {doc_excel_types}")
    else:
        print("❌ 无法提取文档中Excel导出的支持类型")
    
    # 一致性检查
    print("\n🔍 一致性验证...")
    issues = []
    
    # 检查代码和文档中分页查询类型是否一致
    if paginated_types and doc_paginated_types:
        if set(paginated_types) == set(doc_paginated_types):
            print("✅ 代码和文档中的分页查询支持类型一致")
        else:
            issues.append("代码和文档中的分页查询支持类型不一致")
            print("❌ 代码和文档中的分页查询支持类型不一致")
            print(f"   代码: {paginated_types}")
            print(f"   文档: {doc_paginated_types}")
    
    # 检查文档中两个接口的支持类型是否一致
    if doc_paginated_types and doc_excel_types:
        if set(doc_paginated_types) == set(doc_excel_types):
            print("✅ 文档中分页查询和Excel导出支持类型一致")
        else:
            issues.append("文档中分页查询和Excel导出支持类型不一致")
            print("❌ 文档中分页查询和Excel导出支持类型不一致")
            print(f"   分页查询: {doc_paginated_types}")
            print(f"   Excel导出: {doc_excel_types}")
    
    # 验证指定的三个类型是否正确
    expected_types = ['standard_review', 'standard_recommendation', 'standard_compliance']
    
    if paginated_types:
        if set(paginated_types) == set(expected_types):
            print("✅ 分页查询支持的类型符合预期")
        else:
            issues.append("分页查询支持的类型不符合预期")
            print("❌ 分页查询支持的类型不符合预期")
            print(f"   实际: {paginated_types}")
            print(f"   预期: {expected_types}")
    
    # 验证这些类型在模型中是否都存在
    if all_task_types and expected_types:
        missing_types = [t for t in expected_types if t not in all_task_types]
        if not missing_types:
            print("✅ 所有预期的任务类型在模型中都已定义")
        else:
            issues.append(f"以下任务类型在模型中未定义: {missing_types}")
            print(f"❌ 以下任务类型在模型中未定义: {missing_types}")
    
    # 总结
    print("\n" + "="*60)
    if not issues:
        print("🎉 所有检查通过！任务类型定义一致")
        print("✅ 分页查询和Excel导出接口支持相同的任务类型")
        print("✅ 代码实现和文档描述保持一致")
        print("✅ 支持的任务类型符合预期")
    else:
        print("⚠️  发现以下问题:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print("\n建议检查并修复上述问题以保证一致性")
    
    print("="*60)
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 