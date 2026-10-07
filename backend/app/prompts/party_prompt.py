def build_party_prompt(data: dict) -> str:
    party_type = data.get('event_type', data.get('eventType', data.get('party_type', 'Birthday Party')))
    guests = data.get('guest_count', data.get('guestCount', 10))
    budget = data.get('total_budget', data.get('totalBudget', 5000))
    currency = data.get('currency', 'INR')

    return f"""You are an elite event planner, party strategist, and financial coordinator for PocketSmart AI.
Generate a comprehensive, real-time party and event budget plan.

User Input Parameters:
- Event Type: {party_type}
- Guest Count: {guests}
- Venue Type: {data.get('venue_type', data.get('venueType', 'Indoor'))}
- Total Budget: {currency} {budget}
- Currency: {currency}
- Food / Catering Preference: {data.get('food_preference', data.get('foodPreference', 'Standard'))}
- Decoration Preference: {data.get('decoration_preference', data.get('decorationPreference', 'Celebration theme'))}
- Entertainment Preference: {data.get('entertainment_preference', data.get('entertainmentPreference', 'Music and Games'))}
- Location / City: {data.get('location', 'Local city')}
- Additional Requirements: {data.get('additional_requirements', data.get('additionalRequirements', 'None'))}

Generate 4 to 8 realistic itemized expenses grouped under categories like Venue, Catering, Entertainment, Contingency, Favors.
Include suitable platforms (Swiggy, Zomato, Bookmyshow, Amazon, Flipkart, Google, Booking, Makemytrip, Oyo, Nobroker).

Return ONLY valid raw JSON with this exact structure:
{{
  "ai_summary": "Detailed event coordination strategy and budget distribution.",
  "allocations": [
    {{"category": "Venue", "percentage": 10.0, "allocated_amount": 500.0}},
    {{"category": "Catering", "percentage": 40.0, "allocated_amount": 2000.0}},
    {{"category": "Entertainment", "percentage": 30.0, "allocated_amount": 1500.0}},
    {{"category": "Contingency", "percentage": 20.0, "allocated_amount": 1000.0}}
  ],
  "recommendations": [
    {{
      "name": "Home-cooked / Catered Meal",
      "category": "Catering",
      "price": 2000.0,
      "quantity": 1,
      "description": "Appetizers and dinner spread curated for {guests} guests.",
      "match_score": 95.0,
      "budget_impact": "medium",
      "shopping_links": [
        {{"name": "Swiggy", "url": "https://www.swiggy.com"}},
        {{"name": "Zomato", "url": "https://www.zomato.com"}}
      ]
    }},
    {{
      "name": "Streaming service / Sound rental",
      "category": "Entertainment",
      "price": 500.0,
      "quantity": 1,
      "description": "Party playlist and audio streaming setup.",
      "match_score": 90.0,
      "budget_impact": "low",
      "shopping_links": [
        {{"name": "Amazon", "url": "https://www.amazon.in"}},
        {{"name": "Flipkart", "url": "https://www.flipkart.com"}},
        {{"name": "Bookmyshow", "url": "https://in.bookmyshow.com"}}
      ]
    }}
  ],
  "venue_suggestions": [
    {{
      "name": "Home / Banquet Space",
      "type": "Residential / Indoor Venue",
      "location": "{data.get('location', 'Local residential area')}",
      "cost": 0.0,
      "website": "https://www.google.com",
      "map_url": "https://maps.google.com"
    }}
  ],
  "additional_suggestions": [
    "Consider making the meal a potluck style if comfortable with guests to reduce catering costs.",
    "Look for discounts or offers on streaming services or party games.",
    "Homemade decorations can be a cost effective alternative if you decide to add some."
  ]
}}
"""
