from math import gcd


def invertModulo (a, n):
    res, no_res = certificates (a, n, 1)
    return res

def certificates (a, b, c):
    if c % gcd(a,b)!=0:
        return "no answer can be found",0
    if b == 0:
        return a//c, 0
    p, q = certificates (b, a%b, c)
    x = q
    y = p - (a//b)*q
    return x,y
print(invertModulo(5,3))