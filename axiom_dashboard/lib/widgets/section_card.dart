import 'package:flutter/material.dart';

class SectionCard extends StatelessWidget {
  final String title;
  final Widget child;
  final Color? accent;

  const SectionCard({
    super.key,
    required this.title,
    required this.child,
    this.accent,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveAccent = accent ?? Theme.of(context).colorScheme.primary;

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF111B24),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: effectiveAccent.withValues(alpha: 0.45),
          width: 1.1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.22),
            blurRadius: 30,
            offset: const Offset(0, 12),
          ),
        ],
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
          ),
          const SizedBox(height: 14),
          child,
        ],
      ),
    );
  }
}
