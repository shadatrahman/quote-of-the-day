/**
 * Subscription model and related types for Quote of the Day application.
 */

import { SubscriptionTier } from './user';

export enum SubscriptionStatus {
  ACTIVE = "ACTIVE",
  CANCELLED = "CANCELLED",
  PAST_DUE = "PAST_DUE",
  INCOMPLETE = "INCOMPLETE"
}

export interface Subscription {
  id: string; // UUID primary key
  user_id: string; // Foreign key to User
  tier: SubscriptionTier; // Subscription level
  status: SubscriptionStatus; // Payment status
  stripe_customer_id: string | null; // Stripe customer reference
  stripe_subscription_id: string | null; // Stripe subscription reference
  current_period_start: string | null; // Billing cycle start (ISO date)
  current_period_end: string | null; // Billing cycle end (ISO date)
  cancelled_at: string | null; // Cancellation timestamp (ISO date)
  created_at: string; // Subscription creation (ISO date)
  updated_at: string; // Last update (ISO date)
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

