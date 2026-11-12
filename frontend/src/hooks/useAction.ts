import {useState} from 'react';
export type ActionResult<T>= {ok:true;value:T}|{ok:false;error:unknown};
export function useAction(){const [busy,setBusy]=useState(false);const [error,setError]=useState('');const [notice,setNotice]=useState('');async function act<T=unknown>(fn:()=>Promise<T>,message='已保存'):Promise<ActionResult<T>>{setBusy(true);setError('');setNotice('');try{const value=await fn();setNotice(message);return {ok:true,value}}catch(e){setError((e as Error).message);return {ok:false,error:e}}finally{setBusy(false)}}return {busy,error,notice,act,setError}}
