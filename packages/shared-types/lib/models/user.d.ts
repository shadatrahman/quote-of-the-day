/**
 * User model and related types for Quote of the Day application.
 */
export interface NotificationSettings {
    enabled: boolean;
    delivery_time: string;
    weekdays_only: boolean;
    pause_until: string | null;
}
export declare enum SubscriptionTier {
    FREE = "FREE",
    PREMIUM = "PREMIUM"
}
export interface User {
    id: string;
    email: string;
    is_active: boolean;
    is_verified: boolean;
    subscription_tier: SubscriptionTier;
    timezone: string;
    notification_settings: NotificationSettings;
    created_at: string;
    updated_at: string;
    last_login_at: string | null;
    last_quote_delivered: string | null;
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
//# sourceMappingURL=user.d.ts.map