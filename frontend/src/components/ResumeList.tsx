/**
 * Resume List Component
 * Displays user's uploaded resumes and allows management
 */

import React, { useState, useEffect } from "react";
import {
  ResumeService,
  ResumeDetailResponse,
  ResumeListResponse,
} from "../services/resumeService";
import "../styles/ResumeList.css";

interface ResumeListProps {
  token?: string;
  onResumesLoaded?: (resumes: ResumeDetailResponse[]) => void;
  onError?: (error: string) => void;
}

export const ResumeList: React.FC<ResumeListProps> = ({
  token = "",
  onResumesLoaded,
  onError,
}) => {
  const [resumes, setResumes] = useState<ResumeDetailResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [deleting, setDeleting] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      loadResumes();
    }
  }, [token]);

  const loadResumes = async () => {
    if (!token) return;

    setLoading(true);
    setError("");

    try {
      const response: ResumeListResponse = await ResumeService.listResumes(
        token
      );
      setResumes(response.resumes || []);
      onResumesLoaded?.(response.resumes || []);
    } catch (error: any) {
      const errorMsg =
        error.response?.data?.detail ||
        error.message ||
        "Failed to load resumes";
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (resumeId: string) => {
    if (!token) return;

    if (!window.confirm("Are you sure you want to delete this resume?")) {
      return;
    }

    setDeleting(resumeId);

    try {
      await ResumeService.deleteResume(resumeId, token);
      setResumes(resumes.filter((r) => r.id !== resumeId));
      onResumesLoaded?.(resumes.filter((r) => r.id !== resumeId));
    } catch (error: any) {
      const errorMsg =
        error.response?.data?.detail ||
        error.message ||
        "Failed to delete resume";
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setDeleting(null);
    }
  };

  const toggleExpand = (resumeId: string) => {
    setExpandedId(expandedId === resumeId ? null : resumeId);
  };

  if (!token) {
    return (
      <div className="resume-list-container">
        <div className="empty-state">
          <p>Please log in to view your resumes</p>
        </div>
      </div>
    );
  }

  return (
    <div className="resume-list-container">
      <div className="resume-list-card">
        <div className="resume-list-header">
          <h2>Your Resumes</h2>
          <button
            className="btn btn-refresh"
            onClick={loadResumes}
            disabled={loading}
            title="Refresh"
          >
            🔄
          </button>
        </div>

        {error && (
          <div className="alert alert-error">
            <p>{error}</p>
            <button onClick={() => setError("")}>✕</button>
          </div>
        )}

        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading resumes...</p>
          </div>
        ) : resumes.length === 0 ? (
          <div className="empty-state">
            <p className="empty-icon">📄</p>
            <p className="empty-text">No resumes uploaded yet</p>
            <p className="empty-subtext">
              Upload your first resume to get started
            </p>
          </div>
        ) : (
          <div className="resume-list">
            {resumes.map((resume) => (
              <div key={resume.id} className="resume-item">
                <div
                  className="resume-item-header"
                  onClick={() => toggleExpand(resume.id)}
                >
                  <div className="resume-item-title">
                    <div className="file-icon">📄</div>
                    <div className="resume-info">
                      <h3 className="resume-name">{resume.display_name}</h3>
                      <p className="resume-meta">
                        <span className="file-type">
                          {ResumeService.getFileTypeLabel(resume.file_type)}
                        </span>
                        <span className="separator">•</span>
                        <span className="file-size">
                          {ResumeService.formatFileSize(resume.file_size)}
                        </span>
                        <span className="separator">•</span>
                        <span className="upload-date">
                          {new Date(resume.uploaded_at).toLocaleDateString()}
                        </span>
                        {resume.is_primary && (
                          <>
                            <span className="separator">•</span>
                            <span className="primary-badge">Primary</span>
                          </>
                        )}
                      </p>
                    </div>
                  </div>
                  <div className="resume-item-actions">
                    <span
                      className={`expansion-icon ${
                        expandedId === resume.id ? "expanded" : ""
                      }`}
                    >
                      ▼
                    </span>
                  </div>
                </div>

                {expandedId === resume.id && (
                  <div className="resume-item-details">
                    <div className="detail-section">
                      <h4>File Information</h4>
                      <div className="detail-grid">
                        <div className="detail-item">
                          <span className="detail-label">Filename:</span>
                          <span className="detail-value">{resume.filename}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">File Type:</span>
                          <span className="detail-value">
                            {resume.file_type.toUpperCase()}
                          </span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Extraction Status:</span>
                          <span
                            className={`detail-value status status-${resume.extraction_status}`}
                          >
                            {resume.extraction_status === "success"
                              ? "✓ Success"
                              : resume.extraction_status === "failed"
                              ? "✗ Failed"
                              : "⏳ Pending"}
                          </span>
                        </div>
                      </div>
                    </div>

                    {resume.extraction_metadata &&
                      Object.keys(resume.extraction_metadata).length > 0 && (
                        <div className="detail-section">
                          <h4>Extraction Details</h4>
                          <div className="detail-grid">
                            {Object.entries(resume.extraction_metadata).map(
                              ([key, value]) => (
                                <div key={key} className="detail-item">
                                  <span className="detail-label">
                                    {key
                                      .replace(/_/g, " ")
                                      .replace(/\b\w/g, (l) =>
                                        l.toUpperCase()
                                      )}
                                    :
                                  </span>
                                  <span className="detail-value">
                                    {typeof value === "object"
                                      ? JSON.stringify(value)
                                      : String(value)}
                                  </span>
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      )}

                    {resume.extraction_error && (
                      <div className="detail-section error">
                        <h4>Extraction Error</h4>
                        <p className="error-text">{resume.extraction_error}</p>
                      </div>
                    )}

                    <div className="resume-item-footer">
                      <button
                        className="btn btn-danger"
                        onClick={() => handleDelete(resume.id)}
                        disabled={deleting === resume.id}
                      >
                        {deleting === resume.id ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeList;
