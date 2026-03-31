class ValidationModel {
  final String pnr;
  final String passenger;

  const ValidationModel({required this.pnr, required this.passenger});

  factory ValidationModel.fromJson(Map<String, dynamic> json) {
    return ValidationModel(
      pnr: json['pnr']?.toString() ?? 'unknown',
      passenger: json['passenger']?.toString() ?? 'unknown',
    );
  }
}

class FlightOptionModel {
  final String flight;
  final String time;
  final String status;

  const FlightOptionModel({
    required this.flight,
    required this.time,
    required this.status,
  });

  factory FlightOptionModel.fromJson(Map<String, dynamic> json) {
    return FlightOptionModel(
      flight: json['flight']?.toString() ?? '-',
      time: json['time']?.toString() ?? '-',
      status: json['status']?.toString() ?? '-',
    );
  }
}

class OriginalFlightModel {
  final String airline;
  final String flight;
  final String route;
  final String date;
  final String status;

  const OriginalFlightModel({
    required this.airline,
    required this.flight,
    required this.route,
    required this.date,
    required this.status,
  });

  factory OriginalFlightModel.fromJson(Map<String, dynamic> json) {
    return OriginalFlightModel(
      airline: json['airline']?.toString() ?? 'unknown',
      flight: json['flight']?.toString() ?? 'unknown',
      route: json['route']?.toString() ?? 'unknown',
      date: json['date']?.toString() ?? 'unknown',
      status: json['status']?.toString() ?? 'unknown',
    );
  }
}

class TriggeredRuleModel {
  final int ruleId;
  final String field;
  final String operator;
  final String value;
  final String action;
  final int priority;

  const TriggeredRuleModel({
    required this.ruleId,
    required this.field,
    required this.operator,
    required this.value,
    required this.action,
    required this.priority,
  });

  factory TriggeredRuleModel.fromJson(Map<String, dynamic> json) {
    return TriggeredRuleModel(
      ruleId: int.tryParse(json['rule_id']?.toString() ?? '0') ?? 0,
      field: json['field']?.toString() ?? '',
      operator: json['operator']?.toString() ?? '=',
      value: json['value']?.toString() ?? '',
      action: json['action']?.toString() ?? '',
      priority: int.tryParse(json['priority']?.toString() ?? '0') ?? 0,
    );
  }
}

class AxiomResponse {
  final String status;
  final String eventType;
  final ValidationModel validation;
  final String ruleApplied;
  final String justification;
  final List<FlightOptionModel> options;
  final String actionRequired;
  final int analysisTimeMs;
  final OriginalFlightModel originalFlight;
  final List<String> flow;
  final List<String> auditTrace;
  final String engineMode;
  final List<TriggeredRuleModel> triggeredRules;

  const AxiomResponse({
    required this.status,
    required this.eventType,
    required this.validation,
    required this.ruleApplied,
    required this.justification,
    required this.options,
    required this.actionRequired,
    required this.analysisTimeMs,
    required this.originalFlight,
    required this.flow,
    required this.auditTrace,
    required this.engineMode,
    required this.triggeredRules,
  });

  factory AxiomResponse.fromJson(Map<String, dynamic> json) {
    final optionsRaw = json['options'] as List<dynamic>? ?? const [];
    final flowRaw = json['flow'] as List<dynamic>? ?? const [];
    final auditRaw = json['audit_trace'] as List<dynamic>? ?? const [];
    final rawTriggered = json['triggered_rules'] as List<dynamic>? ?? const [];

    return AxiomResponse(
      status: json['status']?.toString() ?? 'RECHAZADO',
      eventType: json['event_type']?.toString() ?? 'No clasificado',
      validation: ValidationModel.fromJson(
        (json['validation'] as Map<String, dynamic>? ?? const {}),
      ),
      ruleApplied: json['rule_applied']?.toString() ?? '-',
      justification: json['justification']?.toString() ?? '-',
      options: optionsRaw
          .map(
            (item) => FlightOptionModel.fromJson(item as Map<String, dynamic>),
          )
          .toList(),
      actionRequired: json['action_required']?.toString() ?? '-',
      analysisTimeMs:
          int.tryParse(json['analysis_time_ms']?.toString() ?? '0') ?? 0,
      originalFlight: OriginalFlightModel.fromJson(
        (json['original_flight'] as Map<String, dynamic>? ?? const {}),
      ),
      flow: flowRaw.map((item) => item.toString()).toList(),
      auditTrace: auditRaw.map((item) => item.toString()).toList(),
      engineMode: json['engine_mode']?.toString() ?? 'python',
      triggeredRules: rawTriggered
          .map(
            (item) => TriggeredRuleModel.fromJson(item as Map<String, dynamic>),
          )
          .toList(),
    );
  }
}
