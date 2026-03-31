import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'models/rule_platform_models.dart';
import 'services/axiom_api.dart';
import 'widgets/section_card.dart';

class RulesPage extends StatefulWidget {
  const RulesPage({super.key});

  @override
  State<RulesPage> createState() => _RulesPageState();
}

class _RulesPageState extends State<RulesPage> {
  static const _operators = ['=', '>', '<', '>=', '<=', 'missing'];

  final _api = const AxiomApiService();

  List<RuleModel> _rules = const [];
  bool _loading = true;
  bool _saving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadRules();
  }

  Future<void> _loadRules() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final rules = await _api.getRules();
      if (!mounted) {
        return;
      }
      setState(() => _rules = rules);
    } catch (err) {
      if (!mounted) {
        return;
      }
      setState(() => _error = err.toString());
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Future<void> _createRule() async {
    final draft = await _openRuleEditor();
    if (draft == null) {
      return;
    }

    setState(() => _saving = true);
    try {
      await _api.addRule(draft);
      await _loadRules();
    } catch (err) {
      if (!mounted) {
        return;
      }
      setState(() => _error = err.toString());
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }

  Future<void> _editRule(RuleModel rule) async {
    final draft = await _openRuleEditor(existing: rule);
    if (draft == null) {
      return;
    }

    setState(() => _saving = true);
    try {
      await _api.updateRule(rule.ruleId, draft);
      await _loadRules();
    } catch (err) {
      if (!mounted) {
        return;
      }
      setState(() => _error = err.toString());
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }

  Future<void> _deleteRule(RuleModel rule) async {
    final shouldDelete = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF0F1822),
          title: const Text('Delete rule'),
          content: Text(
              'Delete rule #${rule.ruleId}? This action cannot be undone.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(true),
              style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFFDC5F5F)),
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );

    if (shouldDelete != true) {
      return;
    }

    setState(() => _saving = true);
    try {
      await _api.deleteRule(rule.ruleId);
      await _loadRules();
    } catch (err) {
      if (!mounted) {
        return;
      }
      setState(() => _error = err.toString());
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }

  Future<RuleDraft?> _openRuleEditor({RuleModel? existing}) async {
    final fieldController = TextEditingController(text: existing?.field ?? '');
    final valueController = TextEditingController(text: existing?.value ?? '');
    final actionController =
        TextEditingController(text: existing?.action ?? '');
    final priorityController = TextEditingController(
      text: (existing?.priority ?? 1).toString(),
    );
    var selectedOperator = existing?.operator ?? '=';

    final result = await showDialog<RuleDraft>(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              backgroundColor: const Color(0xFF0F1822),
              title: Text(existing == null
                  ? 'Add rule'
                  : 'Edit rule #${existing.ruleId}'),
              content: SizedBox(
                width: 420,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextField(
                      controller: fieldController,
                      decoration: const InputDecoration(labelText: 'Field'),
                    ),
                    const SizedBox(height: 10),
                    DropdownButtonFormField<String>(
                      initialValue: selectedOperator,
                      decoration: const InputDecoration(labelText: 'Operator'),
                      items: _operators
                          .map((item) =>
                              DropdownMenuItem(value: item, child: Text(item)))
                          .toList(),
                      onChanged: (value) {
                        if (value == null) {
                          return;
                        }
                        setDialogState(() => selectedOperator = value);
                      },
                    ),
                    const SizedBox(height: 10),
                    TextField(
                      controller: valueController,
                      enabled: selectedOperator != 'missing',
                      decoration: const InputDecoration(labelText: 'Value'),
                    ),
                    const SizedBox(height: 10),
                    TextField(
                      controller: actionController,
                      decoration: const InputDecoration(labelText: 'Action'),
                    ),
                    const SizedBox(height: 10),
                    TextField(
                      controller: priorityController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Priority'),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () {
                    final field = fieldController.text.trim();
                    final action = actionController.text.trim();
                    final value = selectedOperator == 'missing'
                        ? ''
                        : valueController.text.trim();
                    final priority =
                        int.tryParse(priorityController.text.trim()) ?? 1;

                    if (field.isEmpty || action.isEmpty || priority < 1) {
                      return;
                    }

                    Navigator.of(context).pop(
                      RuleDraft(
                        field: field,
                        operator: selectedOperator,
                        value: value,
                        action: action,
                        priority: priority,
                      ),
                    );
                  },
                  child: const Text('Save'),
                ),
              ],
            );
          },
        );
      },
    );

    fieldController.dispose();
    valueController.dispose();
    actionController.dispose();
    priorityController.dispose();

    return result;
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = GoogleFonts.spaceGroteskTextTheme(
      Theme.of(context).textTheme,
    ).apply(bodyColor: Colors.white, displayColor: Colors.white);

    return Theme(
      data: Theme.of(context).copyWith(textTheme: textTheme),
      child: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF071017), Color(0xFF0E1923), Color(0xFF05161C)],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 18),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 1220),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Wrap(
                      alignment: WrapAlignment.spaceBetween,
                      spacing: 12,
                      runSpacing: 12,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Rule Platform',
                              style: textTheme.displaySmall?.copyWith(
                                fontWeight: FontWeight.w800,
                                color: const Color(0xFF57E6C2),
                              ),
                            ),
                            Text(
                              'Excel-style table rule management',
                              style: textTheme.titleMedium?.copyWith(
                                color: const Color(0xFFA1B2C5),
                              ),
                            ),
                          ],
                        ),
                        Wrap(
                          spacing: 10,
                          children: [
                            OutlinedButton.icon(
                              onPressed: _loading ? null : _loadRules,
                              icon: const Icon(Icons.refresh),
                              label: const Text('Refresh'),
                            ),
                            FilledButton.icon(
                              onPressed:
                                  (_loading || _saving) ? null : _createRule,
                              style: FilledButton.styleFrom(
                                backgroundColor: const Color(0xFF1DCEA6),
                                foregroundColor: const Color(0xFF02110D),
                              ),
                              icon: const Icon(Icons.add),
                              label: const Text('Add Rule'),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    SectionCard(
                      title: 'Rule Editor',
                      child: _loading
                          ? const Padding(
                              padding: EdgeInsets.symmetric(vertical: 24),
                              child: Center(child: CircularProgressIndicator()),
                            )
                          : _buildRuleTable(),
                    ),
                    if (_error != null) ...[
                      const SizedBox(height: 12),
                      Text(
                        _error!,
                        style: const TextStyle(color: Color(0xFFFF7A7A)),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRuleTable() {
    if (_rules.isEmpty) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 20),
        child: Text('No rules found. Add the first rule.'),
      );
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        headingTextStyle: const TextStyle(
          color: Color(0xFF7CCDEB),
          fontWeight: FontWeight.w700,
        ),
        columns: const [
          DataColumn(label: Text('ID')),
          DataColumn(label: Text('Field')),
          DataColumn(label: Text('Operator')),
          DataColumn(label: Text('Value')),
          DataColumn(label: Text('Action')),
          DataColumn(label: Text('Priority')),
          DataColumn(label: Text('Controls')),
        ],
        rows: _rules
            .map(
              (rule) => DataRow(
                cells: [
                  DataCell(Text(rule.ruleId.toString())),
                  DataCell(Text(rule.field)),
                  DataCell(Text(rule.operator)),
                  DataCell(Text(rule.value.isEmpty ? '-' : rule.value)),
                  DataCell(Text(rule.action)),
                  DataCell(Text(rule.priority.toString())),
                  DataCell(
                    Wrap(
                      spacing: 8,
                      children: [
                        IconButton(
                          tooltip: 'Edit',
                          onPressed: _saving ? null : () => _editRule(rule),
                          icon: const Icon(Icons.edit_outlined),
                        ),
                        IconButton(
                          tooltip: 'Delete',
                          onPressed: _saving ? null : () => _deleteRule(rule),
                          icon: const Icon(
                            Icons.delete_outline,
                            color: Color(0xFFFF7A7A),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            )
            .toList(),
      ),
    );
  }
}
