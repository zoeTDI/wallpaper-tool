import copy
from typing import List, Dict

from config import app_config


class FilterService:
    def execute(
        self,
        data: List[Dict],
        selected_type: str,
        selected_age: str,
        type_pass_value: str = app_config.filter.type_filter.options[0].value,
        age_pass_value: str = app_config.filter.age_filter.options[0].value,
    ) -> List[Dict]:

        if selected_type == type_pass_value and selected_age == age_pass_value:
            return copy.deepcopy(data)

        results = []
        for item in data:
            item_type = str(item.get("type", "")).lower()
            item_age = str(item.get("contentrating", "")).lower()

            match_type = selected_type == type_pass_value or selected_type == item_type
            match_age = selected_age == age_pass_value or selected_age == item_age

            if match_type and match_age:
                results.append(item)
        return results
