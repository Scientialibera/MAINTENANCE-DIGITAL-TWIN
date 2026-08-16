async function parse(response) {
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch (_) {
      // Keep the HTTP fallback message.
    }
    throw new Error(detail);
  }
  return response.json();
}

export async function getFleet() {
  return parse(await fetch('/api/fleet'));
}

export async function getAsset(assetId) {
  return parse(await fetch(`/api/assets/${encodeURIComponent(assetId)}`));
}

export async function simulateAsset(assetId, scenario) {
  return parse(await fetch(`/api/assets/${encodeURIComponent(assetId)}/simulate`, {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify(scenario)
  }));
}

export async function getModelValidation() {
  return parse(await fetch('/api/model/validation'));
}

export async function optimizeMaintenance(payload) {
  return parse(await fetch('/api/maintenance/optimize', {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify(payload)
  }));
}
