import json

def load_json(path:str) -> list:
    
    with open(path,"r",encoding="utf-8")as f:
        return json.load(f)
            

def save_json(data: list, path: str) -> None:
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("utils鰓")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
def generate_ai_payload(history, prompt, temp=1,thinking=True):

    return {
    "contents": history,
    "generationConfig": {
      "maxOutputTokens": 3000,
      #"thinkingConfig": {"thinkingBudget": 1024 if thinking else 0},　モデルによってはthinking使うのアリ。
      "temperature": temp,
    },
    "systemInstruction": {"parts": [{"text": prompt}]},

}
