from timeit import timeit as tm
import e2D

v1 = Vector2D(2, 4)
v2 = Vector2D(4, 8)

v3 = e2D.V2(2,4)
v4 = e2D.V2(4,8)
v5 = e2D.V2(8,8)

t1 = tm("avg_position(*[V2one*i for i in range(1000)])", number=1_000, globals=globals())
t2 = tm("e2D.avg_position(*[V2one*i for i in range(1000)])", number=1_000, globals=globals())
# t3 = tm("v3 * v5", number=1_000_000, globals=globals())

print(v1 + 1, v3 + 1)
print(t1, t2, 100 / t1 * t2)

v1.y = 1
print(v1)
v1.y *= 5.5
print(v1)
