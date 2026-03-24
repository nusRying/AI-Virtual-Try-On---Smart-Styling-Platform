import json
import os

class RecommendationEngine:
    def __init__(self, items_file="backend/data/matching_items.json", catalog_file="backend/data/garments.json"):
        self.items_file = items_file
        self.catalog_file = catalog_file

    def _load_json(self, file_path):
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r") as f:
            return json.load(f)

    def get_recommendations(self, garment_id):
        catalog = self._load_json(self.catalog_file)
        matching_pool = self._load_json(self.items_file)
        
        selected_garment = next((g for g in catalog if g["id"] == garment_id), None)
        if not selected_garment:
            return []

        selected_tags = set(selected_garment.get("tags", []))
        
        # Simple tag-based similarity scoring
        recommendations = []
        for item in matching_pool:
            item_tags = set(item.get("tags", []))
            # Calculate intersection size as a simple similarity score
            score = len(selected_tags.intersection(item_tags))
            item_copy = item.copy()
            item_copy["match_score"] = score
            recommendations.append(item_copy)

        # Sort by score descending and return top matches for each category
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        
        best_pants = next((r for r in recommendations if r["category"] == "Pants"), None)
        best_shoes = next((r for r in recommendations if r["category"] == "Shoes"), None)
        
        result = []
        if best_pants: result.append(best_pants)
        if best_shoes: result.append(best_shoes)
        
        return result
