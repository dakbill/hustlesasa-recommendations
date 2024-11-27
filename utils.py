def summarize(product_ids):
    if len(product_ids) < 3:
        return ' and '.join([f"[id:{product_id}]" for product_id in product_ids])
    else:
        return f"""
            {', '.join([f"[id:{product_id}]" for product_id in product_ids[:-2]])} and [id:{product_ids[-1]}]
        """.strip()
        