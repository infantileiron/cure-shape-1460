"""Complete-link dissimilarity clustering. Stable lexicographic member-ID ties."""
import math

def complete_link(ids,matrix,threshold):
 if len(ids)<2 or len(set(ids))!=len(ids):raise ValueError("unique curve IDs required")
 n=len(ids)
 if len(matrix)!=n or any(len(row)!=n for row in matrix):raise ValueError("square matrix required")
 if not math.isfinite(threshold) or threshold<0:raise ValueError("invalid cut threshold")
 for i in range(n):
  for j in range(n):
   v=matrix[i][j]
   if not math.isfinite(v) or v<0 or abs(v-matrix[j][i])>1e-10 or (i==j and v!=0):raise ValueError("invalid dissimilarity matrix")
 index={s:i for i,s in enumerate(ids)};active={s:(s,) for s in sorted(ids)};merges=[];used=set(ids);serial=0
 while len(active)>1:
  names=sorted(active,key=lambda s:active[s]);choices=[]
  for k,a in enumerate(names):
   for b in names[k+1:]:
    pairs=[(matrix[index[x]][index[y]],x,y) for x in active[a] for y in active[b]]
    d=max(p[0] for p in pairs);witness=min((x,y) for v,x,y in pairs if v==d)
    choices.append((d,active[a],active[b],a,b,witness))
  d,_,_,a,b,witness=min(choices);members=tuple(sorted(active[a]+active[b]))
  serial+=1;node='@'+str(serial)
  while node in used:serial+=1;node='@'+str(serial)
  used.add(node)
  merges.append({"node_id":node,"left":a,"right":b,"distance":d,"members":list(members),"max_witness":list(witness)})
  del active[a];del active[b];active[node]=members
 cut={s:(s,) for s in sorted(ids)}
 for m in merges:
  if m["distance"]>threshold:break
  del cut[m["left"]];del cut[m["right"]];cut[m["node_id"]]=tuple(m["members"])
 clusters=[]
 for number,members in enumerate(sorted(cut.values()),1):
  diameter=max(matrix[index[x]][index[y]] for x in members for y in members)
  clusters.append({"cluster_id":f"G{number:02}","members":list(members),"diameter":diameter})
 return {"merges":merges,"clusters":clusters,"threshold":threshold,"linkage":"complete","tie_rule":"lexicographic sorted member IDs"}
