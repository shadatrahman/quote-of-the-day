/**
 * Shared types for Quote of the Day application.
 * This package provides type definitions that can be used across
 * both the backend (Python) and frontend (Flutter/TypeScript) applications.
 */

// Export all user-related types
export * from './models/user';

// Export all subscription-related types
export * from './models/subscription';

// Export common types
export interface ApiResponse<T = any> {
  data?: T;
  error?: {
    code: string;
    message: string;
    timestamp: string;
    request_id?: string;
  };
  meta?: {
    total?: number;
    page?: number;
    limit?: number;
  };
}

export interface PaginatedResponse<T = any> extends ApiResponse<T[]> {
  meta: {
    total: number;
    page: number;
    limit: number;
    total_pages: number;
  };
}
