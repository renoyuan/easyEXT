class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # 重载加法运算符 (+)
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        raise TypeError("操作数类型必须是 Vector")
    
    # 重载减法运算符 (-)
    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        raise TypeError("操作数类型必须是 Vector")
    
    # 重载标量乘法运算符 (*)
    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        raise TypeError("标量必须是整数或浮点数")
    
    # 重载相等运算符 (==)
    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return False
    
    # 重载字符串表示 (print 时输出可读内容)
    def __str__(self):
        return f"Vector({self.x}, {self.y})"

# 示例使用
if __name__ == "__main__":
    v1 = Vector(2, 3)
    v2 = Vector(4, 5)
    
    # 加法
    v3 = v1 + v2
    print(f"加法结果: {v3}")  # 输出: Vector(6, 8) [2,7](@ref)
    
    # 减法
    v4 = v2 - v1
    print(f"减法结果: {v4}")  # 输出: Vector(2, 2) [2](@ref)
    
    # 标量乘法
    v5 = v1 * 3
    print(f"标量乘法: {v5}")  # 输出: Vector(6, 9) [2](@ref)
    
    # 相等比较
    v6 = Vector(2, 3)
    print(f"v1 等于 v6: {v1 == v6}")  # 输出: True [7](@ref)
    print(f"v1 等于 v2: {v1 == v2}")  # 输出: False