/// Upgrade screen for premium subscription with Stripe integration.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/shared_types.dart';

import '../domain/subscription_entities.dart';
import '../presentation/subscription_notifier.dart';

class UpgradeScreen extends ConsumerStatefulWidget {
  const UpgradeScreen({super.key});

  @override
  ConsumerState<UpgradeScreen> createState() => _UpgradeScreenState();
}

class _UpgradeScreenState extends ConsumerState<UpgradeScreen> {
  final _formKey = GlobalKey<FormState>();
  final _paymentMethodController = TextEditingController();
  bool _isProcessing = false;

  @override
  void dispose() {
    _paymentMethodController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // final subscriptionState = ref.watch(subscriptionStateProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Upgrade to Premium'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: _isProcessing
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildPricingCard(context),
                  const SizedBox(height: 24),
                  _buildFeaturesCard(context),
                  const SizedBox(height: 24),
                  _buildPaymentForm(context),
                  const SizedBox(height: 24),
                  _buildUpgradeButton(context),
                ],
              ),
            ),
    );
  }

  Widget _buildPricingCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const Icon(
              Icons.star,
              size: 64,
              color: Colors.amber,
            ),
            const SizedBox(height: 16),
            Text(
              'Premium Plan',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 8),
            Text(
              '\$1.00',
              style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                color: Theme.of(context).primaryColor,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              'per month',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                'Cancel anytime',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).primaryColor,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeaturesCard(BuildContext context) {
    final premiumFeatures = SubscriptionFeatureAccess.getFeaturesForTier(SubscriptionTier.premium);
    final freeFeatures = SubscriptionFeatureAccess.getFeaturesForTier(SubscriptionTier.free);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'What you get with Premium',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            ...premiumFeatures.entries.map((entry) {
              final isPremiumOnly = !(freeFeatures[entry.key] ?? false);
              return _buildFeatureRow(
                context,
                _getFeatureDisplayName(entry.key),
                isPremiumOnly,
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureRow(BuildContext context, String feature, bool isPremiumOnly) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(
            Icons.check_circle,
            color: isPremiumOnly ? Theme.of(context).primaryColor : Colors.green,
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              feature,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
          if (isPremiumOnly)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                'PREMIUM',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).primaryColor,
                  fontWeight: FontWeight.bold,
                  fontSize: 10,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildPaymentForm(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Payment Information',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            Form(
              key: _formKey,
              child: Column(
                children: [
                  TextFormField(
                    controller: _paymentMethodController,
                    decoration: const InputDecoration(
                      labelText: 'Payment Method ID',
                      hintText: 'Enter Stripe payment method ID',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter a payment method ID';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Note: In a real app, this would integrate with Stripe Elements for secure payment collection.',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUpgradeButton(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: _isProcessing ? null : _handleUpgrade,
        icon: const Icon(Icons.star),
        label: Text(_isProcessing ? 'Processing...' : 'Upgrade to Premium'),
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 16),
        ),
      ),
    );
  }

  Future<void> _handleUpgrade() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isProcessing = true;
    });

    try {
      await ref
          .read(subscriptionStateProvider.notifier)
          .upgradeToPremium(
            _paymentMethodController.text.trim(),
          );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Successfully upgraded to Premium!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to upgrade: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });
      }
    }
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
}
