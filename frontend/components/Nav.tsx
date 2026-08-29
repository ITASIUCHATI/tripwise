"use client";

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { clearToken, getToken } from '../lib/api';

const links = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/planner', label: 'Planner' },
    { href: '/trips', label: 'Trips' },
];

export default function Nav() {
    const pathname = usePathname();
    const router = useRouter();
    const [authenticated, setAuthenticated] = useState(false);

    useEffect(() => {
        setAuthenticated(Boolean(getToken()));
    }, [pathname]);

    function logout() {
        clearToken();
        setAuthenticated(false);
        router.replace('/login');
    }

    return (
        <nav>
            <Link href="/" className="brand">TripWise</Link>
            <div>
                {authenticated && links.map((link) => (
                    <Link key={link.href} href={link.href} className={pathname === link.href ? 'active' : ''}>
                        {link.label}
                    </Link>
                ))}
                {authenticated ? (
                    <button className="nav-button" type="button" onClick={logout}>Logout</button>
                ) : (
                    <>
                        <Link href="/login?mode=login" className={pathname === '/login' ? 'active' : ''}>Sign in</Link>
                        <Link href="/login?mode=register">Create account</Link>
                    </>
                )}
            </div>
        </nav>
    );
}
