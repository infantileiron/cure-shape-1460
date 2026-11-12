"""Minimum cumulative squared cost; tie: shortest path then diagonal/up/left."""
import math

def dtw(x,y,window):
 if not x or not y or len(x)!=len(y):raise ValueError("DTW requires equal nonempty lengths")
 if isinstance(window,bool) or not isinstance(window,int) or not 0<=window<len(x):raise ValueError("invalid Sakoe-Chiba window")
 if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in [*x,*y]):raise ValueError("nonfinite samples")
 n=len(x);cost=[[math.inf]*(n+1) for _ in range(n+1)];length=[[0]*(n+1) for _ in range(n+1)];back={};cost[0][0]=0
 for i in range(1,n+1):
  for j in range(max(1,i-window),min(n,i+window)+1):
   choices=[(cost[a][b],length[a][b],priority,a,b) for priority,(a,b) in enumerate(((i-1,j-1),(i-1,j),(i,j-1))) if math.isfinite(cost[a][b])]
   if not choices:continue
   c,l,_,a,b=min(choices);v=c+(x[i-1]-y[j-1])**2
   if not math.isfinite(v):raise ValueError("DTW squared cost overflow")
   cost[i][j]=v;length[i][j]=l+1;back[i,j]=(a,b)
 if not math.isfinite(cost[n][n]):raise ValueError("no feasible alignment path")
 path=[];i=j=n
 while i and j:path.append([i-1,j-1]);i,j=back[i,j]
 path.reverse();return {"cost":cost[n][n],"path_length":length[n][n],"distance":math.sqrt(cost[n][n]/length[n][n]),"path":path}
