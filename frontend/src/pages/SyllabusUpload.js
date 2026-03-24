import React from "react";
import { useAuth } from "../context/AuthContext";

function SyllabusUpload() {
  const { user } = useAuth();

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Syllabus Upload</h1>
        <p className="page-subtitle">
          Upload your course syllabi and we'll extract deadlines, exams, and assignments automatically.
        </p>
      </div>

      <div className="page-card-grid">
        <div className="upload-zone">
          <div className="upload-icon">{"\uD83D\uDCC1"}</div>
          <div className="upload-text">
            Drag and drop your syllabus here, or click to browse
          </div>
          <div className="upload-hint">
            Supports PDF, DOCX, and TXT — up to 10 MB
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">{user?.display_name}'s Syllabi</h3>
            <span className="card-badge">0 files</span>
          </div>
          <div className="empty-state">
            <div className="empty-state-icon">{"\uD83D\uDCCB"}</div>
            <p className="empty-state-text">
              No syllabi uploaded yet. Upload your first one to get started.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SyllabusUpload;
