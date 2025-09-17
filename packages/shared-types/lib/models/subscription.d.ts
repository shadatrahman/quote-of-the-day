/**
 * Subscription model and related types for Quote of the Day application.
 */
import { SubscriptionTier } from './user';
export declare enum SubscriptionStatus {
    ACTIVE = "ACTIVE",
    CANCELLED = "CANCELLED",
    PAST_DUE = "PAST_DUE",
    INCOMPLETE = "INCOMPLETE"
}
export interface Subscription {
    id: string;
    user_id: string;
    tier: SubscriptionTier;
    status: SubscriptionStatus;
    stripe_customer_id: string | null;
    stripe_subscription_id: string | null;
    current_period_start: string | null;
    current_period_end: string | null;
    cancelled_at: string | null;
    created_at: string;
    updated_at: string;
}
export interface SubscriptionCreate {
    tier: SubscriptionTier;
    stripe_customer_id?: string;
    stripe_subscription_id?: string;
    current_period_start?: string;
    current_period_end?: string;
}
export interface SubscriptionUpdate {
    status?: SubscriptionStatus;
    stripe_customer_id?: string;
    stripe_subscription_id?: string;
    current_period_start?: string;
    current_period_end?: string;
    cancelled_at?: string;
}
export interface SubscriptionUpgradeRequest {
    payment_method_id: string;
}
export interface SubscriptionCancelRequest {
    reason?: string;
}
export interface SubscriptionStatusResponse {
    subscription: Subscription | null;
    is_premium: boolean;
    features: SubscriptionFeatures;
}
export interface SubscriptionFeatures {
    daily_quotes: boolean;
    basic_notifications: boolean;
    quote_starring: boolean;
    unlimited_starred_quotes: boolean;
    quote_search: boolean;
    advanced_notifications: boolean;
    quote_history: boolean;
    priority_support: boolean;
    export_quotes: boolean;
    custom_quote_categories: boolean;
}
export interface StripeConfig {
    publishable_key: string;
    premium_price_id: string;
}
export interface StripeWebhookEvent {
    id: string;
    type: string;
    data: Record<string, any>;
    created: number;
}
//# sourceMappingURL=subscription.d.ts.map