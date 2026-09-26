/**
 * Resume Upload Component
 * Allows users to upload resumes and displays upload progress
 */

import React, { useState, useRef, useEffect } from "react";
import { ResumeService, FileSupportInfo, UploadProgress } from "../services/resumeService";
import "../styles/ResumeUpload.css";

interface ResumeUploadProps {
  token?: string;
  onSuccess?: (resume: any) => void;
  onError?: (error: string) => void;
}

export const ResumeUpload: React.FC<ResumeUploadProps> = ({
  token = "",
  onSuccess,
  onError,
}) => {
  const [supportedFormats, setSupportedFormats] = useState<FileSupportInfo | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [displayName, setDisplayName] = useState<string>("");
  const [isPrimary, setIsPrimary] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    loaded: 0,
    total: 0,
    percentage: 0,
  });
  const [uploadStatus, setUploadStatus] = useState<
    "idle" | "uploading" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [successMessage, setSuccessMessage] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load supported formats on mount
  useEffect(() => {
    loadSupportedFormats();
  }, []);

  const loadSupportedFormats = async () => {
    try {
      const formats = await ResumeService.getSupportedFormats();
      setSupportedFormats(formats);
    } catch (error) {
      console.error("Failed to load supported formats:", error);
    }
  };

  const handleFileSelect = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file
    const validation = await ResumeService.validateFile(file);

    if (!validation.valid) {
      setSelectedFile(null);
      setErrorMessage(validation.error || "Invalid file");
      setUploadStatus("error");
      setDisplayName("");
      return;
    }

    setSelectedFile(file);
    setErrorMessage("");
    setUploadStatus("idle");
    
    // Auto-fill display name from filename
    const displayName = file.name.substring(0, file.name.lastIndexOf("."));
    setDisplayName(displayName);
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDrop = async (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();

    const file = event.dataTransfer.files?.[0];
    if (!file) return;

    // Validate file
    const validation = await ResumeService.validateFile(file);

    if (!validation.valid) {
      setSelectedFile(null);
      setErrorMessage(validation.error || "Invalid file");
      setUploadStatus("error");
      return;
    }

    setSelectedFile(file);
    setErrorMessage("");
    setUploadStatus("idle");

    // Auto-fill display name from filename
    const displayName = file.name.substring(0, file.name.lastIndexOf("."));
    setDisplayName(displayName);
  };

  const handleUpload = async () => {
    if (!selectedFile || !token) {
      setErrorMessage("File selection or authentication issue");
      setUploadStatus("error");
      return;
    }

    setUploading(true);
    setUploadStatus("uploading");
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const resume = await ResumeService.uploadResume(
        selectedFile,
        displayName || undefined,
        isPrimary,
        (progress) => {
          setUploadProgress(progress);
        },
        token
      );

      setUploadStatus("success");
      setSuccessMessage(
        `Resume "${resume.display_name}" uploaded successfully!`
      );
      setSelectedFile(null);
      setDisplayName("");
      setUploadProgress({ loaded: 0, total: 0, percentage: 0 });

      // Clear input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      // Call success callback
      onSuccess?.(resume);

      // Clear success message after 5 seconds
      setTimeout(() => {
        setSuccessMessage("");
        setUploadStatus("idle");
      }, 5000);
    } catch (error: any) {
      const errorMsg =
        error.response?.data?.detail ||
        error.message ||
        "Upload failed. Please try again.";

      setErrorMessage(errorMsg);
      setUploadStatus("error");
      onError?.(errorMsg);
    } finally {
      setUploading(false);
    }
  };

  const handleClearError = () => {
    setErrorMessage("");
    setUploadStatus("idle");
  };

  return (
    <div className="resume-upload-container">
      <div className="resume-upload-card">
        <h2>Upload Your Resume</h2>

        {/* Supported Formats Info */}
        {supportedFormats && (
          <div className="supported-formats-info">
            <p className="info-label">Supported Formats:</p>
            <div className="format-badges">
              {supportedFormats.supported_formats.map((format) => (
                <span key={format} className="format-badge">
                  {format.substring(1).toUpperCase()}
                </span>
              ))}
            </div>
            <p className="info-label">Max File Size: {supportedFormats.max_file_size_mb} MB</p>
          </div>
        )}

        {/* File Drop Zone */}
        <div
          className={`file-drop-zone ${selectedFile ? "has-file" : ""} ${
            uploadStatus === "error" ? "error" : ""
          }`}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={supportedFormats?.supported_formats.join(",") || ""}
            onChange={handleFileSelect}
            disabled={uploading}
            style={{ display: "none" }}
          />

          {selectedFile ? (
            <div className="file-selected">
              <div className="file-icon">📄</div>
              <div className="file-info">
                <p className="file-name">{selectedFile.name}</p>
                <p className="file-type">
                  {ResumeService.getFileTypeLabel(
                    selectedFile.name.split(".").pop() || ""
                  )}
                </p>
                <p className="file-size">
                  {ResumeService.formatFileSize(selectedFile.size)}
                </p>
              </div>
            </div>
          ) : (
            <div className="file-prompt">
              <div className="upload-icon">📤</div>
              <p className="prompt-text">
                Drag & drop your resume here or click to browse
              </p>
              <p className="prompt-subtext">
                Supported formats: PDF, DOCX, DOC, TXT, RTF, ODT, HTML, Markdown
              </p>
            </div>
          )}
        </div>

        {/* Display Name Input */}
        {selectedFile && (
          <div className="form-group">
            <label htmlFor="displayName">Display Name (optional)</label>
            <input
              id="displayName"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="My First Resume"
              disabled={uploading}
            />
          </div>
        )}

        {/* Primary Resume Checkbox */}
        {selectedFile && (
          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                checked={isPrimary}
                onChange={(e) => setIsPrimary(e.target.checked)}
                disabled={uploading}
              />
              <span>Set as primary resume</span>
            </label>
          </div>
        )}

        {/* Upload Progress */}
        {uploading && (
          <div className="upload-progress">
            <p className="progress-label">Uploading...</p>
            <div className="progress-bar-container">
              <div
                className="progress-bar"
                style={{ width: `${uploadProgress.percentage}%` }}
              ></div>
            </div>
            <p className="progress-text">
              {uploadProgress.percentage}% •{" "}
              {ResumeService.formatFileSize(uploadProgress.loaded)} /{" "}
              {ResumeService.formatFileSize(uploadProgress.total)}
            </p>
          </div>
        )}

        {/* Error Message */}
        {uploadStatus === "error" && errorMessage && (
          <div className="alert alert-error">
            <div className="alert-content">
              <p className="alert-title">Upload Failed</p>
              <p className="alert-message">{errorMessage}</p>
            </div>
            <button
              className="alert-close"
              onClick={handleClearError}
              disabled={uploading}
            >
              ✕
            </button>
          </div>
        )}

        {/* Success Message */}
        {uploadStatus === "success" && successMessage && (
          <div className="alert alert-success">
            <div className="alert-content">
              <p className="alert-title">✓ Success</p>
              <p className="alert-message">{successMessage}</p>
            </div>
          </div>
        )}

        {/* Upload Button */}
        {selectedFile && uploadStatus !== "success" && (
          <div className="button-group">
            <button
              className="btn btn-primary"
              onClick={handleUpload}
              disabled={uploading || !token}
            >
              {uploading ? "Uploading..." : "Upload Resume"}
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => {
                setSelectedFile(null);
                setDisplayName("");
                setUploadStatus("idle");
                if (fileInputRef.current) {
                  fileInputRef.current.value = "";
                }
              }}
              disabled={uploading}
            >
              Clear
            </button>
          </div>
        )}

        {/* Success Action Buttons */}
        {uploadStatus === "success" && (
          <div className="button-group">
            <button
              className="btn btn-primary"
              onClick={() => {
                setUploadStatus("idle");
                setSuccessMessage("");
                if (fileInputRef.current) {
                  fileInputRef.current.click();
                }
              }}
            >
              Upload Another Resume
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeUpload;
