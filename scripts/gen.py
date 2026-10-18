import hashlib, sys
from datetime import datetime, timezone
def unix(w): return int(datetime.fromisoformat(w).replace(tzinfo=timezone.utc).timestamp())
def candidates(t, nmax, per=20, shift=40):
    x=(t<<16)|0x330E; out=[]
    for n in range(1,nmax+1):
        s=b""
        for _ in range(per):
            x=(0x5DEECE66D*x+0xB)%2**48; s+=bytes([x>>shift])
        out.append(s)
    return out
def W_of(seed, p):
    t=p.bit_length(); s=(t-1)//160; h=t-160*s-1
    z=int.from_bytes(seed,'big')
    W=int.from_bytes(hashlib.sha1(seed).digest(),'big') & ((1<<h)-1)
    for i in range(1,s+1):
        W=(W<<160)|int.from_bytes(hashlib.sha1(((z+i)%2**160).to_bytes(20,'big')).digest(),'big')
    return W
def legendre(a,p): return pow(a,(p-1)//2,p)
def sqrtmod(a,p):
    if p%4==3: return pow(a,(p+1)//4,p)
    q,s=p-1,0
    while q%2==0: q//=2; s+=1
    z=2
    while legendre(z,p)!=p-1: z+=1
    m,c,t,r=s,pow(z,q,p),pow(a,q,p),pow(a,(q+1)//2,p)
    while t!=1:
        i,tt=0,t
        while tt!=1: tt=tt*tt%p; i+=1
        b=pow(c,1<<(m-i-1),p); m,c,t,r=i,b*b%p,t*b*b%p,r*b%p
    return r
P192=2**192-2**64-1; P239=2**239-2**143-2**95+2**47-1
RUNS={
 "ANSI192":("1997-05-18 14:45:34",6013, P192, {139:0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1, 6013:0xcc22d6dfb95c6b25e49c0d6364a4e5980c393aa21668d953, 5228:0x22123dc2395a05caa7423daeccc94760a7d462256bd56916}),
 "ANSI239":("1997-05-15 15:49:03",3048, P239, {2185:0x6b016c3bdcf18941d0d654921475ca71a9db2fb27d1d37796185c2942c0a, 2320:0x617fab6832576cbbfed50d99f0249c3fee58b94ba0038c7ae84c8c832f2c, 3048:0x255705fa2a306654b1f4cb03d6a750a30c250102d4988717d9ba15ab6d3e}),
 "P-256":("1997-08-16 01:52:34",1842, 2**256-2**224+2**192+2**96-1, 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b),
 "P-224":("1998-04-03 12:52:07",7026, 2**224-2**96+1, 0xb4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4),
}
name=sys.argv[1]; when,nmax,p,bpub=RUNS[name]
cands=candidates(unix(when),nmax)
with open(f"{name}.cands","w") as f:
    nvalid=0
    for i,seed in enumerate(cands,1):
        c=W_of(seed,p)%p
        if c==0: continue
        r=(-27*pow(c,-1,p))%p
        if legendre(r,p)!=1: continue
        b=sqrtmod(r,p); assert b*b*c%p==(-27)%p
        nvalid+=1
        f.write(f"{i} {seed.hex()} {b} {p-b}\n")
        pubs = bpub if isinstance(bpub, dict) else {nmax: bpub}
        if i in pubs: print(f"candidate {i}: published b matches root1: {b==pubs[i]}  root2: {p-b==pubs[i]}")
print(name,"candidates",nmax,"with valid b:",nvalid)
