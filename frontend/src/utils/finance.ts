import type {Transaction} from '../types';
export const inr=(n:number)=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(n||0);
export function summarize(rows:Transaction[]){const income=rows.filter(x=>x.transaction_type==='income').reduce((s,x)=>s+x.amount,0),gross=rows.filter(x=>x.transaction_type==='expense').reduce((s,x)=>s+x.amount,0),refunds=rows.filter(x=>x.transaction_type==='refund').reduce((s,x)=>s+x.amount,0),net=gross-refunds,flow=income-net;return {income,gross,refunds,net,flow,savings:income>0?flow/income*100:null};}
export const monthStart=(d=new Date())=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-01`;
