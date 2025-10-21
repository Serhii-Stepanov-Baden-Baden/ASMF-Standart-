import json
import yaml
from typing import Dict, Any, List

# Enhanced SemanticMemory (from prev)
class SemanticMemory:
    def __init__(self):
        self.storage = {}

    def extract_concepts(self, text: str) -> List[str]:
        # Improved mock: keyword-based
        keywords = ["перегрев", "проблема", "безопасность"]
        return [kw for kw in keywords if kw in text.lower()]

    def store(self, key: str, data: Dict):
        if key not in self.storage:
            self.storage[key] = {}
        self.storage[key][data.get("emotion_id", "default")] = data

    def retrieve(self, key: str, id_: str) -> Dict[str, Any]:
        if key in self.storage and id_ in self.storage[key]:
            return self.storage[key][id_]
        if key == "context":
            return {"context": "Решили проблему с перегревом тормозов?"}  # Str in dict
        return {"primary": "neutral"}  # Default

# Mock ESEP with better tone detection
class ESEP:
    def __init__(self, sensitivity: float):
        self.sensitivity = sensitivity

    def detect_tone(self, text: str) -> str:
        # Simple keyword mock (expand to torch.nn for real)
        if any(word in text.lower() for word in ["проблема", "перегрев"]):
            return "worry"
        return "neutral"

    def encode(self, primary: str, secondary: List[str], intensity: float) -> Dict:
        # Return vector as list
        vector = [intensity if i == 0 else 0.3 for i in range(3)]  # Mock dim=3
        return {"vector": vector, "primary": primary, "secondary": secondary}

# Config
config_yaml = """
esep:
  weight: 0.5
"""
with open('config.yaml', 'w') as f:
    f.write(config_yaml)

class ESEPProcessor:
    def __init__(self, config_path: str = "config.yaml"):
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            raise ValueError("config.yaml не найден!")
        self.memory = SemanticMemory()
        self.esep = ESEP(sensitivity=self.config["esep"]["weight"])

    def encode_emotion(self, input_text: str, context_id: str) -> Dict[str, Any]:
        tone = self.esep.detect_tone(input_text)
        concepts = self.memory.extract_concepts(input_text)
        emotion_vector = self.esep.encode(
            primary=tone,
            secondary=["calm", "focus"],
            intensity=0.78
        )
        emotion_data = {
            "emotion_id": f"ESEP_2025_{context_id}",
            "primary": tone,
            "secondary": ["calm", "focus"],
            "intensity": 0.78,
            "vector": emotion_vector["vector"],  # Save vector
            "context_link": f"asmf/context/session_{context_id}",
            "timestamp": "2025-10-21T14:01:00Z",
            "concepts": concepts  # Link semantics
        }
        self.memory.store("emotional_state", emotion_data)
        # Mock store context
        self.memory.store("context", {"context": "Решили проблему с перегревом тормозов?", "id": f"session_{context_id}"})
        return emotion_data

    def generate_response(self, context_id: str) -> str:
        try:
            emotion = self.memory.retrieve("emotional_state", f"ESEP_2025_{context_id}")
            context_data = self.memory.retrieve("context", f"session_{context_id}")
            context = context_data.get("context", "No context")
            if emotion.get("primary") == "neutral":
                raise ValueError("Эмоция не найдена — default neutral")
            return f"Ответ с тоном {emotion['primary']}: {context}"
        except ValueError as e:
            return f"Default ответ: {e}"

# Тест
session = {
    "input_text": "Перегрев тормозов — это проблема!",
    "context_id": "325"
}
esep_proc = ESEPProcessor()
emotion = esep_proc.encode_emotion(session["input_text"], session["context_id"])
print(emotion)
response = esep_proc.generate_response("325")
print(response)
# Вывод: {'emotion_id': 'ESEP_2025_325', ..., 'concepts': ['перегрев', 'проблема']}
# "Ответ с тоном worry: Решили проблему с перегревом тормозов?"
