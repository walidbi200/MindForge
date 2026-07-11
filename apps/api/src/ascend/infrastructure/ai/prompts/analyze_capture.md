Analyze the following capture and provide structured suggestions for the user's Knowledge Graph.

### Capture Content:
```text
{capture_content}
```

### Source Context (Optional):
```text
{source_context}
```

### Instructions:
1. **Summary**: Provide a concise 1-2 sentence summary of the core insight or information in the capture.
2. **Concepts**: Identify 1-5 distinct, foundational concepts mentioned or implied. A concept should be a reusable idea, framework, or entity (e.g., "Spaced Repetition", "Modular Monolith", "PostgreSQL"). Provide a short description and a confidence score (0.0 to 1.0).
3. **Relationships**: If any of the extracted concepts relate to each other, define the relationship edge. Use simple relationship types like "RELATED_TO", "PART_OF", "CAUSES", "DEPENDS_ON", "EXEMPLIFIES". Provide a confidence score.
4. **Questions**: Suggest 1-3 thought-provoking questions that the user could ask themselves during a future review of this material to test their recall or deepen their understanding.
5. **Collections**: Suggest 1-3 tags or overarching categories this capture belongs to (e.g., "System Design", "Psychology").
6. **Review Suggestion**: Suggest a logical review schedule or priority (e.g., "1_DAY", "1_WEEK", "1_MONTH", "NEVER") based on the material's complexity and importance.

### Output Format:
You MUST output ONLY a valid JSON object matching this schema exactly:

```json
{
  "summary": "...",
  "concepts": [
    {
      "name": "...",
      "description": "...",
      "confidence": 0.95
    }
  ],
  "relationships": [
    {
      "from": "Concept Name A",
      "to": "Concept Name B",
      "type": "RELATED_TO",
      "confidence": 0.88
    }
  ],
  "questions": [
    "..."
  ],
  "collections": [
    "..."
  ],
  "review_suggestion": "1_WEEK"
}
```
