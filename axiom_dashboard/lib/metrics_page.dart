import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'models/rule_platform_models.dart';
import 'services/axiom_api.dart';
import 'widgets/section_card.dart';

class MetricsPage extends StatefulWidget {
  const MetricsPage({super.key});

  @override
  State<MetricsPage> createState() => _MetricsPageState();
}

class _MetricsPageState extends State<MetricsPage> {
  final _api = const AxiomApiService();

  MetricsModel? _metrics;
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadMetrics();
  }

  Future<void> _loadMetrics() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final metrics = await _api.getMetrics();
      if (!mounted) {
        return;
      }
      setState(() => _metrics = metrics);
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
                    Wrap(
                      alignment: WrapAlignment.spaceBetween,
                      spacing: 12,
                      runSpacing: 12,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Analytics Dashboard',
                              style: textTheme.displaySmall?.copyWith(
                                fontWeight: FontWeight.w800,
                                color: const Color(0xFF57E6C2),
                              ),
                            ),
                            Text(
                              'Decision engine telemetry and rule impact',
                              style: textTheme.titleMedium?.copyWith(
                                color: const Color(0xFFA1B2C5),
                              ),
                            ),
                          ],
                        ),
                        OutlinedButton.icon(
                          onPressed: _loading ? null : _loadMetrics,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Refresh'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    if (_loading)
                      const Center(
                        child: Padding(
                          padding: EdgeInsets.symmetric(vertical: 24),
                          child: CircularProgressIndicator(),
                        ),
                      )
                    else if (_error != null)
                      Text(
                        _error!,
                        style: const TextStyle(color: Color(0xFFFF7A7A)),
                      )
                    else if (_metrics != null)
                      _buildMetricsView(_metrics!, textTheme),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMetricsView(MetricsModel metrics, TextTheme textTheme) {
    return Column(
      children: [
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            _metricCard(
              title: 'Total Decisions',
              value: metrics.totalRequests.toString(),
              accent: const Color(0xFF4CE4C0),
            ),
            _metricCard(
              title: 'Manual Reviews',
              value: metrics.manualReviews.toString(),
              accent: const Color(0xFFFF7B7B),
            ),
            _metricCard(
              title: 'Avg Processing',
              value: '${metrics.avgProcessingTimeMs.toStringAsFixed(2)} ms',
              accent: const Color(0xFF6ACBFF),
            ),
            _metricCard(
              title: 'Triggered Rules',
              value: metrics.rulesTriggered.length.toString(),
              accent: const Color(0xFF9AD96D),
            ),
          ],
        ),
        const SizedBox(height: 12),
        SectionCard(
          title: 'Decisions per day',
          child: SizedBox(
            height: 260,
            child: _buildDecisionsChart(metrics),
          ),
        ),
        const SizedBox(height: 12),
        LayoutBuilder(
          builder: (context, constraints) {
            final split = constraints.maxWidth >= 980;
            final latencyCard = SectionCard(
              title: 'Processing latency',
              child: SizedBox(height: 250, child: _buildLatencyChart(metrics)),
            );
            final topRulesCard = SectionCard(
              title: 'Top triggered rules',
              child: SizedBox(height: 250, child: _buildTopRulesChart(metrics)),
            );

            if (split) {
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: latencyCard),
                  const SizedBox(width: 12),
                  Expanded(child: topRulesCard),
                ],
              );
            }

            return Column(
              children: [
                latencyCard,
                const SizedBox(height: 12),
                topRulesCard,
              ],
            );
          },
        ),
      ],
    );
  }

  Widget _metricCard({
    required String title,
    required String value,
    required Color accent,
  }) {
    return SizedBox(
      width: 286,
      child: SectionCard(
        title: title,
        accent: accent,
        child: Text(
          value,
          style: TextStyle(
            color: accent,
            fontWeight: FontWeight.w800,
            fontSize: 30,
          ),
        ),
      ),
    );
  }

  Widget _buildDecisionsChart(MetricsModel metrics) {
    if (metrics.decisionsPerDay.isEmpty) {
      return const Center(child: Text('No data yet.'));
    }

    final spots = <BarChartGroupData>[];
    for (var i = 0; i < metrics.decisionsPerDay.length; i++) {
      final item = metrics.decisionsPerDay[i];
      spots.add(
        BarChartGroupData(
          x: i,
          barRods: [
            BarChartRodData(
              toY: item.count.toDouble(),
              color: const Color(0xFF4EDFC0),
              width: 12,
              borderRadius: BorderRadius.circular(3),
            ),
          ],
        ),
      );
    }

    return BarChart(
      BarChartData(
        barGroups: spots,
        gridData: const FlGridData(show: false),
        borderData: FlBorderData(show: false),
        titlesData: FlTitlesData(
          rightTitles:
              const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles:
              const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          leftTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: true, reservedSize: 34),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final index = value.toInt();
                if (index % 3 != 0 || index >= metrics.decisionsPerDay.length) {
                  return const SizedBox.shrink();
                }
                final label = metrics.decisionsPerDay[index].day.substring(5);
                return Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Text(
                    label,
                    style:
                        const TextStyle(fontSize: 11, color: Color(0xFF92A8BA)),
                  ),
                );
              },
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTopRulesChart(MetricsModel metrics) {
    final top = metrics.topTriggeredRules;
    if (top.isEmpty) {
      return const Center(child: Text('No triggered rules yet.'));
    }

    final maxValue =
        top.map((item) => item.count).fold<int>(0, (a, b) => a > b ? a : b);

    return ListView.separated(
      itemCount: top.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final item = top[index];
        final ratio = maxValue == 0 ? 0.0 : item.count / maxValue;

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(item.rule, maxLines: 1, overflow: TextOverflow.ellipsis),
            const SizedBox(height: 4),
            Stack(
              children: [
                Container(
                  height: 10,
                  decoration: BoxDecoration(
                    color: const Color(0xFF1A2A35),
                    borderRadius: BorderRadius.circular(99),
                  ),
                ),
                FractionallySizedBox(
                  widthFactor: ratio,
                  child: Container(
                    height: 10,
                    decoration: BoxDecoration(
                      color: const Color(0xFF73D965),
                      borderRadius: BorderRadius.circular(99),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 2),
            Text(
              '${item.count}',
              style: const TextStyle(color: Color(0xFF8CA3B8), fontSize: 12),
            ),
          ],
        );
      },
    );
  }

  Widget _buildLatencyChart(MetricsModel metrics) {
    if (metrics.latencySeriesMs.isEmpty) {
      return const Center(child: Text('No latency data yet.'));
    }

    final points = <FlSpot>[];
    for (var i = 0; i < metrics.latencySeriesMs.length; i++) {
      points.add(FlSpot(i.toDouble(), metrics.latencySeriesMs[i]));
    }

    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: false),
        borderData: FlBorderData(show: false),
        titlesData: const FlTitlesData(
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        lineBarsData: [
          LineChartBarData(
            spots: points,
            isCurved: true,
            color: const Color(0xFF67C9FF),
            barWidth: 3,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
              color: const Color(0xFF67C9FF).withValues(alpha: 0.2),
            ),
          ),
        ],
      ),
    );
  }
}
