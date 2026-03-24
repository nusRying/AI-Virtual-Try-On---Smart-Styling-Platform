import random

class StylingReasoner:
    def __init__(self):
        self.templates = [
            "This combination works because the {item1_tag} aesthetic of the {item1_name} perfectly complements the {item2_tag} vibe of the {item2_name}.",
            "Pairing these creates a balanced {style} look that is both modern and comfortable.",
            "The color palette here is exceptionally cohesive, bringing out the best in both your {item1_name} and these {item2_name}.",
            "We recommend this match for a {occasion} setting where style and ease are equally important."
        ]

    def generate_styling_tip(self, selected_item, matched_items):
        if not matched_items:
            return "Try selecting a different garment to see styling tips!"

        item1_name = selected_item.get("name", "selected piece")
        item1_tag = selected_item.get("tags", ["stylish"])[0]
        
        # Pick the first matched item for the detailed tip
        target = matched_items[0]
        item2_name = target.get("name", "matching item")
        item2_tag = target.get("tags", ["versatile"])[0]
        
        style = random.choice(["contemporary", "rugged", "refined", "casual-chic"])
        occasion = random.choice(["weekend outing", "business casual", "evening dinner", "relaxed workday"])

        template = random.choice(self.templates)
        
        tip = template.format(
            item1_name=item1_name,
            item1_tag=item1_tag,
            item2_name=item2_name,
            item2_tag=item2_tag,
            style=style,
            occasion=occasion
        )

        return tip
