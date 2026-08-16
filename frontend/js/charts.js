function scale(values, minOut, maxOut) {
  const finite = values.filter(Number.isFinite);
  const min = Math.min(...finite);
  const max = Math.max(...finite);
  const span = Math.max(1e-9, max - min);
  return values.map(value => minOut + ((value - min) / span) * (maxOut - minOut));
}

function points(x, y) {
  return x.map((value, index) => `${value.toFixed(1)},${y[index].toFixed(1)}`).join(' ');
}

export function sensorChart(history) {
  if (!history?.length) return "<div class='metric-empty'>No telemetry history loaded.</div>";
  const width = 1000, height = 150, left = 38, right = 16, top = 10, bottom = 24;
  const xs = history.map(row => Number(row.cycle));
  const x = scale(xs, left, width - right);
  const series = [
    {key: 'sensor_2', className: 'chart-line-blue'},
    {key: 'sensor_4', className: 'chart-line-teal'},
    {key: 'sensor_15', className: 'chart-line-amber'},
  ];
  const lines = series.map(item => {
    const raw = history.map(row => Number(row[item.key]));
    const normalized = scale(raw, height - bottom, top);
    return `<polyline class="${item.className}" points="${points(x, normalized)}"></polyline>`;
  }).join('');

  const grids = [0.2,0.4,0.6,0.8].map(frac => {
    const y = top + frac * (height - top - bottom);
    return `<line class="chart-grid" x1="${left}" y1="${y}" x2="${width-right}" y2="${y}"/>`;
  }).join('');
  const labels = [xs[0], xs[Math.floor(xs.length/2)], xs[xs.length-1]].map((label,index) => {
    const xpos = index === 0 ? left : index === 1 ? width/2 : width-right;
    return `<text class="chart-axis" x="${xpos}" y="${height-5}" text-anchor="${index===0?'start':index===2?'end':'middle'}">${label}</text>`;
  }).join('');
  return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}">${grids}${lines}${labels}</svg>`;
}

export function degradationChart(history, rul) {
  if (!history?.length) return "<div class='metric-empty'>No trajectory loaded.</div>";
  const width=980,height=220,left=42,right=18,top=15,bottom=30;
  const cycles=history.map(row=>Number(row.cycle));
  const x=scale(cycles,left,width-right);
  const s4=history.map(row=>Number(row.sensor_4));
  const normalized=scale(s4,0,1);
  const healthY=normalized.map(value=>height-bottom-value*(height-top-bottom));
  const p50=Number(rul?.p50 ?? 50);
  const currentCycle=cycles[cycles.length-1];
  const futureCycle=currentCycle+p50;
  const combinedCycles=[...cycles,futureCycle];
  const projectedX=scale(combinedCycles,left,width-right);
  const currentX=projectedX[cycles.length-1];
  const maintenanceStart=currentX + (projectedX[projectedX.length-1]-currentX)*0.58;
  const maintenanceWidth=Math.max(5,(projectedX[projectedX.length-1]-maintenanceStart)*0.32);

  const grid=[.25,.5,.75].map(f=>`<line class="chart-grid" x1="${left}" y1="${top+f*(height-top-bottom)}" x2="${width-right}" y2="${top+f*(height-top-bottom)}"/>`).join('');
  return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}">
    ${grid}
    <rect x="${maintenanceStart}" y="${top}" width="${maintenanceWidth}" height="${height-top-bottom}" fill="#fbf1dd" stroke="#ead4a7"/>
    <text class="chart-axis" x="${maintenanceStart+5}" y="${top+13}">Suggested maintenance window</text>
    <polyline class="chart-line-blue" points="${points(projectedX.slice(0,cycles.length),healthY)}"></polyline>
    <line x1="${currentX}" y1="${top}" x2="${currentX}" y2="${height-bottom}" stroke="#738a95" stroke-dasharray="4 4"/>
    <line x1="${currentX}" y1="${healthY[healthY.length-1]}" x2="${projectedX[projectedX.length-1]}" y2="${height-bottom-4}" stroke="#2f77a5" stroke-width="2" stroke-dasharray="6 5"/>
    <text class="chart-axis" x="${left}" y="${height-8}">Cycle ${cycles[0]}</text>
    <text class="chart-axis" x="${currentX}" y="${height-8}" text-anchor="middle">Now ${currentCycle}</text>
    <text class="chart-axis" x="${width-right}" y="${height-8}" text-anchor="end">P50 horizon ${Math.round(futureCycle)}</text>
  </svg>`;
}
