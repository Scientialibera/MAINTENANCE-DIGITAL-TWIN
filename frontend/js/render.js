import {sensorChart, degradationChart} from './charts.js';

const money = value => `$${Math.round(Number(value || 0)).toLocaleString()}`;
const pct = value => `${Math.round(Number(value || 0) * 100)}%`;
const safe = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const equipmentCatalog = [
  {tag:'PMP-101',type:'Centrifugal pump'},
  {tag:'CMP-102',type:'Air compressor'},
  {tag:'HEX-103',type:'Heat exchanger'},
  {tag:'VLV-104',type:'Control valve'},
  {tag:'HOP-201',type:'Feed hopper'},
  {tag:'CRH-202',type:'Rotary crusher'},
  {tag:'CNV-203',type:'Belt conveyor'},
  {tag:'PRS-204',type:'Hydraulic press'},
  {tag:'MTR-301',type:'Auxiliary motor'},
  {tag:'FAN-302',type:'Exhaust fan'}
];
const assetIndex = assetOrId => Math.max(0,Number(String(typeof assetOrId==='string' ? assetOrId : assetOrId?.asset_id || '').match(/\d+/)?.[0] || 1)-1);
export function assetDisplay(assetOrId) {
  const id=typeof assetOrId==='string' ? assetOrId : assetOrId?.asset_id;
  const unit=assetIndex(id);
  return equipmentCatalog[unit] || {tag:id || 'ASSET',type:'Rotating equipment'};
}

const equipmentIcon=index=>[
  `<g class="equipment-icon pump"><circle cx="0" cy="0" r="28"/><path d="M-28 0 H-43 M28 0 H43 M-9-13 L15 0 L-9 13 Z"/></g>`,
  `<g class="equipment-icon compressor"><path d="M-38-24 L31-16 V16 L-38 24 Z"/><path d="M-21-19 V19 M-5-17 V17 M12-15 V15"/><line x1="31" y1="0" x2="43" y2="0"/></g>`,
  `<g class="equipment-icon exchanger"><circle cx="0" cy="0" r="31"/><path d="M-20-22 L20 22 M20-22 L-20 22"/><line x1="-43" y1="0" x2="-31" y2="0"/><line x1="31" y1="0" x2="43" y2="0"/></g>`,
  `<g class="equipment-icon valve"><path d="M-35-22 L0 0 L-35 22 Z M35-22 L0 0 L35 22 Z"/><line x1="0" y1="0" x2="0" y2="-31"/><rect x="-13" y="-41" width="26" height="10" rx="3"/></g>`,
  `<g class="equipment-icon hopper"><path d="M-35-30 H35 L20 8 H-20 Z"/><rect x="-10" y="8" width="20" height="24"/><line x1="-24" y1="8" x2="-32" y2="33"/><line x1="24" y1="8" x2="32" y2="33"/></g>`,
  `<g class="equipment-icon crusher"><rect x="-38" y="-30" width="76" height="60" rx="8"/><circle cx="-14" cy="0" r="16"/><circle cx="17" cy="0" r="13"/><circle cx="-14" cy="0" r="4"/><circle cx="17" cy="0" r="3"/></g>`,
  `<g class="equipment-icon conveyor"><path d="M-42-15 H42 V15 H-42 Z"/><circle cx="-27" cy="0" r="9"/><circle cx="0" cy="0" r="9"/><circle cx="27" cy="0" r="9"/><path d="M-31 15 L-38 31 M31 15 L38 31"/></g>`,
  `<g class="equipment-icon press"><path d="M-36-32 H36 V-21 H13 V5 H-13 V-21 H-36 Z M-32 23 H32 V33 H-32 Z"/><rect x="-9" y="5" width="18" height="18"/></g>`,
  `<g class="equipment-icon motor"><rect x="-35" y="-25" width="63" height="50" rx="18"/><path d="M28-9 H40 V9 H28 M-21 25 V34 M14 25 V34"/><text x="-4" y="7">M</text></g>`,
  `<g class="equipment-icon fan"><circle cx="0" cy="0" r="32"/><circle cx="0" cy="0" r="5"/><path d="M0-5 Q-3-30 17-25 Q25-18 5 0 M5 0 Q30-3 25 17 Q18 25 0 5 M0 5 Q3 30-17 25 Q-25 18-5 0 M-5 0 Q-30 3-25-17 Q-18-25 0-5"/></g>`
][index] || `<g class="equipment-icon"><circle cx="0" cy="0" r="31"/><path d="M-20 0 H20 M0-20 V20"/></g>`;

