"""
Interpolation
"""

import math


def monospline(xs, ys):
    """
    Monotone cubic interpolation
    """
    # Deal with length issues
    length = len(xs)
    if length != len(ys):
        raise ValueError('Need an equal count of xs and ys')
    if length == 0:
        return lambda x: 0
    if length == 1:
        return lambda x: ys[0]

    # Rearrange xs and ys so that xs is sorted
    old_xs, old_ys = xs, ys
    xs = sorted(old_xs)
    ys = [y for _, y in sorted(zip(old_xs, old_ys))]

    # Get consecutive differences and slopes
    dys = []
    dxs = []
    ms = []
    for i in range(length-1):
        dx = xs[i+1] - xs[i]
        dy = ys[i+1] - ys[i]
        dxs.append(dx)
        dys.append(dy)
        ms.append(dy/dx)

    # Get degree-1 coefficients
    cls = [ms[0]]
    for i in range(len(dxs)-1):
        m = ms[i]
        m_next = ms[i+1]
        if m * m_next <= 0:
            cls.append(0)
        else:
            dx_ = dxs[i]
            dx_next = dxs[i+1]
            common = dx_ + dx_next
            cls.append(
                3 * common / ((common + dx_next)/m + (common + dx_) / m_next)
            )
    cls.append(ms[-1])

    # Get degree-2 and degree-3 coefficients
    c2s = []
    c3s = []
    for i in range(len(cls)-1):
        c1 = cls[i]
        m_ = ms[i]
        inv_dx = 1/dxs[i]
        common_ = c1 + cls[i+1] - 2*m_
        c2s.append((m_ - c1 - common_) * inv_dx)
        c3s.append(common_ * inv_dx**2)

    # Return interpolant function
    def interpolant(x):
        # The rightmost point in the dataset should give an exact result
        if x == xs[-1]:
            return ys[-1]

        # Search for the interval x is in, returning the corresponding y if x
        # is one of the original xs
        low = 0
        high = len(c3s) - 1
        while low <= high:
            mid = math.floor(0.5 * (low + high))
            x_here = xs[mid]

            if x_here < x:
                low = mid + 1
            elif x_here > x:
                high = mid - 1
            else:
                return ys[mid]
        i = max(0, high)

        # Interpolate
        diff = x - xs[i]
        return ys[i] + cls[i]*diff + c2s[i]*diff**2 + c3s[i]*diff**3

    return interpolant
