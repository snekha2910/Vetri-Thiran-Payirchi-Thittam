def build_jewelry_prompt(data: dict) -> str:
    occasion = data.get('occasion', 'Party')
    jewelry_type = data.get('jewelry_type', data.get('jewelryType', 'Set'))
    style = data.get('style', 'Contemporary')
    budget = data.get('total_budget', data.get('totalBudget', 5000))
    currency = data.get('currency', 'INR')

    return f"""You are an expert luxury jewelry stylist, gemologist, and fashion coordinator for PocketSmart AI.
Generate a comprehensive, real-time personalized jewelry recommendations and styling plan.

User Input Parameters:
- Occasion: {occasion}
- Jewelry Type Focus: {jewelry_type}
- Style Aesthetic: {style}
- Metal Preference: {data.get('metal_preference', data.get('metalPreference', 'Gold'))}
- Color Preference: {data.get('color_preference', data.get('colorPreference', 'Classic metallic'))}
- Total Budget: {currency} {budget}
- Currency: {currency}
- Additional Notes: {data.get('additional_requirements', data.get('additionalRequirements', 'None'))}

Generate tailored jewelry piece recommendations (such as bracelet, ring, watch, necklace, earrings, or bangles).
Include top jewelry platforms (Amazon, Flipkart, Bluestone, Tanishq, CaratLane, Malabar, Mia).

Return ONLY valid raw JSON with this exact structure:
{{
  "ai_summary": "Detailed personalized jewelry styling advice and aesthetic harmony rationale.",
  "outfit_analysis": {{
    "colors": ["blue", "white"],
    "style": "{style.lower()}",
    "formality": "{"informal" if occasion.lower() in ("casual", "party") else "formal"}"
  }},
  "allocations": [
    {{"category": "Statement Piece", "percentage": 50.0, "allocated_amount": 2500.0}},
    {{"category": "Accents & Rings", "percentage": 30.0, "allocated_amount": 1500.0}},
    {{"category": "Wristwear", "percentage": 20.0, "allocated_amount": 1000.0}}
  ],
  "recommendations": [
    {{
      "name": "bracelet",
      "category": "Wristwear",
      "style": "casual",
      "price": 500.0,
      "quantity": 1,
      "description": "A simple, braided leather bracelet with metal accents. Complements the casual style of the outfit without being overly flashy.",
      "match_score": 95.0,
      "budget_impact": "low",
      "shopping_links": [
        {{"name": "Amazon", "url": "https://www.amazon.in"}},
        {{"name": "Flipkart", "url": "https://www.flipkart.com"}},
        {{"name": "Bluestone", "url": "https://www.bluestone.com"}},
        {{"name": "Tanishq", "url": "https://www.tanishq.co.in"}},
        {{"name": "CaratLane", "url": "https://www.caratlane.com"}},
        {{"name": "Malabar", "url": "https://www.malabargoldanddiamonds.com"}},
        {{"name": "Mia", "url": "https://www.miabytanishq.com"}}
      ]
    }}
  ],
  "styling_tips": [
    "Keep the jewelry minimal to match the casual style of the outfit.",
    "Consider the watch as a statement piece, choosing a design that reflects personal style.",
    "Ensure the metal tones of the ring and bracelet complement each other."
  ]
}}
"""
