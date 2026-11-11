"""結果の後の確かめ: synth.Sampler と tau-extend の hmm2.sample の記号の 2 連の頻度を比べる。
使い方: python3 -I checks/sampler_vs_hmm2.py <scripts のパス>（合成だけ）"""
import sys, numpy as np
sys.path.insert(0, sys.argv[1])
import synth as SY
from pinned import H
m=SY.make_m0(3,2026111001)
D=SY.draw_D(m,np.random.default_rng(7)); mw=SY.writer_model(m,D,0.3)
N=H.NSYM; L=60000; n=4
def big(seqs):
    c=np.zeros((N,N))
    for s in seqs: np.add.at(c,(s[:-1],s[1:]),1)
    return c/c.sum()
a=big([SY.Sampler(mw).seq(np.random.default_rng([1,i]).random((L,2))) for i in range(n)])
b=big(H.sample(mw,[L]*n,np.random.default_rng(2)))
c=big(H.sample(mw,[L]*n,np.random.default_rng(3)))
tv=lambda x,y: 0.5*np.abs(x-y).sum()
print("TV Sampler vs hmm2.sample %.4f ; hmm2 vs hmm2 (control) %.4f"%(tv(a,b),tv(b,c)))
# negative control: perturbed model should differ
mb=SY.writer_model(m,D,0.0)
d=big(H.sample(mb,[L]*n,np.random.default_rng(4)))
print("TV vs other model (should be larger) %.4f"%tv(b,d))
