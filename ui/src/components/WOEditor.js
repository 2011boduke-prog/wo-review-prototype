import { useMemo, useState } from 'react';

function stringifyMaybe(value) {
  if (typeof value === 'string') return value;
  if (value == null) return '';
  return JSON.stringify(value, null, 2);
}

function WOEditor({ workOrder, onUpdated, apiBase }) {
  const initialCorrections = useMemo(
    () => stringifyMaybe(workOrder.corrections || workOrder.extracted || {}),
    [workOrder]
  );
  const [correctionsText, setCorrectionsText] = useState(initialCorrections);
  const [message, setMessage] = useState('');
  const [saving, setSaving] = useState(false);

  const save = async (approved = false) => {
    setSaving(true);
    setMessage('');
    try {
      let correctedFields = {};
      if (correctionsText.trim()) {
        correctedFields = JSON.parse(correctionsText);
      }

      const response = await fetch(`${apiBase}/work_order/${workOrder.wo}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ corrected_fields: correctedFields, approved })
      });

      if (!response.ok) {
        throw new Error(`Update failed: ${response.status}`);
      }

      const updated = await response.json();
      onUpdated(updated);
      setMessage(approved ? 'Approved and saved.' : 'Saved.');
    } catch (err) {
      setMessage(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="grid">
      <div className="card">
        <h3>Raw Work Order Text</h3>
        <p><strong>WO:</strong> {workOrder.wo}</p>
        <p><strong>Asset:</strong> {workOrder.asset}</p>
        <p><strong>Status:</strong> {workOrder.status}</p>
        <p>{workOrder.raw_text}</p>
      </div>

      <div className="card">
        <h3>Extracted / Corrected Fields (JSON)</h3>
        <div className="field">
          <textarea
            rows="16"
            value={correctionsText}
            onChange={(e) => setCorrectionsText(e.target.value)}
          />
        </div>
        <div className="actions">
          <button type="button" onClick={() => save(false)} disabled={saving}>Save</button>
          <button type="button" onClick={() => save(true)} disabled={saving}>Approve</button>
        </div>
        {message ? <p>{message}</p> : null}
      </div>
    </div>
  );
}

export default WOEditor;
