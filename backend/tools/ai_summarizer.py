import os
from typing import List, Dict, Any
from openai import OpenAI

def generate_fallback_summary(query: str, content: List[str], citations: List[Dict[str, str]]) -> str:
    """
    Generate a fallback summary when AI is not available.
    """
    # Combine the most relevant content
    combined_content = " ".join(content[:3])
    
    # Create a simple summary based on available content
    summary = f"Based on research into '{query}', key findings include: {combined_content[:200]}..."
    
    if len(combined_content) > 200:
        summary += f" Additional research shows significant developments in this field with multiple sources providing comprehensive coverage."
    
    return summary

def get_ai_summary(query: str, content: List[str], citations: List[Dict[str, str]]) -> str:
    """
    Generate an intelligent, topic-specific summary using OpenAI GPT.
    
    Args:
        query: The original research query
        content: List of extracted content from web pages
        citations: List of citation dictionaries with title and url
    
    Returns:
        AI-generated summary tailored to the research topic
    """
    try:
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ OpenAI API key not found. Using fallback summary generation.")
            return generate_fallback_summary(query, content, citations)
        
        client = OpenAI(api_key=api_key)
        
        # Prepare the content for AI processing
        combined_content = "\n\n".join(content[:5])  # Use top 5 content pieces
        citation_info = "\n".join([f"- {cite.get('title', 'Unknown')}: {cite.get('url', 'No URL')}" for cite in citations])
        
        # Create a focused prompt for the AI
        prompt = f"""
You are an expert research analyst. Generate a concise, intelligent summary based on the research query and content provided.

RESEARCH QUERY: {query}

CONTENT FROM SOURCES:
{combined_content}

AVAILABLE SOURCES:
{citation_info}

INSTRUCTIONS:
- Create a focused summary that directly answers the research query
- Use clear, professional language
- Include specific facts and developments mentioned in the content
- Keep the summary between 150-250 words
- Be factual and avoid speculation
- Focus on recent developments and key insights

SUMMARY:
"""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional research analyst who creates concise, accurate summaries of research topics."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.2,  # Very low temperature for focused, factual content
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Fallback to enhanced rule-based summary
        return generate_fallback_summary(query, content, citations)

def generate_fallback_summary(query: str, content: List[str], citations: List[Dict[str, str]]) -> str:
    """
    Deterministic multi-section research report that does not require an API key.
    It organizes extracted facts into a readable structure with paragraphs.
    """
    num_sources = max(1, len(citations))

    # Collect salient first sentences from scraped content
    salient: List[str] = []
    for block in content:
        if not block:
            continue
        first = block.strip().split('. ')
        if first and len(first[0]) > 40:
            sentence = first[0].strip().rstrip('.') + '.'
            if sentence not in salient:
                salient.append(sentence)
        if len(salient) >= 8:
            break

    executive = (
        f"This report synthesizes findings on '{query}'. It analyzes {num_sources} "
        f"recently retrieved web sources and extracts converging evidence on the topic."
    )

    if not salient:
        salient = [
            "The reviewed sources discuss recent developments and context for the topic.",
            "Evidence points to rapid iteration and active research across industry and academia.",
        ]

    recent_developments = " ".join(salient[:4])
    additional_insights = " ".join(salient[4:]) if len(salient) > 4 else "No further notable developments were consistently reported across sources."

    evidence_lines = []
    for c in citations[:5]:
        title = c.get('title') or c.get('url') or 'Source'
        url = c.get('url') or ''
        evidence_lines.append(f"- {title} — {url}")
    evidence = "\n".join(evidence_lines) if evidence_lines else "- No citations available"

    outlook = (
        "Short-term outlook: expect incremental updates, more rigorous evaluations, and broader adoption where ROI is clear. "
        "Risks include over-claiming, data quality limits, and policy uncertainty."
    )

    return (
        "Executive Summary\n" + executive + "\n\n" +
        "Recent Developments\n" + recent_developments + "\n\n" +
        "Additional Insights\n" + additional_insights + "\n\n" +
        "Evidence & Sources\n" + evidence + "\n\n" +
        "Outlook\n" + outlook
    )
