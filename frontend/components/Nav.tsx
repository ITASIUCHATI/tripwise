'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const links = [
    {
        href: '/dashboard',
        label: 'Dashboard',
    },
    {
        href: '/planner',
        label: 'Planner',
    },
    {
        href: '/trips',
        label: 'Trips',
    },
];

export default function Nav() {
    const pathname = usePathname();

    return (
        <nav>
            <Link
                href="/"
                className="brand"
            >
                TripWise
            </Link>

            <div>
                {links.map((link) => (
                    <Link
                        key={link.href}
                        href={link.href}
                        className={
                            pathname === link.href
                                ? 'active'
                                : ''
                        }
                    >
                        {link.label}
                    </Link>
                ))}
            </div>
        </nav>
    );
}