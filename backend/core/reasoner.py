import os
import google.generativeai as genai
from typing import List, Dict

class StylingReasoner:
    """
    Intelligent styling reasoner that explains WHY a combination works.
    Now powered by Gemini Pro for sophisticated fashion advice.
    """
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.use_llm = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.use_llm = True
                print("Gemini Pro Reasoner initialized.")
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")

    def generate_styling_tip(self, selected_item: Dict, matched_items: List[Dict]) -> str:
        if not matched_items:
            return "Upload a photo and select a garment to see our styling insights!"

        if self.use_llm:
            try:
                return self._generate_llm_tip(selected_item, matched_items)
            except Exception as e:
                print(f"LLM Reasoning failed: {e}. Falling back to rule-based.")
        
        return self._generate_rule_based_tip(selected_item, matched_items)

    def _generate_llm_tip(self, selected_item: Dict, matched_items: List[Dict]) -> str:
        # Construct a descriptive prompt for Gemini
        target_names = [item['name'] for item in matched_items]
        
        prompt = f"""
        You are a professional AI Fashion Stylist. 
        A user has selected a {selected_item['name']} (Category: {selected_item['category']}, Tags: {', '.join(selected_item['tags'])}).
        
        You have recommended the following items to complete the look:
        {', '.join(target_names)}
        
        Write a concise, encouraging styling tip (max 3 sentences) explaining why this outfit works together. 
        Focus on style consistency, color harmony, and the 'vibe' of the collection.
        Do not use markdown formatting.
        """
        
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def _generate_rule_based_tip(self, selected_item: Dict, matched_items: List[Dict]) -> str:
        # Legacy rule-based logic as reliable fallback
        shirt_name = selected_item.get("name", "selected piece")
        target = matched_items[0]
        target_name = target.get("name", "matching item")
        
        tip = (
            f"This combination creates a cohesive and intentional silhouette. "
            f"The {target_name} were selected to complement your {shirt_name} by maintaining "
            f"consistent color tones and a balanced profile suitable for various settings."
        )
        return tip
