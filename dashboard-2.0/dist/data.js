export const MACHINES = [
 {field:'field1',name:'Crusher',code:'CR',low:700,target:1000,unit:'TPH'},
 {field:'field2',name:'Raw Mill',code:'RM',low:300,target:350,unit:'TPH'},
 {field:'field3',name:'Kiln',code:'KL',low:280,target:335,unit:'TPH'},
 {field:'field4',name:'Finish Mill 1',code:'F1',low:100,target:120,unit:'TPH'},
 {field:'field5',name:'Finish Mill 2',code:'F2',low:100,target:120,unit:'TPH'},
 {field:'field6',name:'Coal Mill',code:'CM',low:30.3,target:32.7,unit:'TPH'},
 {field:'field7',name:'Blend Silo',code:'BS',low:5,target:95,unit:'%',silo:true}
];
export const STALE_MS=10*60*1000;
export function numeric(value){if(value==null || typeof value==='boolean' || String(value).trim()==='')return null;const n=Number(value);return Number.isFinite(n)?n:null;}
export function mergeFeed(feeds, previous={}){
 const result={...previous};
 for(const f of feeds){const time=Date.parse(f.created_at);if(!Number.isFinite(time))continue;
  for(const m of MACHINES){const value=numeric(f[m.field]);if(value===null)continue;
   if(!result[m.field] || time>=result[m.field].time)result[m.field]={value,time};
  }
 }return result;
}
export function status(m,reading,now=Date.now()){
 if(!reading)return {label:'No data',tone:'missing'};
 if(now-reading.time>STALE_MS)return {label:'Stale reading',tone:'missing'};
 if(m.silo)return reading.value>=m.low&&reading.value<m.target?{label:'Within range',tone:'good'}:{label:'Out of range',tone:'bad'};
 if(reading.value>=m.target)return {label:'On target',tone:'good'};
 if(reading.value>=m.low)return {label:'Below target',tone:'warn'};
 return {label:'Low output',tone:'bad'};
}
