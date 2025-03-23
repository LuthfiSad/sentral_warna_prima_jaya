from typing import Dict

def get_pagination_meta(page: int, per_page: int, total_data: int) -> Dict[str, int]:
    return {
        "page": page,
        "perPage": per_page,
        "totalData": total_data,
        "totalPages": (total_data + per_page - 1) // per_page,  # Math.ceil
    }
