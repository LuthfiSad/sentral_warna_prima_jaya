from typing import Dict

def get_pagination_meta(page: int, perPage: int, total_data: int) -> Dict[str, int]:
    return {
        "page": page,
        "perPage": perPage,
        "totalData": total_data,
        "totalPages": (total_data + perPage - 1) // perPage,  # Math.ceil
    }
