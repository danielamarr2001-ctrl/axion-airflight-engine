import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/axiom_response.dart';
import '../models/rule_platform_models.dart';

class AxiomApiService {
  final String baseUrl;

  const AxiomApiService({
    this.baseUrl = const String.fromEnvironment(
      'AXIOM_API_URL',
      defaultValue: 'http://127.0.0.1:8000',
    ),
  });

  /// PROCESS DECISION REQUEST
  Future<AxiomResponse> processProblem(String problem) async {
    final response = await http.post(
      Uri.parse('$baseUrl/process'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        "problem": """
PNR: AX123
Passenger: Laura Martinez
event_type: delay
delay_minutes: 240
"""
      }),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Error HTTP ${response.statusCode}: ${response.body}');
    }

    return AxiomResponse.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  /// GET ALL RULES
  Future<List<RuleModel>> getRules() async {
    final response = await http.get(Uri.parse('$baseUrl/rules'));

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Error HTTP ${response.statusCode}: ${response.body}');
    }

    final payload = jsonDecode(response.body) as List<dynamic>;

    return payload
        .map((item) => RuleModel.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// CREATE RULE
  Future<RuleModel> addRule(RuleDraft rule) async {
    final response = await http.post(
      Uri.parse('$baseUrl/rules'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(rule.toJson()),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Error HTTP ${response.statusCode}: ${response.body}');
    }

    return RuleModel.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  /// UPDATE RULE
  Future<RuleModel> updateRule(int ruleId, RuleDraft rule) async {
    final response = await http.put(
      Uri.parse('$baseUrl/rules/$ruleId'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(rule.toJson()),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Error HTTP ${response.statusCode}: ${response.body}');
    }

    return RuleModel.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  /// DELETE RULE
  Future<void> deleteRule(int ruleId) async {
    final response = await http.delete(Uri.parse('$baseUrl/rules/$ruleId'));

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Error HTTP ${response.statusCode}: ${response.body}');
    }
  }

  /// GET METRICS
  Future<MetricsModel> getMetrics() async {
    final response = await http.get(Uri.parse('$baseUrl/metrics'));

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Error HTTP ${response.statusCode}: ${response.body}');
    }

    return MetricsModel.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }
}