export function equipmentTwin(asset,projection=null) {
  const index=assetIndex(asset);
  const display=assetDisplay(asset);
  const riskBand=projection?.risk_band || asset.risk_band;
  const telemetry=projection?.telemetry || asset.telemetry || {};
  const labels=[
    {key:'S2',label:'Input response',value:Number(telemetry.sensor_2).toFixed(3),unit:'benchmark units',tx:300,ty:65,anchor:'end',lx:312,ly:72,x:350,y:125},
    {key:'S4',label:'Thermal load',value:Number(telemetry.sensor_4).toFixed(3),unit:'benchmark units',tx:450,ty:36,anchor:'middle',lx:450,ly:52,x:450,y:105},
    {key:'S15',label:'Degradation',value:Number(telemetry.sensor_15).toFixed(3),unit:'benchmark units',tx:600,ty:65,anchor:'start',lx:588,ly:72,x:550,y:125},
    {key:'VIB',label:'Vibration index',value:telemetry.vibration_index == null ? '1.00' : Number(telemetry.vibration_index).toFixed(2),unit:'scenario index',tx:610,ty:264,anchor:'start',lx:598,ly:253,x:548,y:225}
  ];
  const callouts=labels.map(item=>`<g class="sensor-callout" data-sensor-key="${item.key}" data-sensor-label="${item.label}" data-sensor-value="${item.value}" data-sensor-unit="${item.unit}" data-asset-id="${asset.asset_id}"><line x1="${item.x}" y1="${item.y}" x2="${item.lx}" y2="${item.ly}"/><circle class="sensor-hit" cx="${item.x}" cy="${item.y}" r="15"/><circle class="sensor-point" cx="${item.x}" cy="${item.y}" r="7"/><text x="${item.tx}" y="${item.ty}" text-anchor="${item.anchor}">${item.key} · ${item.label}</text></g>`).join('');
  return `<svg class="engine-svg equipment-twin-svg" viewBox="0 0 900 410" role="img" aria-label="${display.tag} ${display.type} digital twin">
    <defs><filter id="assetShadow"><feDropShadow dx="0" dy="12" stdDeviation="14" flood-color="#23495c" flood-opacity=".12"/></filter></defs>
    <path class="twin-flow" d="M180 175 H720"/>
    <g class="twin-asset" data-asset-id="${asset.asset_id}" transform="translate(450 175) scale(1.9)" filter="url(#assetShadow)">
      <circle class="twin-status-ring ${riskBand}" cx="0" cy="0" r="57"/>
      ${equipmentIcon(index)}
      <circle class="twin-hit" cx="0" cy="0" r="50"/>
    </g>
    ${callouts}
    <text class="twin-tag" x="450" y="329">${display.tag}</text>
    <text class="twin-type" x="450" y="360">${display.type}</text>
    <text class="twin-source" x="450" y="389">LIVE BENCHMARK PROXY · ${safe(asset.cell)}</text>
  </svg>`;
}

export function overviewKpis(kpis) {
  const items=[
    ['Asset availability',`${kpis.asset_availability_pct.toFixed(1)}%`,'non-critical benchmark assets'],
    ['OEE proxy',`${kpis.oee_proxy_pct.toFixed(1)}%`,'demonstration operating indicator'],
    ['Critical assets',kpis.critical_assets,'requires immediate review'],
    ['Predicted failures',kpis.predicted_failures,'high or critical risk'],
    ['Maintenance backlog',kpis.maintenance_backlog,'attention queue']
  ];
  return items.map(([label,value,detail])=>`<div class="kpi-card"><div class="label">${label}</div><div class="value">${value}</div><div class="detail">${detail}</div></div>`).join('');
}

export function plantTopology(assets) {
  const width=900,height=530;
  const positions=[[130,135],[330,135],[530,135],[730,135],[130,380],[330,380],[530,380],[730,380]];
  const visible=assets.slice(0,8);
  const connectors=`<path class="flow-line" d="M190 135 H270 M390 135 H470 M590 135 H670 M190 380 H270 M390 380 H470 M590 380 H670"/>`;
  const machines=visible.map((asset,index)=>{
    const [x,y]=positions[index];
    const display=assetDisplay(asset);
    return `<g class="machine-group" data-asset-id="${asset.asset_id}" transform="translate(${x},${y})">
      <circle class="machine-ring ${asset.risk_band}" cx="0" cy="0" r="57"/>
      ${equipmentIcon(index)}
      <circle class="machine-hit" cx="0" cy="0" r="50"/>
      <text class="machine-label" x="0" y="80">${display.tag}</text>
      <text class="machine-type" x="0" y="95">${display.type}</text>
      <text class="machine-meta" x="0" y="110">${Math.round(asset.rul.p50)} cycles RUL</text>
    </g>`;
  }).join('');
  return `<svg class="plant-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet">
    <rect class="plant-floor" x="35" y="15" width="830" height="500" rx="18"/>
    ${connectors}${machines}
    <g class="line-heading line-a"><rect x="55" y="35" width="145" height="28" rx="14"/><circle cx="71" cy="49" r="4"/><text x="83" y="52.5">LINE A · PROCESS GAS</text></g>
    <g class="line-heading line-b"><rect x="55" y="280" width="164" height="28" rx="14"/><circle cx="71" cy="294" r="4"/><text x="83" y="297.5">LINE B · MATERIAL FLOW</text></g>
  </svg>`;
}

