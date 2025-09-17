/// Subscription status screen showing current subscription details.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/shared_types.dart';

import '../domain/subscription_entities.dart';
import '../presentation/subscription_notifier.dart';
import 'upgrade_screen.dart';
import 'subscription_management_screen.dart';

class SubscriptionStatusScreen extends ConsumerWidget {
  const SubscriptionStatusScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final subscriptionState = ref.watch(subscriptionStateProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Subscription'),
        actions: [
          if (subscriptionState.isPremium)
            IconButton(
              icon: const Icon(Icons.settings),
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const SubscriptionManagementScreen(),
                  ),
                );
              },
            ),
        ],
      ),
      body: subscriptionState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : subscriptionState.error != null
          ? _buildErrorState(context, ref, subscriptionState.error!)
          : _buildContent(context, ref, subscriptionState),
    );
  }

  Widget _buildErrorState(BuildContext context, WidgetRef ref, String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.red,
          ),
          const SizedBox(height: 16),
          Text(
            'Error loading subscription',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            error,
            style: Theme.of(context).textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => ref.read(subscriptionStateProvider.notifier).refresh(),
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildContent(BuildContext context, WidgetRef ref, SubscriptionState state) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSubscriptionCard(context, state),
          const SizedBox(height: 24),
          _buildFeaturesCard(context, state),
          const SizedBox(height: 24),
          _buildActionButtons(context, ref, state),
        ],
      ),
    );
  }

  Widget _buildSubscriptionCard(BuildContext context, SubscriptionState state) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  state.isPremium ? Icons.star : Icons.person,
                  color: state.isPremium ? Colors.amber : Colors.grey,
                ),
                const SizedBox(width: 8),
                Text(
                  state.isPremium ? 'Premium Plan' : 'Free Plan',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              state.isPremium ? 'You have access to all premium features' : 'Upgrade to unlock premium features',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            if (state.subscription != null) ...[
              const SizedBox(height: 16),
              _buildSubscriptionDetails(context, state.subscription!),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSubscriptionDetails(BuildContext context, Subscription subscription) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildDetailRow(context, 'Status', subscription.status.value),
        if (subscription.currentPeriodStart != null)
          _buildDetailRow(
            context,
            'Billing Period',
            '${_formatDate(subscription.currentPeriodStart!)} - ${_formatDate(subscription.currentPeriodEnd!)}',
          ),
        if (subscription.cancelledAt != null)
          _buildDetailRow(
            context,
            'Cancelled',
            _formatDate(subscription.cancelledAt!),
          ),
      ],
    );
  }

  Widget _buildDetailRow(BuildContext context, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeaturesCard(BuildContext context, SubscriptionState state) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Features',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            ...SubscriptionFeatureAccess.getFeaturesForTier(
              state.isPremium ? SubscriptionTier.premium : SubscriptionTier.free,
            ).entries.map((entry) => _buildFeatureRow(context, entry.key, entry.value)),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureRow(BuildContext context, String feature, bool hasAccess) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(
            hasAccess ? Icons.check_circle : Icons.cancel,
            color: hasAccess ? Colors.green : Colors.grey,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _getFeatureDisplayName(feature),
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: hasAccess ? null : Colors.grey,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButtons(BuildContext context, WidgetRef ref, SubscriptionState state) {
    return Column(
      children: [
        if (!state.isPremium) ...[
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const UpgradeScreen(),
                  ),
                );
              },
              icon: const Icon(Icons.star),
              label: const Text('Upgrade to Premium'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],
        if (state.isPremium) ...[
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const SubscriptionManagementScreen(),
                  ),
                );
              },
              icon: const Icon(Icons.settings),
              label: const Text('Manage Subscription'),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ),
        ],
      ],
    );
  }

  String _getFeatureDisplayName(String feature) {
    switch (feature) {
      case 'daily_quotes':
        return 'Daily Quote Delivery';
      case 'basic_notifications':
        return 'Basic Notifications';
      case 'quote_starring':
        return 'Quote Starring';
      case 'unlimited_starred_quotes':
        return 'Unlimited Starred Quotes';
      case 'quote_search':
        return 'Quote Search';
      case 'advanced_notifications':
        return 'Advanced Notifications';
      case 'quote_history':
        return 'Quote History Archive';
      case 'priority_support':
        return 'Priority Support';
      case 'export_quotes':
        return 'Export Quotes';
      case 'custom_quote_categories':
        return 'Custom Categories';
      default:
        return feature.replaceAll('_', ' ').split(' ').map((word) => word.isEmpty ? word : word[0].toUpperCase() + word.substring(1)).join(' ');
    }
  }

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      return '${date.day}/${date.month}/${date.year}';
    } catch (e) {
      return dateString;
    }
  }
}
