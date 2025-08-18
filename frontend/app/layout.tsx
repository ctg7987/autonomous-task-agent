export const metadata = {
  title: "Autonomous Multi-Tool AI Task Agent",
  description: "MVP UI",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
