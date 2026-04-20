import { useEffect, useState } from 'react';
import { BrowserRouter, Link, Route, Routes, useNavigate, useParams } from 'react-router-dom';
import './App.css';
import ResultsList from './components/ResultsList';
import SearchBar from './components/SearchBar';
import WOEditor from './components/WOEditor';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

function SearchScreen() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const runSearch = async ({ q, asset, wo, limit }) => {
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (asset) params.set('asset', asset);
    if (wo) params.set('wo', wo);
    params.set('limit', String(limit || 25));

    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE}/search?${params.toString()}`);
      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h2>Search Work Orders</h2>
      <SearchBar onSearch={runSearch} loading={loading} />
      {error ? <p className="error">{error}</p> : null}
      <ResultsList items={results} onOpen={(woId) => navigate(`/review/${woId}`)} />
    </section>
  );
}

function ReviewScreen() {
  const { woId } = useParams();
  const [workOrder, setWorkOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchWorkOrder = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(`${API_BASE}/work_order/${woId}`);
        if (!response.ok) {
          throw new Error(`Load failed: ${response.status}`);
        }
        const data = await response.json();
        setWorkOrder(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchWorkOrder();
  }, [woId]);

  if (loading) return <p>Loading work order...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!workOrder) return <p>No data found.</p>;

  return (
    <section>
      <h2>Review {workOrder.wo}</h2>
      <WOEditor
        workOrder={workOrder}
        onUpdated={setWorkOrder}
        apiBase={API_BASE}
      />
    </section>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header className="topbar">
          <h1>WO Review Prototype</h1>
          <nav>
            <Link to="/">Search</Link>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<SearchScreen />} />
            <Route path="/review/:woId" element={<ReviewScreen />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
