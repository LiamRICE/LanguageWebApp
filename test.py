from src.utils.learning_utils import pick_lowest_priority_items
from src.utils.user_utils import read_user_json

data = read_user_json("liam")

x = data.get("thai_letters")

y = pick_lowest_priority_items(x, 3, is_seen=False)
print("Length:", len(y))
print("Items:", [z.get("letter_name") for z in y])