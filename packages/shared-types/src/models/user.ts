/**
 * User model and related types for Quote of the Day application.
 */

export interface NotificationSettings {
  enabled: boolean;
  delivery_time: string; // HH:MM format
  weekdays_only: boolean;
  pause_until: string | null; // ISO date string
}

export enum SubscriptionTier {
  FREE = "FREE",
  PREMIUM = "PREMIUM"
}

export interface User {
  id: string; // UUID primary key
  email: string; // Email for authentication
  is_active: boolean; // Account status
  is_verified: boolean; // Email verification status
  subscription_tier: SubscriptionTier; // Default to FREE
  timezone: string; // User's timezone
  notification_settings: NotificationSettings;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  last_login_at: string | null; // ISO date string
  last_quote_delivered: string | null; // ISO date string
}

export interface UserCreate {
  email: string;
  password: string;
  password_confirm: string;
  timezone: string;
  notification_settings: NotificationSettings;
}

export interface UserUpdate {
  timezone?: string;
  notification_settings?: NotificationSettings;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface EmailVerificationRequest {
  token: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
  password_confirm: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
  password_confirm: string;
}

export interface ApiError {
  code: string;
  message: string;
  timestamp: string;
  request_id?: string;
}