export function healthRanking(assets) {
  return [...assets].sort((a,b)=>a.rul.p50-b.rul.p50).slice(0,8).map(asset=>`
    <div class="health-row" data-asset-id="${asset.asset_id}">
      <div class="health-name"><strong>${assetDisplay(asset).tag}</strong><span>${safe(assetDisplay(asset).type)}</span></div>
      <div class="health-bar"><div class="health-fill ${asset.risk_band}" style="width:${asset.health_score}%"></div></div>
      <div class="health-rul">${Math.round(asset.rul.p50)}</div>
    </div>`).join('');
}

export function renderTelemetry(history) { return sensorChart(history); }
export function renderDegradation(history,rul) { return degradationChart(history,rul); }

export function telemetryCards(asset, telemetryOverride=null) {
  const telemetry=telemetryOverride || asset.telemetry;
  const entries=[['S2',telemetry.sensor_2],['S3',telemetry.sensor_3],['S4',telemetry.sensor_4],['S15',telemetry.sensor_15],['S20',telemetry.sensor_20],['S21',telemetry.sensor_21]];
  if (telemetry.vibration_index != null) entries[5]=['Vibration idx',telemetry.vibration_index];
  return entries.map(([label,value])=>`<div class="telemetry-card"><span>${label}</span><strong>${Number(value).toFixed(3)}</strong></div>`).join('');
}

export function updateRul(asset, projection=null) {
  const rul=projection?.rul || asset.rul;
  document.getElementById('rulP10').textContent=Number(rul.p10).toFixed(0);
  document.getElementById('rulP50').textContent=Number(rul.p50).toFixed(0);
  document.getElementById('rulP90').textContent=Number(rul.p90).toFixed(0);
  const max=125;
  const left=Math.min(100,Math.max(0,Number(rul.p10)/max*100));
  const right=Math.min(100,Math.max(left,Number(rul.p90)/max*100));
  const median=Math.min(100,Math.max(0,Number(rul.p50)/max*100));
  const window=document.getElementById('rulWindow');
  window.style.left=`${left}%`; window.style.width=`${Math.max(1,right-left)}%`;
  document.getElementById('rulMarker').style.left=`${median}%`;
  const baselineRisk=Number(asset.failure_probability);
  const risk=projection ? Number(projection.failure_probability) : baselineRisk;
  const acceleration=projection?.wear_acceleration || 1;
  document.getElementById('scenarioComparison').innerHTML=`
    <div class="compare-card"><span>Health</span><strong>${projection?.health_score ?? asset.health_score}/100</strong></div>
    <div class="compare-card"><span>Risk indicator</span><strong>${pct(risk)}</strong></div>
    <div class="compare-card"><span>Wear acceleration</span><strong>${Number(acceleration).toFixed(2)}x</strong></div>`;
}

export function riskSummary(assets) {
  const critical=assets.filter(a=>a.risk_band==='critical').length;
  const high=assets.filter(a=>a.risk_band==='high').length;
  const watch=assets.filter(a=>a.risk_band==='watch').length;
  const avg=assets.reduce((sum,a)=>sum+a.health_score,0)/Math.max(1,assets.length);
  return [['Critical',critical],['High risk',high],['Watch',watch],['Average health',`${avg.toFixed(1)}/100`]].map(([label,value])=>`<div class="summary-tile"><span>${label}</span><strong>${value}</strong></div>`).join('');
}

