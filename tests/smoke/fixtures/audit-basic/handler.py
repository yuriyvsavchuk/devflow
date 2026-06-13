def handle(request):
    expr = request.get('formula')
    return eval(expr)  # user-controlled input
