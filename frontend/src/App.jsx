import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [documentId, setDocumentId] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [deletingDocumentId, setDeletingDocumentId] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const fetchDocuments = async () => {
    setLoadingDocuments(true);

    try {
      const response = await fetch(`${API_URL}/documents/`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to load previous DPRs.");
      }

      setDocuments(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Could not load previous DPRs.");
    } finally {
      setLoadingDocuments(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const uploadDocument = async () => {
    if (!file) {
      setError("Please select a PDF first.");
      return;
    }

    setError("");
    setNotice("");
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setDocumentId(String(data.document_id));
      setAnalysis(null);
      setNotice(
        `Document uploaded successfully. Document ID: #${data.document_id}`
      );
      await fetchDocuments();
    } catch (err) {
      setError(err.message || "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const analyzeDocument = async () => {
    if (!documentId) {
      setError("Select or upload a document first.");
      return;
    }

    setError("");
    setNotice("");
    setAnalyzing(true);

    try {
      const response = await fetch(
        `${API_URL}/documents/${documentId}/analyze`,
        { method: "POST" }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Analysis failed.");
      }

      setAnalysis(data);
      setNotice("DPR analysis completed and saved.");
      await fetchDocuments();
    } catch (err) {
      setError(err.message || "Analysis failed.");
    } finally {
      setAnalyzing(false);
    }
  };

  const deleteDocument = async (id, filename) => {
    const confirmed = window.confirm(
      `Are you sure you want to permanently delete "${filename}" and its saved analysis? This cannot be undone.`
    );

    if (!confirmed) return;

    setError("");
    setNotice("");
    setDeletingDocumentId(id);

    try {
      const response = await fetch(`${API_URL}/documents/${id}`, {
        method: "DELETE",
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || "Failed to delete DPR.");
      }

      setDocuments((previous) =>
        previous.filter((doc) => String(doc.id) !== String(id))
      );

      if (String(documentId) === String(id)) {
        setDocumentId("");
        setAnalysis(null);
      }

      setNotice(`"${filename}" was deleted successfully.`);
    } catch (err) {
      setError(err.message || "Could not delete DPR.");
    } finally {
      setDeletingDocumentId(null);
    }
  };

  const viewPreviousDPR = async (id) => {
    setError("");
    setNotice("");
    setAnalyzing(true);
    setDocumentId(String(id));

    try {
      const response = await fetch(`${API_URL}/documents/${id}/analysis`);
      const data = await response.json();

      if (response.status === 404) {
        setAnalysis(null);
        setNotice(
          `DPR #${id} is saved, but it has no saved analysis yet. Click "Analyze Document" to analyze it now.`
        );
        return;
      }

      if (!response.ok) {
        throw new Error(data.detail || "Could not retrieve this DPR analysis.");
      }

      setAnalysis(data);
      setNotice(`Loaded saved analysis for ${data.filename}.`);
    } catch (err) {
      setError(err.message || "Could not retrieve this DPR.");
    } finally {
      setAnalyzing(false);
    }
  };

  const getHealthLabel = (score) => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    if (score >= 40) return "Needs Attention";
    return "Critical";
  };

  const getRiskLabel = (score) => {
    if (score <= 30) return "Low";
    if (score <= 60) return "Medium";
    return "High";
  };

  const formatDate = (value) => {
    if (!value) return "Date unavailable";
    const date = new Date(value);
    return Number.isNaN(date.getTime())
      ? "Date unavailable"
      : date.toLocaleDateString();
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>DPR Intelligence</h1>
          <p>AI-powered project report analysis</p>
        </div>
        <div className="status-badge">● AI Analysis</div>
      </header>

      <main className="container">
        <section className="upload-card">
          <div className="section-heading">
            <div>
              <h2>Analyze a DPR</h2>
              <p>
                Upload a project report and let AI extract project intelligence.
              </p>
            </div>
          </div>

          <div className="upload-area">
            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={(event) => {
                setFile(event.target.files?.[0] || null);
                setAnalysis(null);
                setDocumentId("");
                setError("");
                setNotice("");
              }}
            />

            {file && (
              <div className="selected-file">
                <span>📄</span>
                <div>
                  <strong>{file.name}</strong>
                  <small>{(file.size / 1024 / 1024).toFixed(2)} MB</small>
                </div>
              </div>
            )}

            <button
              className="primary-button"
              onClick={uploadDocument}
              disabled={uploading || !file}
            >
              {uploading ? "Uploading..." : "Upload DPR"}
            </button>

            {documentId && (
              <button
                className="analyze-button"
                onClick={analyzeDocument}
                disabled={analyzing || deletingDocumentId !== null}
              >
                {analyzing ? "Loading..." : "Analyze Document"}
              </button>
            )}
          </div>

          {notice && <div className="success-message">{notice}</div>}
          {error && <div className="error-message">{error}</div>}
        </section>

        <section className="content-card previous-dpr-card">
          <div className="section-heading previous-dpr-heading">
            <div>
              <h2>Previous DPRs</h2>
              <p>Open a previously uploaded report and retrieve its saved analysis.</p>
            </div>

            <button
              className="view-button"
              onClick={fetchDocuments}
              disabled={loadingDocuments || deletingDocumentId !== null}
            >
              {loadingDocuments ? "Refreshing..." : "Refresh"}
            </button>
          </div>

          {loadingDocuments && documents.length === 0 ? (
            <p className="empty-state">Loading previous DPRs...</p>
          ) : documents.length === 0 ? (
            <p className="empty-state">
              No previous DPRs found. Upload a PDF to get started.
            </p>
          ) : (
            <div className="previous-dpr-list">
              {documents.map((doc) => (
                <div className="previous-dpr-item" key={doc.id}>
                  <div className="dpr-file-info">
                    <div className="dpr-file-icon">📄</div>
                    <div className="dpr-file-text">
                      <strong>{doc.filename}</strong>
                      <div className="dpr-meta">
                        <span>ID #{doc.id}</span>
                        <span>•</span>
                        <span>{doc.pages} pages</span>
                        <span>•</span>
                        <span>{formatDate(doc.created_at)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="dpr-actions">
                    <button
                      className="view-button"
                      onClick={() => viewPreviousDPR(doc.id)}
                      disabled={
                        analyzing ||
                        deletingDocumentId !== null
                      }
                    >
                      {analyzing && String(documentId) === String(doc.id)
                        ? "Loading..."
                        : "View Analysis"}
                    </button>

                    <button
                      className="delete-button"
                      onClick={() => deleteDocument(doc.id, doc.filename)}
                      disabled={
                        deletingDocumentId !== null || analyzing
                      }
                      aria-label={`Delete ${doc.filename}`}
                    >
                      {String(deletingDocumentId) === String(doc.id)
                        ? "Deleting..."
                        : "Delete"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {analysis && (
          <>
            <section className="scores-grid">
              <div className="score-card health">
                <div className="score-header">
                  <span>Project Health</span>
                  <span className="score-icon">♥</span>
                </div>
                <div className="score-value">
                  {analysis.scores?.health_score ?? 0}
                  <span>/100</span>
                </div>
                <div className="score-label">
                  {getHealthLabel(analysis.scores?.health_score ?? 0)}
                </div>
                <div className="progress">
                  <div
                    className="progress-fill health-fill"
                    style={{
                      width: `${analysis.scores?.health_score ?? 0}%`,
                    }}
                  />
                </div>
              </div>

              <div className="score-card risk">
                <div className="score-header">
                  <span>Risk Score</span>
                  <span className="score-icon">!</span>
                </div>
                <div className="score-value">
                  {analysis.scores?.risk_score ?? 0}
                  <span>/100</span>
                </div>
                <div className="score-label">
                  {getRiskLabel(analysis.scores?.risk_score ?? 0)}
                </div>
                <div className="progress">
                  <div
                    className="progress-fill risk-fill"
                    style={{
                      width: `${analysis.scores?.risk_score ?? 0}%`,
                    }}
                  />
                </div>
              </div>

              <div className="score-card completeness">
                <div className="score-header">
                  <span>Data Completeness</span>
                  <span className="score-icon">◉</span>
                </div>
                <div className="score-value">
                  {analysis.scores?.data_completeness ?? 0}
                  <span>%</span>
                </div>
                <div className="score-label">Information Coverage</div>
                <div className="progress">
                  <div
                    className="progress-fill completeness-fill"
                    style={{
                      width: `${analysis.scores?.data_completeness ?? 0}%`,
                    }}
                  />
                </div>
              </div>

              <div className="score-card risk-level">
                <div className="score-header">
                  <span>Risk Level</span>
                  <span className="score-icon">◆</span>
                </div>
                <div className="risk-level-value">
                  {analysis.scores?.risk_level ?? "Unknown"}
                </div>
                <div className="score-label">Overall Project Risk</div>
              </div>
            </section>

            <section className="content-card">
              <div className="card-title">
                <span>Executive Summary</span>
              </div>
              <p className="summary">
                {analysis.analysis?.executive_summary ||
                  "No executive summary available."}
              </p>
            </section>

            <section className="content-card">
              <div className="card-title">
                <span>Project Details</span>
              </div>
              <div className="details-grid">
                <div>
                  <label>Project Name</label>
                  <p>
                    {analysis.analysis?.project_details?.project_name ||
                      "Not specified"}
                  </p>
                </div>
                <div>
                  <label>Project Type</label>
                  <p>
                    {analysis.analysis?.project_details?.project_type ||
                      "Not specified"}
                  </p>
                </div>
                <div>
                  <label>Objective</label>
                  <p>
                    {analysis.analysis?.project_details?.objective ||
                      "Not specified"}
                  </p>
                </div>
                <div>
                  <label>Duration</label>
                  <p>
                    {analysis.analysis?.project_details?.duration ||
                      "Not specified"}
                  </p>
                </div>
              </div>
            </section>

            <section className="intelligence-grid">
              <div className="content-card intelligence-card">
                <div className="card-title">
                  <span>Financial Intelligence</span>
                </div>
                <div className="intelligence-row">
                  <label>Budget</label>
                  <p>
                    {analysis.analysis?.financials?.budget ||
                      "Not specified in document"}
                  </p>
                </div>
                <div className="intelligence-row">
                  <label>Funding</label>
                  <p>
                    {analysis.analysis?.financials?.funding ||
                      "Not specified in document"}
                  </p>
                </div>
                <div className="intelligence-score">
                  <div className="intelligence-score-header">
                    <span>Financial Completeness</span>
                    <strong>
                      {analysis.analysis?.financials?.financial_completeness ??
                        0}
                      %
                    </strong>
                  </div>
                  <div className="progress">
                    <div
                      className="progress-fill completeness-fill"
                      style={{
                        width: `${
                          analysis.analysis?.financials?.financial_completeness ??
                          0
                        }%`,
                      }}
                    />
                  </div>
                </div>
              </div>

              <div className="content-card intelligence-card">
                <div className="card-title">
                  <span>Timeline Intelligence</span>
                </div>
                <div className="timeline-grid">
                  <div>
                    <label>Start Date</label>
                    <p>
                      {analysis.analysis?.timeline?.start_date ||
                        "Not specified in document"}
                    </p>
                  </div>
                  <div>
                    <label>End Date</label>
                    <p>
                      {analysis.analysis?.timeline?.end_date ||
                        "Not specified in document"}
                    </p>
                  </div>
                </div>
                <div className="intelligence-row">
                  <label>Duration</label>
                  <p>
                    {analysis.analysis?.timeline?.duration ||
                      "Not specified in document"}
                  </p>
                </div>
                <div className="intelligence-score">
                  <div className="intelligence-score-header">
                    <span>Timeline Completeness</span>
                    <strong>
                      {analysis.analysis?.timeline?.timeline_completeness ?? 0}%
                    </strong>
                  </div>
                  <div className="progress">
                    <div
                      className="progress-fill health-fill"
                      style={{
                        width: `${
                          analysis.analysis?.timeline?.timeline_completeness ?? 0
                        }%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            </section>

            <section className="content-card">
              <div className="card-title">
                <span>Identified Risks</span>
              </div>
              {analysis.analysis?.risks?.length > 0 ? (
                <div className="risk-list">
                  {analysis.analysis.risks.map((risk, index) => {
                    const severity = String(
                      risk.severity || "Medium"
                    ).toLowerCase();

                    return (
                      <div
                        className="risk-item"
                        key={`${risk.risk}-${index}`}
                      >
                        <div>
                          <strong>{risk.risk}</strong>
                        </div>
                        <span className={`severity ${severity}`}>
                          {risk.severity || "Medium"}
                        </span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="empty-state">No major risks identified.</p>
              )}
            </section>

            <section className="content-card">
              <div className="card-title">
                <span>Missing Information</span>
              </div>
              {analysis.analysis?.missing_information?.length > 0 ? (
                <ul className="bullet-list">
                  {analysis.analysis.missing_information.map((item, index) => (
                    <li key={`${item}-${index}`}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p className="empty-state">
                  No major information gaps identified.
                </p>
              )}
            </section>

            <section className="content-card">
              <div className="card-title">
                <span>AI Recommendations</span>
              </div>
              {analysis.analysis?.recommendations?.length > 0 ? (
                <div className="recommendation-list">
                  {analysis.analysis.recommendations.map(
                    (recommendation, index) => (
                      <div
                        className="recommendation-item"
                        key={`${recommendation}-${index}`}
                      >
                        <span>{index + 1}</span>
                        <p>{recommendation}</p>
                      </div>
                    )
                  )}
                </div>
              ) : (
                <p className="empty-state">No recommendations available.</p>
              )}
            </section>
          </>
        )}
      </main>

      <footer>DPR Intelligence System • AI-powered project intelligence</footer>
    </div>
  );
}

export default App;
