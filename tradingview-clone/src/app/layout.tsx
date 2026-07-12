import type { Metadata } from "next";
import "./globals.css";
import AuthProvider from "@/components/AuthProvider";

export const metadata: Metadata = {
  title: "TradingView – Tüm Piyasaları Takip Edin",
  description:
    "En iyi işlemler önce araştırma, sonra kararlılık gerektirir. Geleceği kendi ellerine alan 100 milyon yatırımcıya katılın.",
  icons: {
    icon: "https://tr.tradingview.com/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr" className="dark h-full antialiased">
      <body className="min-h-full flex flex-col">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
