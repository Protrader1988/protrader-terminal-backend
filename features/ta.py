def sma(values, n):
    out=[]; s=0.0
    for i,v in enumerate(values):
        s+=v
        if i>=n: s-=values[i-n]
        out.append(s/n if i>=n-1 else None)
    return out
