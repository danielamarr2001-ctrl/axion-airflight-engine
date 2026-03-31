"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Search, BookOpen, BarChart3 } from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Processor", href: "/processor", icon: Search },
  { name: "Rules", href: "/rules", icon: BookOpen },
  { name: "Metrics", href: "/metrics", icon: BarChart3 },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-sidebar-border bg-sidebar">
      <div className="flex h-16 items-center px-6">
        <span className="text-xl font-bold tracking-wide text-sidebar-primary">
          AXIOM
        </span>
        <span className="ml-2 text-xs text-muted-foreground">AirFlight Engine</span>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
              pathname === item.href || pathname.startsWith(item.href + "/")
                ? "bg-sidebar-accent text-sidebar-primary font-medium"
                : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            )}
          >
            <item.icon className="h-4 w-4" />
            {item.name}
          </Link>
        ))}
      </nav>
      <div className="border-t border-sidebar-border p-4">
        <p className="text-xs text-muted-foreground">
          Decision Intelligence Platform
        </p>
      </div>
    </aside>
  );
}
