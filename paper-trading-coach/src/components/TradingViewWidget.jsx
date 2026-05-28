import { useEffect, useRef } from 'react';
export default function TradingViewWidget({ symbol='NASDAQ:QQQ', interval='1' }) { const ref=useRef(null);
  useEffect(()=>{ if(!ref.current) return; ref.current.innerHTML=''; const c=document.createElement('div'); c.className='tradingview-widget-container__widget'; ref.current.appendChild(c); const s=document.createElement('script'); s.src='https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js'; s.async=true; s.innerHTML=JSON.stringify({autosize:true,symbol,interval,theme:'dark',timezone:'America/New_York',hide_top_toolbar:false,hide_legend:false,save_image:false,allow_symbol_change:true}); ref.current.appendChild(s); return ()=>{ if(ref.current) ref.current.innerHTML=''; }; },[symbol,interval]);
  return <div className='card h-80'><div className='h-full tradingview-widget-container' ref={ref} /></div>;
}
