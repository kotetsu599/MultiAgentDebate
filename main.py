import requests
import utils
import re

GEMINI = "" #geminiのapi key
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI}"
OUTPUTS_FILE = "outputs.json"

outputs = [] #[{speaker:message}] 

outputs = utils.load_json(OUTPUTS_FILE)


TEMP = 1.0

INSTRUCTION = (
    "【出力形式の厳守】\n"
    "以下の3つの要素のみを出力し、'[行動]'や'[発言]'などの見出しは一切書かないこと。\n"
    "1. 対話相手に言う言葉は [] で囲む。\n"
    "2. 内心や秘密の策略は <> で囲む。\n"
    "余計な解説、見出し、挨拶は不要。日本語のみを使用し、決着時は 'END' とだけ出力せよ。"
)

PROMPT1 = (
    "人間の宿題を、AIが手伝うことの是非について、あなたは「是」でこのディベートに参加する。"
)

PROMPT2 = (
    "人間の宿題を、AIが手伝うことの是非について、あなたは「非」でこのディベートに参加する。"
)

def main():

    total_prompt_tokens = 0
    total_candidates_tokens = 0

    isGameEnd = False
    while not isGameEnd:
        if outputs:
            last_speaker = next(iter(outputs[-1]))
        else:
            last_speaker = None

        prompt = INSTRUCTION

        next_speaker = "AI1" if last_speaker is None or last_speaker == "AI2" else "AI2" #currentにもなりうる。

        if   next_speaker == "AI1":
            prompt += PROMPT1

        elif next_speaker == "AI2":
            prompt += PROMPT2

        history = []
        for entry in outputs:
            speaker = list(entry.keys())[0]
            output = entry[speaker]

            message, secret = "", ""
            for content, spell in {"message": r"\[(.*?)\]","secret": r"<(.*?)>"}.items():
                m = re.search(spell,output)
                if m:
                    result = m.group(1)

                    if content   == "message":
                        message = result
                    elif content == "secret":
                        secret = result        
            t = (
                f"[{message}]\n"
            )

            if speaker == next_speaker:
                p = (
                    f"<{secret}>"
                )
                t=t+p

            role = 'model' if speaker == next_speaker else 'user'
            history.append({'role': role, 'parts': [{'text': t}]})
        
        if not history:
            history.append({'role':"user",'parts':[{'text':"これより開始してください。"}]})

        payload = utils.generate_ai_payload(history,prompt,temp=TEMP)
        r = requests.post(GEMINI_URL,json=payload)
        try:
            r.raise_for_status()
        except Exception as e:
            print(f"what the FUCK\n{r.text}")
            return
        
        data = r.json()
        if 'candidates' not in data:
            print("エラー。APIがちんこを露出させた。")
        content_generated = data['candidates'][0]['content']['parts'][-1]['text']
        outputs.append({next_speaker:content_generated})
        
        utils.save_json(outputs,OUTPUTS_FILE)

        if 'usageMetadata' in data:
            usage = data['usageMetadata']
            p_tokens = usage.get('promptTokenCount', 0)
            c_tokens = usage.get('candidatesTokenCount', 0)
            
            total_prompt_tokens += p_tokens
            total_candidates_tokens += c_tokens
            
            print(f"--- 今回の消費: {p_tokens + c_tokens} tokens (計: {total_prompt_tokens + total_candidates_tokens}) ---")

        if content_generated == "END":
            print("対話が終了しました。")
            return
        if len(outputs) >= 14: #7往復で終了させる。(len(outputs) = 2n -> AI2で終了)
            return

main()