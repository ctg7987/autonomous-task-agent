from typing import List


def extract_facts(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return ["No content available."]
    # Very tiny heuristic: split into sentences and take 2-3 concise bits
    seps = [". ", "! ", "? "]
    for sep in seps:
        parts = text.split(sep)
        if len(parts) > 1:
            break
    else:
        parts = [text]

    facts = []
    for p in parts:
        p = p.strip()
        if p:
            facts.append(p[:180])
        if len(facts) >= 3:
            break
    return facts
