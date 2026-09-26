"""Ed25519 (RFC 8032) на чистом Python — подпись и проверка без внешних библиотек.
Медленно (десятки мс), но для подписи каталога раз в релиз и проверки раз в день — более чем достаточно."""
import hashlib

p = 2 ** 255 - 19
L = 2 ** 252 + 27742317777372353535851937790883648493
d = -121665 * pow(121666, p - 2, p) % p
I = pow(2, (p - 1) // 4, p)


def _h(m):
    return hashlib.sha512(m).digest()


def _xrecover(y):
    xx = (y * y - 1) * pow(d * y * y + 1, p - 2, p)
    x = pow(xx, (p + 3) // 8, p)
    if (x * x - xx) % p != 0:
        x = x * I % p
    if x % 2 != 0:
        x = p - x
    return x


By = 4 * pow(5, p - 2, p) % p
B = (_xrecover(By), By, 1, _xrecover(By) * By % p)          # расширенные координаты


def _add(P, Q):
    x1, y1, z1, t1 = P
    x2, y2, z2, t2 = Q
    A = (y1 - x1) * (y2 - x2) % p
    Bv = (y1 + x1) * (y2 + x2) % p
    C = t1 * 2 * d * t2 % p
    D = z1 * 2 * z2 % p
    E, F, G, H = Bv - A, D - C, D + C, Bv + A
    return (E * F % p, G * H % p, F * G % p, E * H % p)


def _mul(s, P):
    Q = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            Q = _add(Q, P)
        P = _add(P, P)
        s >>= 1
    return Q


def _enc(P):
    x, y, z, _ = P
    zi = pow(z, p - 2, p)
    x, y = x * zi % p, y * zi % p
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def _dec(s):
    y = int.from_bytes(s, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _xrecover(y)
    if (x & 1) != sign:
        x = p - x
    P = (x, y, 1, x * y % p)
    x, y, z, t = P                                             # точка должна лежать на кривой
    if (-x * x + y * y - 1 - d * x * x * y * y) % p != 0:
        raise ValueError("bad point")
    return P


def _eq(P, Q):
    x1, y1, z1, _ = P
    x2, y2, z2, _ = Q
    return (x1 * z2 - x2 * z1) % p == 0 and (y1 * z2 - y2 * z1) % p == 0


def _secret(sk):
    h = _h(sk)
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, h[32:]


def public_key(sk: bytes) -> bytes:
    a, _ = _secret(sk)
    return _enc(_mul(a, B))


def sign(sk: bytes, msg: bytes) -> bytes:
    a, prefix = _secret(sk)
    A = _enc(_mul(a, B))
    r = int.from_bytes(_h(prefix + msg), "little") % L
    R = _enc(_mul(r, B))
    k = int.from_bytes(_h(R + A + msg), "little") % L
    return R + int.to_bytes((r + k * a) % L, 32, "little")


def verify(pk: bytes, msg: bytes, sig: bytes) -> bool:
    try:
        if len(sig) != 64 or len(pk) != 32:
            return False
        A = _dec(pk)
        R = _dec(sig[:32])
        s = int.from_bytes(sig[32:], "little")
        if s >= L:
            return False
        k = int.from_bytes(_h(sig[:32] + pk + msg), "little") % L
        return _eq(_mul(s, B), _add(R, _mul(k, A)))
    except Exception:
        return False
