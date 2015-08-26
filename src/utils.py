def circle_iterator(center_x, center_y, radius):
    for y in range(-radius, radius):
        for x in range(-radius, radius):
            if (x * x) + (y * y) <= radius * radius:
                yield center_x + x, center_y + y
