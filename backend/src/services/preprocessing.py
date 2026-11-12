import math,statistics,re

def validate_dataset(times,curves):
 if len(times)!=64:raise ValueError("每份曲线必须恰好64个完整等距时间点")
 if not all(isinstance(t,(int,float)) and not isinstance(t,bool) and math.isfinite(t) for t in times):raise ValueError("时间必须有限")
 delta=times[1]-times[0]
 if delta<=0 or any(times[i]<=times[i-1] or not math.isclose(times[i]-times[i-1],delta,rel_tol=1e-8,abs_tol=1e-9) for i in range(1,64)):raise ValueError("时间必须严格递增、等距，无重复或缺点；不自动重采样")
 if not 2<=len(curves)<=64:raise ValueError("曲线数须为2至64")
 ids=[]
 for c in curves:
  key=c['curve_id'];values=c['values']
  if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,20}',key):raise ValueError("曲线ID须为唯一英数短ID")
  if key in ids:raise ValueError("曲线ID重复")
  ids.append(key)
  if len(values)!=64 or not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in values):raise ValueError("每条曲线须64个有限值；不补点、不填0")
 return {"point_count":64,"curve_count":len(curves),"step_minutes":delta,"span_minutes":times[-1]-times[0]}

def normalize(curves,mode):
 if mode not in ('raw','zscore'):raise ValueError("未知归一化口径")
 output=[]
 for c in sorted(curves,key=lambda c:c['curve_id']):
  values=c['values'];mean=statistics.fmean(values);sd=statistics.pstdev(values)
  if mode=='zscore' and sd<=1e-12*max(1,max(abs(v) for v in values)):raise ValueError('zscore常量/近常量曲线不可估计：'+c['curve_id']+'；请使用原始口径或移除后重新导入')
  vals=values if mode=='raw' else [(v-mean)/sd for v in values]
  output.append({**c,'values':vals,'raw_values':values,'mean':mean,'population_sd':sd})
 return output
