from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from neo4j import GraphDatabase
import time
import json

# 创建Neo4j蓝图
neo4j_bp = Blueprint('neo4j', __name__)

class Neo4jService:
    """Neo4j图数据库服务"""
    
    def __init__(self):
        # Neo4j连接配置 - 从环境变量读取
        import os
        self.NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://10.100.100.93:7687')
        self.NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
        self.NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'zkk123..075')
    
    def get_related_data(self, standard_name):
        """获取标准关联数据"""
        driver = GraphDatabase.driver(
            self.NEO4J_URI, 
            auth=(self.NEO4J_USER, self.NEO4J_PASSWORD)
        )
        nodes = []
        edges = []

        try:
            with driver.session() as session:
                result = session.run("""
                    MATCH (n:Standard)-[r:RELATED]->(m:Standard)
                    WHERE n.name CONTAINS $name
                    RETURN n, r, m
                """, name=standard_name)

                for record in result:
                    n = record["n"]
                    r = record["r"]
                    m = record["m"]

                    nodes.append({
                        "data": {
                            "id": n["name"], 
                            "label": n["name"], 
                            "level": 0
                        }
                    })
                    nodes.append({
                        "data": {
                            "id": m["name"], 
                            "label": m["name"], 
                            "level": 1, 
                            "parent": n["name"]
                        }
                    })
                    
                    relation_type = r["relation"]
                    edges.append({
                        "data": {
                            "id": f"{n['name']}_{m['name']}", 
                            "source": n["name"], 
                            "target": m["name"], 
                            "label": relation_type
                        }
                    })

        finally:
            driver.close()
            
        return {"nodes": nodes, "edges": edges}

# 创建Neo4j服务实例
neo4j_service = Neo4jService()

@neo4j_bp.route('/related-data', methods=['GET'])
@jwt_required()
def get_related_data():
    """获取标准关联数据（需要认证）"""
    start_time = time.time()
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    user_id = get_jwt_identity()
    
    # 记录请求开始
    current_app.logger.info(f"[请求开始] Neo4j关联数据查询 - 用户ID: {user_id} - IP: {client_ip} - User-Agent: {user_agent[:100]}")
    
    try:
        # 获取查询参数
        standard_name = request.args.get('standard_name')
        
        # 记录请求参数
        current_app.logger.info(f"[请求数据] 查询参数: standard_name={standard_name}")
        
        if not standard_name:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.warning(f"[请求失败] 缺少standard_name参数 - 用户ID: {user_id} - IP: {client_ip} - 耗时: {elapsed_time}ms")
            return jsonify({
                'success': False,
                'message': 'standard_name参数是必需的'
            }), 400
        
        # 查询Neo4j数据
        result = neo4j_service.get_related_data(standard_name)
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '标准关联数据查询成功',
            'data': {
                'standard_name': standard_name,
                'nodes_count': len(result['nodes']),
                'edges_count': len(result['edges']),
                'graph_data': result
            }
        }
        
        # 记录成功响应
        current_app.logger.info(f"[请求成功] Neo4j关联数据查询成功 - 用户ID: {user_id} - 标准名称: {standard_name} - 节点数: {len(result['nodes'])} - 边数: {len(result['edges'])} - IP: {client_ip} - 耗时: {elapsed_time}ms")
        current_app.logger.info(f"[响应数据] 查询成功响应: {json.dumps({'success': True, 'nodes_count': len(result['nodes']), 'edges_count': len(result['edges'])}, ensure_ascii=False)}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"[请求失败] Neo4j关联数据查询失败 - 用户ID: {user_id} - 标准名称: {standard_name} - IP: {client_ip} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500

@neo4j_bp.route('/health', methods=['GET'])
@jwt_required()
def neo4j_health():
    """Neo4j连接健康检查（需要认证）"""
    start_time = time.time()
    user_id = get_jwt_identity()
    client_ip = request.remote_addr
    
    current_app.logger.info(f"[请求开始] Neo4j健康检查 - 用户ID: {user_id} - IP: {client_ip}")
    
    try:
        # 测试Neo4j连接
        driver = GraphDatabase.driver(
            neo4j_service.NEO4J_URI, 
            auth=(neo4j_service.NEO4J_USER, neo4j_service.NEO4J_PASSWORD)
        )
        
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            test_value = result.single()["test"]
            
        driver.close()
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': 'Neo4j连接正常',
            'data': {
                'status': 'healthy',
                'connection_test': 'passed',
                'uri': neo4j_service.NEO4J_URI,
                'response_time_ms': elapsed_time
            }
        }
        
        current_app.logger.info(f"[请求成功] Neo4j健康检查通过 - 用户ID: {user_id} - IP: {client_ip} - 耗时: {elapsed_time}ms")
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"[请求失败] Neo4j健康检查失败 - 用户ID: {user_id} - IP: {client_ip} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Neo4j连接失败: {str(e)}',
            'data': {
                'status': 'unhealthy',
                'connection_test': 'failed',
                'uri': neo4j_service.NEO4J_URI
            }
        }), 500 