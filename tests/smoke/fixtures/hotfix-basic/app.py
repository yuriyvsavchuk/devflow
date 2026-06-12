def orders_endpoint(user):
    # FEATURE_X: new discount lookup (deployed today)
    discount = {}['missing-key']  # crashes for every user
    return {'orders': [], 'discount': discount}
