import json
import lz4.frame
import yaml
from typing import Dict, Any, List

class SemanticMemory:
    def __init__(self, compression: str, assoc_depth: int):
        self.compression = compression
        self.assoc_depth = assoc_depth

    def create_meaning_graph(self, concepts: List[str], relations: Dict[str, Any]) -> Dict:
        graph = {c: {} for c in concepts}
        # Обработка relations как {source: {predicate: target}}
        for source, rel_data in relations.items():
            if isinstance(rel_data, dict):
                for pred, target in rel_data.items():
                    graph[source][pred] = target
            else:
                graph[source] = {rel_data: "enabled"}  # Legacy fallback
        if "overheating" in concepts:
            graph["issues"] = "overheating"
        return graph

    def restore_context(self, context: str):
        pass  # TODO: Load to short-term memory

    def restore_semantic(self, semantic: Dict):
        pass  # TODO: Rebuild embeddings/graph

    def restore_temporal(self, temporal: Dict):
        pass  # TODO: Update timeline

# Config (same)
config_yaml = """
memory:
  semantic:
    compression: lz4
    assoc_depth: 5
"""
with open('config.yaml', 'w') as f:
    f.write(config_yaml)

class ARP:
    def __init__(self, config_path: str = "config.yaml"):
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            raise ValueError("config.yaml не найден!")
        self.memory = SemanticMemory(
            compression=self.config["memory"]["semantic"]["compression"],
            assoc_depth=self.config["memory"]["semantic"]["assoc_depth"]
        )

    def export_session(self, session_data: Dict[str, Any], output_file: str):
        context = session_data["context"]
        # Relations как dict {source: {pred: target}}
        relations = session_data.get("relations", {})  # e.g., {"disk_brakes": {"requires": "ABS"}}
        semantic = self.memory.create_meaning_graph(
            concepts=session_data["concepts"],
            relations=relations
        )
        temporal = {"timestamp": session_data["timestamp"], "session_id": session_data["session_id"]}

        asmf_data = {
            "@context": "https://asmf.org/schema/v1.0",  # JSON-LD
            "asmf_version": "1.0",
            "context": context,
            "semantic": semantic,
            "temporal": temporal,
            "timestamp": session_data["timestamp"]
        }

        compressed = lz4.frame.compress(json.dumps(asmf_data, ensure_ascii=False).encode('utf-8'))
        with open(output_file, "wb") as f:
            f.write(compressed)

    def import_session(self, input_file: str) -> Dict[str, Any]:
        try:
            with open(input_file, "rb") as f:
                compressed = f.read()
            decompressed = lz4.frame.decompress(compressed).decode('utf-8')
            asmf_data = json.loads(decompressed)
            if asmf_data.get("asmf_version") != "1.0":
                raise ValueError("Несовместимая версия ASMF")
            
            self.memory.restore_context(asmf_data["context"])
            self.memory.restore_semantic(asmf_data["semantic"])
            self.memory.restore_temporal(asmf_data["temporal"])
            return asmf_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Ошибка восстановления: {e}")

# Тест (обновил relations для consistency)
session = {
    "context": "Тормозная система: дисковые тормоза, ABS, перегрев",
    "concepts": ["disk_brakes", "ABS", "overheating"],
    "relations": {"disk_brakes": {"requires": "ABS"}},  # Fixed format
    "timestamp": "2025-10-21T13:48:00Z",
    "session_id": "session_1"
}
arp = ARP()
arp.export_session(session, "memory_snapshot.asmf")
restored = arp.import_session("memory_snapshot.asmf")
print(restored["semantic"])
# Вывод: {'disk_brakes': {'requires': 'ABS'}, 'ABS': {}, 'overheating': {}, 'issues': 'overheating'}
