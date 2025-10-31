import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetch("http://localhost:8000/")
      .then((res) => res.json())
      .then((data) => {
        setMessage(data.message);
        setLoading(false);
      })
      .catch(() => {
        setMessage("Failed to connect to backend");
        setLoading(false);
      });
  }, []);

  return (
    <div className="app">
      <h1>React Frontend</h1>
      <div className="card">{loading ? <p>Loading...</p> : <p>Backend says: {message}</p>}</div>
    </div>
  );
}

export default App;
