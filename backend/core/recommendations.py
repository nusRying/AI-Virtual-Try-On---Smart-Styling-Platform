import json
import os
from backend.core.vector_db import vector_db

class RecommendationEngine:
    """
    Advanced recommendation engine that considers color harmony and style consistency.
    Now enhanced with semantic vector search.
    """
    STYLE_RULES = {
        "formal": ["formal", "classic", "minimal"],
        "casual": ["casual", "denim", "rugged", "utility"],
        "minimalist": ["minimal", "white", "black", "grey", "monochrome"],
        "rugged": ["rugged", "olive", "utility", "denim"]
    }

    # Simplified color harmony (complementary and classic pairs)
    COLOR_HARMONY = {
        "white": ["blue", "black", "navy", "grey", "denim", "khaki", "dark"],
        "blue": ["white", "khaki", "grey", "black"],
        "black": ["white", "grey", "blue", "red", "yellow"],
        "navy": ["white", "khaki", "grey", "burgundy"],
        "olive": ["black", "white", "khaki", "brown"],
        "burgundy": ["navy", "black", "grey", "white"],
        "khaki": ["navy", "white", "olive", "black", "blue"],
        "grey": ["white", "black", "navy", "blue", "burgundy"]
    }

    def __init__(self, items_file="backend/data/matching_items.json", catalog_file="backend/data/garments.json"):
        self.items_file = items_file
        self.catalog_file = catalog_file

    def _load_json(self, file_path):
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r") as f:
            return json.load(f)

    def get_recommendations(self, garment_id):
        # 1. Try semantic search first if vector DB is connected
        if vector_db.is_connected:
            try:
                catalog = self._load_json(self.catalog_file)
                selected_garment = next((g for g in catalog if g["id"] == garment_id), None)
                if selected_garment:
                    tags_str = ' '.join(selected_garment.get('tags', []))
                    query_text = f"{selected_garment['name']} {selected_garment.get('description', '')} {tags_str}"
                    similar_ids = vector_db.search_similar(query_text=query_text, limit=10)
                    
                    matching_pool = self._load_json(self.items_file)
                    recommendations = [item for item in matching_pool if item["id"] in similar_ids]
                    if recommendations:
                        return recommendations
            except Exception as e:
                print(f"Semantic search failed, falling back to rule-based: {e}")

        # 2. Rule-based fallback
        catalog = self._load_json(self.catalog_file)
        matching_pool = self._load_json(self.items_file)
        
        selected_garment = next((g for g in catalog if g["id"] == garment_id), None)
        if not selected_garment:
            return []

        selected_tags = [t.lower() for t in selected_garment.get("tags", [])]
        selected_colors = [c for c in self.COLOR_HARMONY if c in selected_tags]
        
        # Determine base style of selected garment
        base_style = "casual" # Default
        for style, style_tags in self.STYLE_RULES.items():
            if any(t in selected_tags for t in style_tags):
                base_style = style
                break

        scored_recommendations = []
        for item in matching_pool:
            item_tags = [t.lower() for t in item.get("tags", [])]
            score = 0
            
            # 1. Style Consistency Score (+5 points)
            target_style_tags = self.STYLE_RULES.get(base_style, [])
            if any(t in item_tags for t in target_style_tags):
                score += 5
            
            # 2. Color Harmony Score (+10 points)
            for color in selected_colors:
                harmonious_colors = self.COLOR_HARMONY.get(color, [])
                if any(c in item_tags for c in harmonious_colors):
                    score += 10
                    break
            
            # 3. Simple Tag Overlap (+1 point each)
            tag_overlap = len(set(selected_tags).intersection(set(item_tags)))
            score += tag_overlap

            item_copy = item.copy()
            item_copy["match_score"] = score
            item_copy["reasoning_style"] = base_style
            scored_recommendations.append(item_copy)

        # Sort by score descending
        scored_recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Select best for each category
        categories = set(r["category"] for r in scored_recommendations)
        result = []
        for cat in categories:
            best_match = next((r for r in scored_recommendations if r["category"] == cat), None)
            if best_match:
                result.append(best_match)
        
        return result
