import { useState } from 'react';

function SearchBar({ onSearch, loading }) {
  const [q, setQ] = useState('');
  const [asset, setAsset] = useState('');
  const [wo, setWo] = useState('');
  const [limit, setLimit] = useState(25);

  const submit = (event) => {
    event.preventDefault();
    onSearch({ q, asset, wo, limit });
  };

  return (
    <form className="card" onSubmit={submit}>
      <div className="field">
        <label htmlFor="q">Query</label>
        <input id="q" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <div className="field">
        <label htmlFor="asset">Asset</label>
        <input id="asset" value={asset} onChange={(e) => setAsset(e.target.value)} />
      </div>
      <div className="field">
        <label htmlFor="wo">WO</label>
        <input id="wo" value={wo} onChange={(e) => setWo(e.target.value)} />
      </div>
      <div className="field">
        <label htmlFor="limit">Limit</label>
        <input
          id="limit"
          type="number"
          min="1"
          max="200"
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value || 25))}
        />
      </div>
      <button type="submit" disabled={loading}>{loading ? 'Searching...' : 'Search'}</button>
    </form>
  );
}

export default SearchBar;
