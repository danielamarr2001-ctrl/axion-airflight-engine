import 'package:flutter/material.dart';

import 'dashboard_page.dart';
import 'metrics_page.dart';
import 'rules_page.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _selectedIndex = 0;

  final _pages = const [
    DashboardPage(),
    RulesPage(),
    MetricsPage(),
  ];

  final _items = const [
    _NavItem(label: 'Processor', icon: Icons.psychology_alt_outlined),
    _NavItem(label: 'Rules', icon: Icons.table_chart_outlined),
    _NavItem(label: 'Metrics', icon: Icons.insights_outlined),
  ];

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isDesktop = constraints.maxWidth >= 980;
        final content = IndexedStack(index: _selectedIndex, children: _pages);

        if (!isDesktop) {
          return Scaffold(
            body: content,
            bottomNavigationBar: NavigationBar(
              selectedIndex: _selectedIndex,
              onDestinationSelected: (index) {
                setState(() => _selectedIndex = index);
              },
              destinations: _items
                  .map(
                    (item) => NavigationDestination(
                      icon: Icon(item.icon),
                      label: item.label,
                    ),
                  )
                  .toList(),
            ),
          );
        }

        return Scaffold(
          body: Row(
            children: [
              Container(
                width: 240,
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [Color(0xFF08131C), Color(0xFF0A1823)],
                  ),
                  border: Border(
                    right: BorderSide(color: Color(0xFF1B2C38)),
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'AXIOM',
                          style: TextStyle(
                            color: Color(0xFF57E6C2),
                            fontSize: 28,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Decision Platform',
                          style: TextStyle(color: Color(0xFF8EA3B5)),
                        ),
                        const SizedBox(height: 24),
                        for (var i = 0; i < _items.length; i++)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: _DesktopNavButton(
                              item: _items[i],
                              selected: i == _selectedIndex,
                              onTap: () => setState(() => _selectedIndex = i),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
              Expanded(child: content),
            ],
          ),
        );
      },
    );
  }
}

class _NavItem {
  final String label;
  final IconData icon;

  const _NavItem({required this.label, required this.icon});
}

class _DesktopNavButton extends StatelessWidget {
  final _NavItem item;
  final bool selected;
  final VoidCallback onTap;

  const _DesktopNavButton({
    required this.item,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: selected ? const Color(0xFF153040) : const Color(0x00000000),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: selected ? const Color(0xFF2A5E7E) : Colors.transparent,
          ),
        ),
        child: Row(
          children: [
            Icon(item.icon,
                color: selected
                    ? const Color(0xFF64E8C5)
                    : const Color(0xFF88A1B4)),
            const SizedBox(width: 10),
            Text(
              item.label,
              style: TextStyle(
                color: selected
                    ? const Color(0xFFDAFFF5)
                    : const Color(0xFF9AB2C4),
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
