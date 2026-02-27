export type UserRole = 'citizen' | 'lawyer' | 'ngo_admin' | 'court_admin' | 'super_admin';

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  role: UserRole;
  mfaRequired: boolean;
}

export interface PipelineProgressEvent {
  event: 'pipeline.progress';
  payload: {
    documentId: string;
    correlationId: string;
    stage: 'OCR' | 'SIMPLIFICATION' | 'PREDICTION' | 'BLOCKCHAIN';
    progress: number;
    message: string;
  };
}
