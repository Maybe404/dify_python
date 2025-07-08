from flask import Flask, jsonify, request
from neo4j import GraphDatabase
import json

app = Flask(__name__)

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "zkk123..075"

def get_related_data(standard_name):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    nodes = []
    edges = []

    with driver.session() as session:
        result = session.run("""
            MATCH (n:Standard)-[r:RELATED]->(m:Standard)
            WHERE n.name = $name
            RETURN n, r, m
        """, name=standard_name)

        for record in result:
            n = record["n"]
            r = record["r"]
            m = record["m"]

            nodes.append({"data": {"id": n["name"], "label": n["name"], "level": 0}})
            nodes.append({"data": {"id": m["name"], "label": m["name"], "level": 1, "parent": n["name"]}})
            relation_type = r["relation"]
            edges.append({"data": {"id": f"{n['name']}_{m['name']}", "source": n["name"], "target": m["name"], "label": relation_type}})

    driver.close()
    return {"nodes": nodes, "edges": edges}

@app.route('/get_related_data', methods=['GET'])
def related_data():
    # 获取标准名称的查询参数
    standard_name = request.args.get('standard_name')
    if not standard_name:
        return jsonify({"error": "standard_name 参数缺失"}), 400

    try:
        result = get_related_data(standard_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3020)
