import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_URL = "";

const PIPELINE_STEPS = [
  "Worksheet image",
  "Template resolution",
  "Image validation and normalisation gate",
  "Page normalisation",
  "Response-region preparation",
  "Response extraction",
  "Response standardization and locking",
  "Structured-output validation",
  "Response scoring",
  "Exception handling",
  "Result aggregation",
];

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [templates, setTemplates] = useState([]);
  const [runData, setRunData] = useState(null);
  const [selectedStep, setSelectedStep] = useState(0);
  const [completedStep, setCompletedStep] = useState(-1);
  const [loadingStep, setLoadingStep] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/api/workbench/templates`)
      .then((response) => response.json())
      .then((data) => setTemplates(data.templates || []))
      .catch(() => setTemplates([]));
  }, []);

  const steps = useMemo(() => {
    if (runData?.steps?.length) return runData.steps;

    return PIPELINE_STEPS.map((title, index) => ({
      index,
      title,
      step_id: title.toLowerCase().replaceAll(" ", "_"),
      status: "pending",
      component: "Waiting for upload",
      algorithm: "Not run yet",
      purpose: "Run this step to see the input, output and errors.",
      input: {},
      output: {},
      errors: [],
      artifacts: [],
      duration_ms: 0,
    }));
  }, [runData]);

  const currentStep = steps[selectedStep] || steps[0];
  const canRun = Boolean(file) && loadingStep === null;

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;
    if (!selectedFile.type.startsWith("image/")) {
      setError("Please upload a PNG/JPG worksheet image.");
      return;
    }

    if (preview) URL.revokeObjectURL(preview);
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setRunData(null);
    setSelectedStep(0);
    setCompletedStep(-1);
    setError("");
  };

  const runToStep = async (stepIndex) => {
    if (!file) {
      setError("Upload a marked or blank worksheet first.");
      return;
    }

    const safeIndex = Math.max(0, Math.min(stepIndex, PIPELINE_STEPS.length - 1));
    setLoadingStep(safeIndex);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("step_index", String(safeIndex));

      const response = await fetch(`${API_URL}/api/workbench/run`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Pipeline step failed.");
      }

      setRunData(data);
      setSelectedStep(safeIndex);
      setCompletedStep(data.requested_step ?? safeIndex);
    } catch (err) {
      setError(err.message || "Pipeline failed.");
    } finally {
      setLoadingStep(null);
    }
  };

  const resetWorkbench = () => {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null);
    setPreview("");
    setRunData(null);
    setSelectedStep(0);
    setCompletedStep(-1);
    setError("");
  };

  const runNextStep = () => {
    const next = completedStep < 0 ? 0 : completedStep + 1;
    runToStep(Math.min(next, PIPELINE_STEPS.length - 1));
  };

  const statusText = loadingStep !== null ? `Running step ${loadingStep + 1}` : "Ready";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Multifold worksheet marking POC</p>
          <h1>Worksheet Pipeline Workbench</h1>
        </div>
        <div className="server-pill">
          <span className="pulse" />
          {statusText}
        </div>
      </header>

      <main className="layout">
        <aside className="side-panel">
          <section className="panel upload-panel">
            <div className="panel-heading">
              <h2>Input worksheet</h2>
              <span>{file ? "Loaded" : "Waiting"}</span>
            </div>

            <div
              className={`drop-zone ${preview ? "with-preview" : ""}`}
              onDragOver={(event) => event.preventDefault()}
              onDrop={(event) => {
                event.preventDefault();
                handleFile(event.dataTransfer.files[0]);
              }}
              onClick={() => document.getElementById("worksheet-input")?.click()}
            >
              <input
                id="worksheet-input"
                type="file"
                accept="image/*"
                hidden
                onChange={(event) => handleFile(event.target.files[0])}
              />

              {preview ? (
                <img src={preview} alt="Uploaded worksheet preview" />
              ) : (
                <div className="upload-empty">
                  <span className="upload-symbol">+</span>
                  <strong>Upload worksheet image</strong>
                  <small>Blank template or student-marked copy</small>
                </div>
              )}
            </div>

            {file && (
              <div className="file-meta">
                <strong>{file.name}</strong>
                <span>{Math.round(file.size / 1024)} KB</span>
              </div>
            )}

            {runData?.template && (
              <div className="template-result">
                <span>Detected template</span>
                <strong>{runData.template.name}</strong>
                <small>{runData.template.current_solution}</small>
              </div>
            )}

            {error && <div className="error-box">{error}</div>}

            <div className="control-grid">
              <button type="button" onClick={() => runToStep(selectedStep)} disabled={!canRun}>
                Run Step
              </button>
              <button type="button" onClick={runNextStep} disabled={!canRun}>
                Run Next
              </button>
              <button type="button" onClick={() => runToStep(PIPELINE_STEPS.length - 1)} disabled={!canRun}>
                Run All
              </button>
              <button type="button" className="secondary" onClick={resetWorkbench}>
                Reset
              </button>
            </div>
          </section>

          <section className="panel templates-panel">
            <div className="panel-heading">
              <h2>Allowed templates</h2>
              <span>{templates.length || 4}</span>
            </div>
            <div className="template-list">
              {templates.map((template) => (
                <div className="template-item" key={template.template_id}>
                  <strong>{template.name}</strong>
                  <span>
                    {template.mode} - {template.region_count} regions
                  </span>
                </div>
              ))}
            </div>
          </section>
        </aside>

        <section className="pipeline-panel panel">
          <div className="panel-heading">
            <h2>Pipeline steps</h2>
            <span>{completedStep + 1 > 0 ? `${completedStep + 1}/11 run` : "0/11 run"}</span>
          </div>

          <div className="step-list">
            {steps.map((step) => (
              <button
                type="button"
                className={`step-row ${selectedStep === step.index ? "selected" : ""} ${step.status}`}
                key={step.step_id}
                onClick={() => setSelectedStep(step.index)}
              >
                <span className="step-number">{step.index + 1}</span>
                <span className="step-copy">
                  <strong>{step.title}</strong>
                  <small>{step.algorithm}</small>
                </span>
                <span className="step-actions">
                  <span className="status-chip">{loadingStep === step.index ? "running" : step.status}</span>
                  <span
                    className="mini-run"
                    onClick={(event) => {
                      event.stopPropagation();
                      runToStep(step.index);
                    }}
                  >
                    Run
                  </span>
                </span>
              </button>
            ))}
          </div>
        </section>

        <section className="detail-panel panel">
          <div className="panel-heading">
            <h2>Step detail</h2>
            <span>#{(currentStep?.index ?? 0) + 1}</span>
          </div>

          <div className="detail-header">
            <div>
              <h3>{currentStep?.title}</h3>
              <p>{currentStep?.purpose}</p>
            </div>
            <span className={`status-chip large ${currentStep?.status}`}>
              {loadingStep === currentStep?.index ? "running" : currentStep?.status}
            </span>
          </div>

          <div className="method-grid">
            <div>
              <span>Component</span>
              <strong>{currentStep?.component}</strong>
            </div>
            <div>
              <span>Algorithm</span>
              <strong>{currentStep?.algorithm}</strong>
            </div>
            <div>
              <span>Runtime</span>
              <strong>{currentStep?.duration_ms || 0} ms</strong>
            </div>
          </div>

          {currentStep?.errors?.length > 0 && (
            <div className="error-box">
              {currentStep.errors.map((item) => (
                <p key={item}>{item}</p>
              ))}
            </div>
          )}

          <div className="io-grid">
            <JsonBlock title="Step input" value={currentStep?.input} />
            <JsonBlock title="Step output" value={currentStep?.output} />
          </div>

          {currentStep?.artifacts?.length > 0 && (
            <div className="artifacts">
              <h4>Artifacts</h4>
              <div className="artifact-grid">
                {currentStep.artifacts
                  .filter((artifact) => artifact.data_url)
                  .map((artifact) => (
                    <figure key={`${currentStep.step_id}-${artifact.title}`}>
                      <img src={artifact.data_url} alt={artifact.title} />
                      <figcaption>{artifact.title}</figcaption>
                    </figure>
                  ))}
              </div>
            </div>
          )}

          {runData?.summary?.score_label && (
            <section className="summary-band">
              <div>
                <span>Final score</span>
                <strong>{runData.summary.score_label}</strong>
              </div>
              <p>{runData.summary.notes}</p>
            </section>
          )}

          {runData?.results?.length > 0 && (
            <div className="results-table">
              <div className="results-head">
                <span>Region</span>
                <span>Response</span>
                <span>Expected</span>
                <span>Status</span>
              </div>
              {runData.results.map((result) => (
                <div className="results-row" key={result.region_id}>
                  <strong>{result.region_id}</strong>
                  <span>{result.student_response}</span>
                  <span>{result.correct_value || "-"}</span>
                  <span className={`score ${result.score}`}>{result.score}</span>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function JsonBlock({ title, value }) {
  return (
    <div className="json-block">
      <h4>{title}</h4>
      <pre>{JSON.stringify(value || {}, null, 2)}</pre>
    </div>
  );
}

export default App;
