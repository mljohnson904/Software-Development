export const etNow = () => new Date(new Date().toLocaleString('en-US',{timeZone:'America/New_York'}));
export const etStatus = () => { const d=etNow(); const mins=d.getHours()*60+d.getMinutes(); if(mins<550) return 'Before Market Prep'; if(mins<570) return 'Watch Only'; if(mins<660) return 'Practice Window'; if(mins<960) return 'Stop & Journal'; return 'Market Closed / Review'; };
