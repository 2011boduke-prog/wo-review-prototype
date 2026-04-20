function ResultsList({ items, onOpen }) {
  if (!items.length) {
    return <p>No results yet. Run a search.</p>;
  }

  return (
    <div>
      {items.map((item) => (
        <div key={item.wo} className="card">
          <p><strong>{item.wo}</strong> - {item.asset}</p>
          <p>{item.priority} | {item.status} | {item.technician}</p>
          <button type="button" onClick={() => onOpen(item.wo)}>Open</button>
        </div>
      ))}
    </div>
  );
}

export default ResultsList;
