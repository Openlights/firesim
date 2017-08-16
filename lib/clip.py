def clip(low, input, high):
    return min(max(input, low), high)
