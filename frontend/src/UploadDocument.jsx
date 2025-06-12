import React, { useState } from "react";

export default function UploadDocument() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError("");
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Wybierz plik PDF, CSV lub HTML.");
      return;
    }
    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Błąd podczas przesyłania pliku");
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div style={{ marginBottom: "2rem" }}>
      <h2>Prześlij dokument (PDF, CSV, HTML)</h2>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept=".pdf,.csv,.html"
          onChange={handleFileChange}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Wysyłanie..." : "Wyślij"}
        </button>
      </form>
      {error && <div style={{ color: "red" }}>{error}</div>}
      {result && (
        <div style={{ marginTop: "1rem" }}>
          <b>Wynik:</b>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
