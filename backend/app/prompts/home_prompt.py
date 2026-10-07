def build_home_prompt(data: dict) -> str:
    rooms_desc = ", ".join(f"{r.get('quantity', 1)}x {r.get('name', 'Room')}" for r in data.get('rooms', [])) if data.get('rooms') else data.get('room_type', 'Living Room')
    reqs_desc = ", ".join(f"{req.get('category')} ({req.get('priority', 'medium')} priority)" for req in data.get('requirements', [])) if data.get('requirements') else "Standard furnishing"

    return f"""You are an elite interior designer, product specialist, and financial strategist for PocketSmart AI.
Generate a comprehensive, real-time interior design and budget plan.

User Input Parameters:
- Planned Rooms: {rooms_desc}
- Requirements & Priorities: {reqs_desc}
- Design Style: {data.get('style', 'Modern')}
- Total Budget: {data.get('currency', 'INR')} {data.get('total_budget', data.get('totalBudget', 0))}
- Currency: {data.get('currency', 'INR')}
- Flexibility: {data.get('flexibility', data.get('budget_flexibility', 'flexible'))}
- Color Preferences: {data.get('color_preference', data.get('colorPreference', 'Warm contemporary neutrals'))}
- Quality Preference: {data.get('quality_preference', data.get('qualityPreference', 'Premium'))}
- Other Requirements: {data.get('other_requirements', data.get('otherRequirements', 'None'))}

Generate 4 to 8 realistic, budget-conscious product recommendations matching the rooms and categories (such as Lighting, Furniture, Decor, Ceiling Fans, Storage, etc.).
Calculate item prices such that the total sum fits realistically within the total budget.
For each item, include top Indian/global shopping platforms (Amazon, Flipkart, Ikea, Myntra, Ajio, Pepperfry).

Return ONLY valid raw JSON with this exact structure:
{{
  "ai_summary": "Detailed strategic overview of the plan and budget distribution.",
  "allocations": [
    {{"category": "Lighting", "percentage": 25.0, "allocated_amount": 1500.0}},
    {{"category": "Furniture", "percentage": 50.0, "allocated_amount": 3000.0}},
    {{"category": "Decor", "percentage": 25.0, "allocated_amount": 1500.0}}
  ],
  "recommendations": [
    {{
      "name": "LED Bulb (Warm White)",
      "category": "Lighting",
      "price": 100.0,
      "quantity": 5,
      "description": "Energy-efficient LED bulbs for general ambient lighting.",
      "style": "Modern",
      "match_score": 96.0,
      "budget_impact": "low",
      "shopping_links": [
        {{"name": "Amazon", "url": "https://www.amazon.in"}},
        {{"name": "Flipkart", "url": "https://www.flipkart.com"}},
        {{"name": "Ikea", "url": "https://www.ikea.com/in/en"}},
        {{"name": "Myntra", "url": "https://www.myntra.com"}},
        {{"name": "Ajio", "url": "https://www.ajio.com"}}
      ]
    }}
  ],
  "additional_suggestions": [
    "Consider purchasing used or factory-refurbished furniture for further cost savings.",
    "Look for seasonal sales and festive discounts on online marketplaces.",
    "Prioritize essential items and postpone non-essential accent purchases."
  ]
}}
"""
