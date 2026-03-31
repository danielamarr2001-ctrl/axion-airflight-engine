class RuleModel {
  final int ruleId;
  final String field;
  final String operator;
  final String value;
  final String action;
  final int priority;

  const RuleModel({
    required this.ruleId,
    required this.field,
    required this.operator,
    required this.value,
    required this.action,
    required this.priority,
  });

  factory RuleModel.fromJson(Map<String, dynamic> json) {
    return RuleModel(
      ruleId: int.tryParse(json['rule_id']?.toString() ?? '0') ?? 0,
      field: json['field']?.toString() ?? '',
      operator: json['operator']?.toString() ?? '=',
      value: json['value']?.toString() ?? '',
      action: json['action']?.toString() ?? '',
      priority: int.tryParse(json['priority']?.toString() ?? '1') ?? 1,
    );
  }
}

class RuleDraft {
  final String field;
  final String operator;
  final String value;
  final String action;
  final int priority;

  const RuleDraft({
    required this.field,
    required this.operator,
    required this.value,
    required this.action,
    required this.priority,
  });

  Map<String, dynamic> toJson() {
    return {
      'field': field,
      'operator': operator,
      'value': value,
      'action': action,
      'priority': priority,
    };
  }
}

class RuleCount {
  final String rule;
  final int count;

  const RuleCount({required this.rule, required this.count});

  factory RuleCount.fromJson(Map<String, dynamic> json) {
    return RuleCount(
      rule: json['rule']?.toString() ?? 'unknown',
      count: int.tryParse(json['count']?.toString() ?? '0') ?? 0,
    );
  }
}

class DailyDecision {
  final String day;
  final int count;

  const DailyDecision({required this.day, required this.count});

  factory DailyDecision.fromJson(Map<String, dynamic> json) {
    return DailyDecision(
      day: json['day']?.toString() ?? '-',
      count: int.tryParse(json['count']?.toString() ?? '0') ?? 0,
    );
  }
}

class MetricsModel {
  final int totalRequests;
  final int manualReviews;
  final double avgProcessingTimeMs;
  final List<RuleCount> rulesTriggered;
  final List<DailyDecision> decisionsPerDay;
  final List<RuleCount> topTriggeredRules;
  final List<double> latencySeriesMs;

  const MetricsModel({
    required this.totalRequests,
    required this.manualReviews,
    required this.avgProcessingTimeMs,
    required this.rulesTriggered,
    required this.decisionsPerDay,
    required this.topTriggeredRules,
    required this.latencySeriesMs,
  });

  factory MetricsModel.fromJson(Map<String, dynamic> json) {
    final rawTriggered = json['rules_triggered'] as List<dynamic>? ?? const [];
    final rawDay = json['decisions_per_day'] as List<dynamic>? ?? const [];
    final rawTop = json['top_triggered_rules'] as List<dynamic>? ?? const [];
    final rawLatency = json['latency_series_ms'] as List<dynamic>? ?? const [];

    return MetricsModel(
      totalRequests:
          int.tryParse(json['total_requests']?.toString() ?? '0') ?? 0,
      manualReviews:
          int.tryParse(json['manual_reviews']?.toString() ?? '0') ?? 0,
      avgProcessingTimeMs:
          double.tryParse(json['avg_processing_time_ms']?.toString() ?? '0') ??
              0,
      rulesTriggered: rawTriggered
          .map((item) => RuleCount.fromJson(item as Map<String, dynamic>))
          .toList(),
      decisionsPerDay: rawDay
          .map((item) => DailyDecision.fromJson(item as Map<String, dynamic>))
          .toList(),
      topTriggeredRules: rawTop
          .map((item) => RuleCount.fromJson(item as Map<String, dynamic>))
          .toList(),
      latencySeriesMs: rawLatency
          .map((item) => double.tryParse(item.toString()) ?? 0)
          .toList(),
    );
  }
}
