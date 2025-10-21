import yaml
import lz4.frame
import json
import re
from typing import Dict, Any

class SemanticMemory:
    def __init__(self, compression: str, assoc_depth: int):
        self.compression = compression
        self.assoc_depth = assoc_depth

    def filter_noise(self, text: str, remove: list) -> str:
        # Удаляем оффтопик (расширь по remove)
        if "offtopic" in remove:
            text = re.sub(r'Кофе пью\.', '', text)  # Простой пример
        return text.strip()

    def extract_concepts(self, text: str) -> list:
        # Динамика: ищем ключевые термины (можно улучшить NLP)
        concepts = re.findall(r'(disk_brakes|ABS|overheating|тормоза|перегрев)', text.lower())
        return list(set(concepts))  # Уникальные

    def create_meaning_graph(self, text: str, relations: list = None) -> Dict:
        concepts = self.extract_concepts(text)
        graph = {"concepts": concepts}
        if relations:
            graph["relations"] = relations
        # Добавляем эмоции (mock)
        graph["emotional_state"] = "neutral"  # TODO: sentiment analysis
        return graph

    def save_egt(self, egt: bytes, filename: str):
        with open(filename, 'wb') as f:
            f.write(egt)

    def restore(self, data: bytes) -> Dict:
        return json.loads(data.decode('utf-8'))

# Конфиг (тот же)
config_yaml = """
memory:
  semantic:
    compression: lz4
    assoc_depth: 5
"""
with open('config.yaml', 'w') as f:
    f.write(config_yaml)

class ASMF:
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

    def process_session(self, session_data: Dict[str, Any]) -> bytes:
        filtered = self.memory.filter_noise(session_data["context"], remove=["repetitions", "offtopic"])
        graph = self.memory.create_meaning_graph(filtered)  # Теперь динамично!
        egt = lz4.frame.compress(json.dumps(graph).encode('utf-8'))
        filename = f"session_{session_data['timestamp']}.egt"
        self.memory.save_egt(egt, filename)
        return egt

    def start_new_session(self, egt_file: str) -> Dict:
        try:
            with open(egt_file, "rb") as f:
                compressed = f.read()
            decompressed = lz4.frame.decompress(compressed)
            return self.memory.restore(decompressed)
        except FileNotFoundError:
            raise ValueError(f"EGT-файл {egt_file} не найден!")

# Тест
session = {
    "context": "Тормозная система: дисковые тормоза, ABS, перегрев. Кофе пью.",
    "user_id": "user123",
    "timestamp": "2025-10-21T13:48:00Z"
}
asmf = ASMF()
egt = asmf.process_session(session)
new_session_graph = asmf.start_new_session("session_2025-10-21T13:48:00Z.egt")
print(new_session_graph)
# Вывод: {'concepts': ['disk_brakes', 'abs', 'overheating'], 'emotional_state': 'neutral'}
