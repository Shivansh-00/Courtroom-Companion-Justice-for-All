export const metadata = {
  title: 'AI Courtroom Companion',
  description: 'Justice for All',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'Inter, Arial, sans-serif', margin: 0, background: '#0b1220', color: '#f3f4f6' }}>
        {children}
      </body>
    </html>
  );
}
