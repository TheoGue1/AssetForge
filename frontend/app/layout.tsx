import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "StockFlow",
  description: "Local Adobe Stock generation studio",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-zinc-950">{children}</body>
    </html>
  );
}
