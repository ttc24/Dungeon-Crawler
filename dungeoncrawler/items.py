class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Weapon(Item):
    def __init__(self, name, description, min_damage, max_damage, price=50):
        super().__init__(name, description)
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.price = price
        self.effect = None
