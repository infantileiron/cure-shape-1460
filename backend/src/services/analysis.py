import hashlib,json
from src.services.preprocessing import validate_dataset,normalize
from src.services.dtw import dtw
from src.services.clustering import complete_link

def analyze(snapshot):
 dataset=snapshot['dataset'];policy=snapshot['policy'];meta=validate_dataset(dataset['times'],dataset['curves']);curves=normalize(dataset['curves'],policy['normalization']);ids=[c['curve_id'] for c in curves];n=len(ids);matrix=[[0.0]*n for _ in ids];pairs=[]
 for i in range(n):
  for j in range(i+1,n):
   aligned=dtw(curves[i]['values'],curves[j]['values'],policy['window']);matrix[i][j]=matrix[j][i]=aligned['distance'];pairs.append({'curve_a':ids[i],'curve_b':ids[j],**aligned})
 tree=complete_link(ids,matrix,policy['threshold'])
 return {'ids':ids,'matrix':matrix,'pairs':pairs,'tree':tree,'curves':curves,'times':dataset['times'],'meta':meta,'policy':policy,'checksum':hashlib.sha256(json.dumps(snapshot,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'assumptions':['局部平方差最小累计代价；显示sqrt(累计代价/该最优路径长度)，不是最小平均代价，也不保证三角不等式。','同分路径依次按最短长度、对角/上/左；配对按曲线ID排序。归并同分按成员ID字典序。','窗口为Sakoe–Chiba |i-j|<=w，单位为采样索引。固定等距完整数据，不重采样、不插值。','complete-link簇间最大距离；阈值含等号，结果簇内直径不超过阈值。','raw保留曲线量级；每曲线zscore采用总体标准差，常量或近常量明确失败，不代填0。','固化读数为模拟反应指数，无真实材料强度或质量合格结论；人工命名是版本化解释。']}
