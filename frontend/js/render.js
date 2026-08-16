import {sensorChart, degradationChart} from './charts.js';

const money = value => `$${Math.round(Number(value || 0)).toLocaleString()}`;
const pct = value => `${Math.round(Number(value || 0) * 100)}%`;
const safe = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

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
  const width=900,height=420;
  const positions=[[130,115],[330,115],[530,115],[730,115],[130,295],[330,295],[530,295],[730,295]];
  const visible=assets.slice(0,8);
  const connectors=`<path class="flow-line" d="M205 115 H255 M405 115 H455 M605 115 H655 M205 295 H255 M405 295 H455 M605 295 H655 M730 155 V255 M130 155 V255"/>`;
  const machines=visible.map((asset,index)=>{
    const [x,y]=positions[index];
    return `<g class="machine-group" data-asset-id="${asset.asset_id}" transform="translate(${x},${y})">
      <circle class="machine-ring ${asset.risk_band}" cx="0" cy="0" r="57"/>
      <rect class="machine-shell" x="-47" y="-34" width="94" height="68" rx="13"/>
      <rect class="machine-head" x="-25" y="-49" width="50" height="17" rx="5"/>
      <circle cx="-20" cy="0" r="13" fill="#e8eef1" stroke="#8ea5b0"/>
      <line x1="-20" y1="-11" x2="-20" y2="11" stroke="#78909a" stroke-width="3"/>
      <rect x="3" y="-13" width="30" height="26" rx="5" fill="#eef3f5" stroke="#9bb0ba"/>
      <text class="machine-label" x="0" y="78">${asset.asset_id}</text>
      <text class="machine-meta" x="0" y="91">${Math.round(asset.rul.p50)} cycles</text>
    </g>`;
  }).join('');
  return `<svg class="plant-svg" viewBox="0 0 ${width} ${height}">
    <rect class="plant-floor" x="35" y="35" width="830" height="350" rx="18"/>
    ${connectors}${machines}
    <text x="55" y="60" fill="#80939b" font-size="9" font-weight="700" letter-spacing=".12em">PROCESS LINE A</text>
    <text x="55" y="240" fill="#80939b" font-size="9" font-weight="700" letter-spacing=".12em">PROCESS LINE B</text>
  </svg>`;
}

export function healthRanking(assets) {
  return [...assets].sort((a,b)=>a.rul.p50-b.rul.p50).slice(0,8).map(asset=>`
    <div class="health-row" data-asset-id="${asset.asset_id}">
      <div class="health-name"><strong>${asset.asset_id}</strong><span>${safe(asset.cell)}</span></div>
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
    <td><strong>${asset.asset_id}</strong><div class="small-label">${safe(asset.asset_name)}</div></td>
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
    return `<div class="gantt-row"><div class="gantt-asset">${asset.asset_id}</div>${cells}</div>`;
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
