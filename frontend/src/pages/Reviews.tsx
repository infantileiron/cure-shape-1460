import {useState,useEffect} from 'react';
import type {Workspace} from '../stores/workspace';
import {create} from '../api/reviews';
import * as reports from '../api/reports';
import {download,ApiError} from '../api/client';
import {useAction} from '../hooks/useAction';
import {Heading} from '../components/common/Heading';
import {Notice} from '../components/common/Notice';
import {Empty} from '../components/common/Empty';
import {ClusterList} from '../components/ClusterList';

type Draft={run_id:string;base_version:number;names:Record<string,string>;note:string;decision:'accepted'|'needs_changes'};
type Conflict={message:string;base:number;current:number};

function defaultNames(clusters:Workspace['runs'][number]['result']['tree']['clusters']){return Object.fromEntries(clusters.map(c=>[c.cluster_id,'形态族·'+c.cluster_id]))}

export function Reviews({data,write,admin,refresh}:{data:Workspace;write:boolean;admin:boolean;refresh:()=>Promise<void>}){
 const[id,setId]=useState(''),[names,setNames]=useState<Record<string,string>>({}),[note,setNote]=useState(''),[decision,setDecision]=useState<'accepted'|'needs_changes'>('accepted'),[conflict,setConflict]=useState<Conflict|null>(null),a=useAction();
 const completed=data.runs.filter(r=>r.status==='completed'),run=completed.find(r=>r.id===id)||completed[0];
 const reviews=run?data.reviews.filter(v=>v.run_id===run.id).sort((x,y)=>y.version-x.version):[];
 const latest=reviews[0];
 // The baseline is captured when the operator opens (or explicitly reloads) this run and is
 // not advanced by background refreshes. Repeated saves from the stale page are therefore
 // rejected by the server instead of silently becoming another version.
 const[base,setBase]=useState(0);
 useEffect(()=>{if(run){setBase(data.reviews.filter(v=>v.run_id===run.id).reduce((max,v)=>Math.max(max,v.version),0));setNames(defaultNames(run.result.tree.clusters))}},[run?.id]);
 const opened=base;
 function resetDraft(){if(!run)return;setNames(defaultNames(run.result.tree.clusters));setNote('')}
 async function submit(){
  if(!run)return;
  const draft:Draft={run_id:run.id,base_version:opened,names:Object.fromEntries(run.result.tree.clusters.map(c=>[c.cluster_id,names[c.cluster_id]??('形态族·'+c.cluster_id)])),note,decision};
  const result=await a.act(async()=>create({run_id:draft.run_id,base_version:draft.base_version,names:run.result.tree.clusters.map(c=>({cluster_id:c.cluster_id,name:draft.names[c.cluster_id]})),note:draft.note,decision:draft.decision}),'新的人工命名版本已保存');
  if(result.ok){setConflict(null);setBase(result.value.version);resetDraft();await refresh();return}
  const error=result.error;
  if(error instanceof ApiError&&error.code==='review_version_conflict'){setConflict({message:error.message,base:error.base_version??opened,current:error.current_version??reviews.length});return}
  await refresh();
 }
 async function resolveConflict(){if(!conflict)return;setBase(conflict.current);setConflict(null);await refresh()}
 return <><Heading index="06 / HUMAN REVIEW" title="人工命名，留下一版解释。" detail="每次保存新增不可变复核版本；页面按打开时的版本提交，若期间已有新版本则拒绝覆盖并保留填写内容。管理员批准所选接受版本，CSV冻结其名称、版本与校验和。"/>
 <label className="selector">复核运行<select aria-label="复核运行" value={run?.id||''} onChange={e=>{setId(e.target.value);setConflict(null);resetDraft()}}>{completed.map(r=><option value={r.id} key={r.id}>{data.studies.find(s=>s.id===r.study_id)?.name} · {r.id.slice(0,12)}</option>)}</select></label>
 {!run?<Empty>先完成一份归并任务，再核对每个簇、命名并提交复核。</Empty>:<>
 <div className="review-context"><span>本页基线 <b>v{opened}</b> · 库中最新 <b>v{latest?.version??0}</b>{latest?<> · 结论 {latest.decision==='accepted'?'接受':'待补充'} · {latest.author}</>:' · 尚无复核'}</span>{latest&&latest.version>opened&&<span>库中已有更新复核 v{latest.version}；保存本页将被拒绝并提示冲突。</span>}</div>
 {conflict&&<p role="alert" className="notice error">复核版本冲突：{conflict.message}<button type="button" onClick={()=>{void resolveConflict()}}>查看最新版本并保留我的填写</button></p>}
 <ClusterList clusters={run.result.tree.clusters}/>
 {write&&<section className="form-section"><form onSubmit={e=>{e.preventDefault();void submit()}}>
  <p className="muted">保存基线：v{opened}（本页打开时最新版本，提交时服务端会再次核对）。</p>
  <div className="form-grid">{run.result.tree.clusters.map(c=><label key={c.cluster_id}>{c.cluster_id} 人工名称<input aria-label={c.cluster_id+'人工名称'} required value={names[c.cluster_id]??('形态族·'+c.cluster_id)} onChange={e=>setNames(prev=>({...prev,[c.cluster_id]:e.target.value}))}/></label>)}</div>
  <label>复核依据与边界<textarea aria-label="复核依据与边界" value={note} minLength={10} required rows={3} onChange={e=>setNote(e.target.value)}/></label>
  <label>复核结论<select aria-label="复核结论" value={decision} onChange={e=>setDecision(e.target.value as 'accepted'|'needs_changes')}><option value="accepted">接受并提请归档</option><option value="needs_changes">待补充依据</option></select></label>
  <button className="primary" disabled={a.busy}>提交人工命名版本</button>
 </form><Notice error={a.error} notice={a.notice}/></section>}
 <div className="section-rule"><h2>版本与归档</h2><span>历史命名不被覆盖，CSV保留批准时名称</span></div>
 {reviews.map(v=>{const archived=data.reports.find(r=>r.review_id===v.id);const isLatest=v.id===latest?.id;const approvalBlocked=!isLatest?`已有更新复核 v${latest?.version}，不能批准旧版本`:'该版本结论为待补充';return <article className="review-row" key={v.id}>
  <div><p className="eyebrow">VERSION {v.version} / {v.decision==='accepted'?'接受':'待补充'} / {v.author}{isLatest?' / 当前最新':''}{archived?' / 已归档':''}</p><h3>{v.names.map(n=>n.cluster_id+' '+n.name).join(' · ')}</h3><p>{v.note}</p><p className="muted">保存基线 v{v.base_version??0} · {v.created_at}</p></div>
  <div>{admin&&!archived&&<button disabled={!isLatest||v.decision!=='accepted'||a.busy} title={isLatest&&v.decision==='accepted'?undefined:approvalBlocked} aria-label={'批准版本v'+v.version+'归档'} onClick={()=>void a.act(async()=>{await reports.create({run_id:run.id,review_id:v.id,title:'滩原固化曲线·人工命名v'+v.version});await refresh()},'已批准所选接受版本并冻结归档')}>批准此接受版本归档</button>}{admin&&!archived&&<small className="muted">{(isLatest&&v.decision==='accepted')?'批准后冻结该版本名称、校验和与簇归属':approvalBlocked}</small>}
  {archived&&<><button onClick={()=>void a.act(()=>download(archived.id,'tanyuan-shape-v'+v.version),'归档CSV已下载')}>下载归档CSV · v{v.version}</button><small className="muted">归档名 {archived.title}</small></>}</div>
 </article>})}
 </>}
 <details className="audit"><summary>操作审计 · 最近写入与拒绝</summary><table><thead><tr><th>操作人</th><th>动作</th><th>HTTP</th></tr></thead><tbody>{data.audit.slice(0,20).map(a=><tr key={a.id}><td>{a.actor}</td><td>{a.action}</td><td>{a.status}</td></tr>)}</tbody></table></details></>
}
