#!/usr/bin/env python3
"""
检查Flask应用的路由配置
"""

from app import create_app

def main():
    """检查应用路由"""
    print("="*60)
    print("检查Flask应用路由配置")
    print("="*60)
    
    try:
        # 创建应用实例
        app = create_app()
        
        print(f"\n应用名称: {app.name}")
        print(f"注册的蓝图数量: {len(app.blueprints)}")
        print(f"蓝图列表: {list(app.blueprints.keys())}")
        
        # 获取所有路由
        print(f"\n所有注册的路由:")
        print("-" * 60)
        
        with app.app_context():
            routes = []
            for rule in app.url_map.iter_rules():
                methods = ', '.join(rule.methods - {'OPTIONS', 'HEAD'})
                routes.append((rule.rule, methods, rule.endpoint))
            
            # 按路径排序
            routes.sort()
            
            # 过滤出dify相关的路由
            dify_routes = []
            other_routes = []
            
            for route, methods, endpoint in routes:
                if '/dify/' in route:
                    dify_routes.append((route, methods, endpoint))
                else:
                    other_routes.append((route, methods, endpoint))
            
            print(f"Dify相关路由 ({len(dify_routes)} 个):")
            print("-" * 40)
            for route, methods, endpoint in dify_routes:
                print(f"  {methods:15} {route:50} -> {endpoint}")
            
            print(f"\n其他路由 ({len(other_routes)} 个):")
            print("-" * 40)
            for route, methods, endpoint in other_routes:
                print(f"  {methods:15} {route:50} -> {endpoint}")
            
            # 检查我们期望的新路由是否存在
            print(f"\n" + "="*60)
            print("检查新增的会话操作路由")
            print("="*60)
            
            expected_routes = [
                'POST /api/dify/v2/<scenario>/conversations/<conversation_id>/name',
                'DELETE /api/dify/v2/<scenario>/conversations/<conversation_id>'
            ]
            
            for expected in expected_routes:
                found = False
                for route, methods, endpoint in dify_routes:
                    # 简化匹配（忽略具体的场景名称）
                    if 'conversations' in route and 'name' in route and 'POST' in methods:
                        if expected.startswith('POST') and '/name' in expected:
                            found = True
                            print(f"  ✅ 找到重命名路由: {methods} {route}")
                            break
                    elif 'conversations' in route and 'name' not in route and 'DELETE' in methods:
                        if expected.startswith('DELETE') and '/name' not in expected:
                            found = True
                            print(f"  ✅ 找到删除路由: {methods} {route}")
                            break
                
                if not found:
                    print(f"  ❌ 未找到路由: {expected}")
        
    except Exception as e:
        print(f"❌ 检查路由时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 