export function riskRows(assets) {
  return [...assets].sort((a,b)=>b.failure_probability-a.failure_probability).map(asset=>`
  <tr data-asset-id="${asset.asset_id}">
    <td><strong>${assetDisplay(asset).tag}</strong><div class="small-label">${safe(assetDisplay(asset).type)}</div></td>
    <td>${safe(asset.cell)}</td>
    <td><div class="table-health"><span>${asset.health_score}</span><div class="mini-bar"><i style="width:${asset.health_score}%"></i></div></div></td>
    <td>${Math.round(asset.rul.p50)} cycles</td><td>${Math.round(asset.rul.p10)} - ${Math.round(asset.rul.p90)}</td><td>${pct(asset.failure_probability)}</td>
    <td><span class="state-pill">${asset.risk_band.toUpperCase()}</span></td>
  </tr>`).join('');
}

export function plannerKpis(result) {
  const s=result.summary;
  return [['Scheduled',Math.round(s.scheduled_assets)],['Failure cost avoided',money(s.failure_cost_avoided)],['Maintenance cost',money(s.maintenance_cost)],['Net expected value',money(s.net_expected_value)]].map(([label,value])=>`<div class="planner-kpi"><span>${label}</span><strong>${value}</strong></div>`).join('');
}

export function gantt(result, assets) {
  const schedule=new Map(result.schedule.map(item=>[item.asset_id,item]));
  const slots=result.slots;
  const header=`<div class="gantt-header"><div></div>${slots.map((slot,index)=>`<div>${index%2===0?'D'+(Math.floor(index/2)+1):'PM'}</div>`).join('')}</div>`;
  const rows=assets.map(asset=>{
    const job=schedule.get(asset.asset_id);
    const cells=slots.map((_,slot)=>{
      const active=job && slot>=job.start_slot && slot<job.start_slot+job.duration_slots;
      return `<div class="gantt-cell ${active?'active':''} ${active && ['critical','high'].includes(asset.risk_band)?'high':''}" title="${active?'Planned maintenance':'Available'}"></div>`;
    }).join('');
    return `<div class="gantt-row"><div class="gantt-asset">${assetDisplay(asset).tag}</div>${cells}</div>`;
  }).join('');
  return `<div class="gantt">${header}${rows}</div>`;
}

export function valueComparison(result) {
  const s=result.summary;
  const after=Math.max(0,s.baseline_expected_failure_cost-s.failure_cost_avoided);
  return `<div class="value-column"><h3>Before optimization</h3>
    <div class="value-line"><span>Expected failure exposure</span><strong>${money(s.baseline_expected_failure_cost)}</strong></div>
    <div class="value-line"><span>Planned maintenance</span><strong>$0</strong></div><div class="value-line"><span>Production loss</span><strong>$0</strong></div></div>
  <div class="value-column"><h3>Optimized plan</h3>
    <div class="value-line"><span>Residual failure exposure</span><strong>${money(after)}</strong></div>
    <div class="value-line"><span>Planned maintenance</span><strong>${money(s.maintenance_cost)}</strong></div>
    <div class="value-line"><span>Production loss</span><strong>${money(s.production_loss)}</strong></div>
    <div class="value-line"><span>Net expected value</span><strong>${money(s.net_expected_value)}</strong></div></div>`;
}

export function modelValidation(payload) {
  const protocol=payload.benchmark_protocol;
  document.getElementById('benchmarkProtocol').innerHTML=Object.entries(protocol).map(([key,value])=>`<div class="protocol-item"><span>${key.replaceAll('_',' ').toUpperCase()}</span><strong>${Array.isArray(value)?value.join(', '):safe(value)}</strong></div>`).join('');
  const modelState=document.getElementById('modelState');
  if (payload.trained_model_available) {
    modelState.innerHTML='<strong>Trained artifact loaded</strong><span>Validation metrics are measured from the whole-engine holdout.</span>';
    const metrics=payload.evaluation || {};
    document.getElementById('validationMetrics').innerHTML=`<div class="metric-grid">
      <div class="metric-box"><span>RMSE</span><strong>${Number(metrics.rmse).toFixed(2)}</strong></div>
      <div class="metric-box"><span>MAE</span><strong>${Number(metrics.mae).toFixed(2)}</strong></div>
      <div class="metric-box"><span>NASA SCORE</span><strong>${Number(metrics.nasa_score).toFixed(0)}</strong></div>
      <div class="metric-box"><span>80% INTERVAL COVERAGE</span><strong>${(Number(metrics.interval_80_coverage)*100).toFixed(1)}%</strong></div></div>`;
  } else {
    modelState.innerHTML='<strong>Training required</strong><span>No fabricated validation metric is displayed.</span>';
    document.getElementById('validationMetrics').innerHTML=`<p>${safe(payload.note)}</p><code>python scripts/fetch_nasa_data.py --cmapss<br>python scripts/train_rul_model.py</code>`;
  }
}
