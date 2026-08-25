import type { Metadata } from 'next';

import Nav from '../components/Nav';

import './styles.css';

export const metadata: Metadata = {
    title: 'TripWise',
    description:
        'ML-powered travel planning and recommendations.',
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body>
                <Nav />

                {children}
            </body>
        </html>
    );
}