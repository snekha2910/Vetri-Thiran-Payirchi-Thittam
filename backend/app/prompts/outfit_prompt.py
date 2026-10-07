def build_outfit_vision_prompt(data: dict) -> str:
    return f"""Analyze this outfit image and suggest complementary jewelry pieces within a budget of {data.get('currency', 'INR')} {data.get('total_budget')}.
Occasion: {data.get('occasion')}
Metal Preference: {data.get('metal_preference')}

Analyze:
1. Neckline cut and silhouette.
2. Color palette and contrast accents.
3. Embroidery and metalwork undertones.

Return ONLY a valid JSON object matching the standard styling schema.
"""
