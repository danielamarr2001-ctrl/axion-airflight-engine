import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'models/axiom_response.dart';
import 'services/axiom_api.dart';
import 'widgets/section_card.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  final _problemController = TextEditingController(
    text:
        'Mi vuelo con Iberia desde Bogota a Madrid IB156 fue cancelado por fallas tecnicas.',
  );

  final _api = const AxiomApiService();

  AxiomResponse? _response;
  String? _error;
  bool _loading = false;

  @override
  void dispose() {
    _problemController.dispose();
    super.dispose();
  }

  Future<void> _process() async {
    final text = _problemController.text.trim();
    if (text.isEmpty) {
      setState(() => _error = 'Debes ingresar una solicitud del cliente.');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final result = await _api.processProblem(text);
      if (!mounted) {
        return;
      }
      setState(() => _response = result);
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
                    _buildHeader(textTheme),
                    const SizedBox(height: 24),
                    _buildInput(textTheme),
                    const SizedBox(height: 18),
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 350),
                      switchInCurve: Curves.easeOutCubic,
                      switchOutCurve: Curves.easeInCubic,
                      child: _response == null
                          ? const SizedBox.shrink()
                          : Column(
                              key: ValueKey(_response.hashCode),
                              children: [
                                _buildOverview(_response!, textTheme),
                                const SizedBox(height: 14),
                                _buildCaseDetails(_response!, textTheme),
                              ],
                            ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(TextTheme textTheme) {
    return Wrap(
      alignment: WrapAlignment.spaceBetween,
      runSpacing: 10,
      spacing: 10,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'AXIOM Processor',
              style: textTheme.displaySmall?.copyWith(
                fontWeight: FontWeight.w800,
                color: const Color(0xFF57E6C2),
              ),
            ),
            const SizedBox(height: 2),
            Text(
              'Input -> Validation -> Classification -> Rules -> Options -> Action',
              style: textTheme.titleMedium?.copyWith(
                color: const Color(0xFFA1B2C5),
              ),
            ),
          ],
        ),
        if (_response != null)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFF153040),
              borderRadius: BorderRadius.circular(999),
              border: Border.all(color: const Color(0xFF2E627F)),
            ),
            child: Text(
              'Rule Engine Mode: ${_response!.engineMode.toUpperCase()}',
              style: textTheme.bodySmall?.copyWith(
                color: const Color(0xFF8AC2D9),
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildInput(TextTheme textTheme) {
    return SectionCard(
      title: 'Customer Request',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextField(
            controller: _problemController,
            minLines: 4,
            maxLines: 6,
            style: textTheme.bodyLarge,
            decoration: InputDecoration(
              hintText:
                  'Mi vuelo con Iberia desde Bogota a Madrid fue cancelado...',
              filled: true,
              fillColor: const Color(0xFF0A1420),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: const BorderSide(color: Color(0xFF244459)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: const BorderSide(color: Color(0xFF244459)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: const BorderSide(
                  color: Color(0xFF46E5C0),
                  width: 1.2,
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _loading ? null : _process,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1DCEA6),
              foregroundColor: const Color(0xFF02110D),
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            icon: _loading
                ? const SizedBox(
                    width: 15,
                    height: 15,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.play_arrow_rounded),
            label: const Text('Procesar solicitud'),
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(_error!, style: const TextStyle(color: Color(0xFFFF7373))),
          ],
        ],
      ),
    );
  }

  Widget _buildOverview(AxiomResponse response, TextTheme textTheme) {
    final approved = response.status.toUpperCase() == 'APROBADO';

    return SectionCard(
      title: 'AXIOM - Decision Result',
      accent: approved ? const Color(0xFF25D7B0) : const Color(0xFFFF6666),
      child: Wrap(
        spacing: 20,
        runSpacing: 14,
        children: [
          _metric(
            label: 'Case status',
            value: response.status,
            valueColor:
                approved ? const Color(0xFF36E9C0) : const Color(0xFFFF8C8C),
          ),
          _metric(
            label: 'Analysis time',
            value: '${response.analysisTimeMs} ms',
            valueColor: const Color(0xFF8BE9D1),
          ),
          _metric(label: 'Event type', value: response.eventType),
          _metric(label: 'Rule', value: response.ruleApplied),
        ],
      ),
    );
  }

  Widget _buildCaseDetails(AxiomResponse response, TextTheme textTheme) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final splitView = constraints.maxWidth >= 900;

        final validationCard = SectionCard(
          title: 'Validation',
          accent: response.validation.pnr == 'present' &&
                  response.validation.passenger == 'present'
              ? const Color(0xFF34DAB5)
              : const Color(0xFFFF6C6C),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _pair('PNR', response.validation.pnr),
              const SizedBox(height: 10),
              _pair('Passenger', response.validation.passenger),
            ],
          ),
        );

        final originalFlightCard = SectionCard(
          title: 'Original Flight',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _pair('Airline', response.originalFlight.airline),
              const SizedBox(height: 10),
              _pair('Flight', response.originalFlight.flight),
              const SizedBox(height: 10),
              _pair('Route', response.originalFlight.route),
              const SizedBox(height: 10),
              _pair('Date', response.originalFlight.date),
              const SizedBox(height: 10),
              _pair('Status', response.originalFlight.status),
            ],
          ),
        );

        Widget topCards;
        if (splitView) {
          topCards = Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(child: validationCard),
              const SizedBox(width: 12),
              Expanded(child: originalFlightCard),
            ],
          );
        } else {
          topCards = Column(
            children: [
              validationCard,
              const SizedBox(height: 12),
              originalFlightCard,
            ],
          );
        }

        return Column(
          children: [
            topCards,
            const SizedBox(height: 12),
            SectionCard(
              title: 'Justification',
              accent: const Color(0xFF3ED9B7),
              child: Text(
                response.justification,
                style: textTheme.bodyLarge?.copyWith(
                  color: const Color(0xFFC2CFDB),
                ),
              ),
            ),
            const SizedBox(height: 12),
            SectionCard(
              title: 'Available Options',
              child: response.options.isEmpty
                  ? Text(
                      'No options available. Complete critical data to continue.',
                      style: textTheme.bodyLarge?.copyWith(
                        color: const Color(0xFFFF9A9A),
                      ),
                    )
                  : LayoutBuilder(
                      builder: (context, optionConstraints) {
                        final width = optionConstraints.maxWidth;
                        final cardWidth = width >= 960
                            ? width / 3 - 10
                            : width >= 620
                                ? width / 2 - 8
                                : width;

                        return Wrap(
                          spacing: 12,
                          runSpacing: 12,
                          children: [
                            for (var i = 0; i < response.options.length; i++)
                              SizedBox(
                                width: cardWidth,
                                child: Container(
                                  padding: const EdgeInsets.all(14),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF0B1621),
                                    borderRadius: BorderRadius.circular(14),
                                    border: Border.all(
                                      color: const Color(0xFF27465A),
                                    ),
                                  ),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'OPTION ${i + 1}',
                                        style: textTheme.labelLarge?.copyWith(
                                          color: const Color(0xFF8AB1C8),
                                          letterSpacing: 1.1,
                                        ),
                                      ),
                                      const SizedBox(height: 9),
                                      Text(
                                        response.options[i].flight,
                                        style: textTheme.titleLarge?.copyWith(
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(response.options[i].time),
                                      const SizedBox(height: 6),
                                      Text(
                                        response.options[i].status,
                                        style: textTheme.bodyMedium?.copyWith(
                                          color: response.options[i].status ==
                                                  'disponible'
                                              ? const Color(0xFF4BE5BF)
                                              : const Color(0xFFFF7A7A),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                          ],
                        );
                      },
                    ),
            ),
            const SizedBox(height: 12),
            SectionCard(
              title: 'Required Action',
              accent: const Color(0xFF4DE3C0),
              child: Text(
                response.actionRequired,
                style: textTheme.bodyLarge?.copyWith(
                  color: const Color(0xFFD4DFE7),
                ),
              ),
            ),
            if (response.triggeredRules.isNotEmpty) ...[
              const SizedBox(height: 12),
              SectionCard(
                title: 'Triggered Table Rules',
                accent: const Color(0xFF319CC7),
                child: Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    for (final rule in response.triggeredRules)
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFF112232),
                          borderRadius: BorderRadius.circular(999),
                          border: Border.all(color: const Color(0xFF2A5D7A)),
                        ),
                        child: Text(
                          '#${rule.ruleId} ${rule.field} ${rule.operator} ${rule.value} -> ${rule.action}',
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ],
        );
      },
    );
  }

  Widget _metric({
    required String label,
    required String value,
    Color? valueColor,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(color: Color(0xFF9FB4C8), fontSize: 13),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            color: valueColor ?? Colors.white,
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
      ],
    );
  }

  Widget _pair(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 92,
          child: Text(label, style: const TextStyle(color: Color(0xFF8CA3B8))),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
}
