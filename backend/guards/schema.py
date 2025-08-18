from typing import Any, Dict

# Minimal guardrails-like validation. We provide a simple schema check.

RAIL_XML = """
<rail version="0.1">
  <output>
    <object name="report">
      <string name="summary" description="Short non-empty summary" />
      <list name="citations">
        <object name="citation">
          <string name="title" />
          <string name="url" />
        </object>
      </list>
    </object>
  </output>
</rail>
"""


def validate_report_json(obj: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(obj, dict):
        raise ValueError("Report must be an object")
    summary = obj.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("summary must be a non-empty string")
    citations = obj.get("citations")
    if not isinstance(citations, list):
        raise ValueError("citations must be a list")
    for c in citations:
        if not isinstance(c, dict):
            raise ValueError("each citation must be an object")
        if not isinstance(c.get("title"), str):
            raise ValueError("citation.title must be string")
        if not isinstance(c.get("url"), str):
            raise ValueError("citation.url must be string")
    return obj
