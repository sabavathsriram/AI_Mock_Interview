import { resumeService, type ResumeUploadResponse, type ResumeDetailResponse, type ResumeListResponse, type FileSupportInfo, type UploadProgress } from './api'

export type { ResumeUploadResponse, ResumeDetailResponse, ResumeListResponse, FileSupportInfo, UploadProgress }

export async function uploadResume(
  file: File,
  displayName?: string,
  isPrimary?: boolean,
  onProgress?: (progress: UploadProgress) => void,
  _token?: string,
): Promise<ResumeUploadResponse> {
  const response = await resumeService.uploadResume(file, displayName, isPrimary ?? false, onProgress)
  return response.data
}

export async function listResumes(_token?: string): Promise<ResumeListResponse> {
  const response = await resumeService.listResumes()
  return response.data
}

export async function getResume(resumeId: string, _token?: string): Promise<ResumeDetailResponse> {
  const response = await resumeService.getResume(resumeId)
  return response.data
}

export async function deleteResume(resumeId: string, _token?: string): Promise<{ success: boolean; message: string }> {
  const response = await resumeService.deleteResume(resumeId)
  return response.data
}

export async function getSupportedFormats(): Promise<FileSupportInfo> {
  const response = await resumeService.getSupportedFormats()
  return response.data
}

export async function validateFile(file: File): Promise<{ valid: boolean; error?: string }> {
  return resumeService.validateFile(file)
}

export function getFileTypeLabel(fileType: string): string {
  return fileType.replace(/^\./, '').toUpperCase()
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const units = ['Bytes', 'KB', 'MB', 'GB']
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  return `${Math.round((bytes / 1024 ** index) * 100) / 100} ${units[index]}`
}

export const ResumeService = {
  uploadResume,
  listResumes,
  getResume,
  deleteResume,
  getSupportedFormats,
  validateFile,
  getFileTypeLabel,
  formatFileSize,
}
