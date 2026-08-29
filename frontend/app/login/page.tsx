"use client";

import { FormEvent, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

import { api, saveToken } from '../../lib/api';

export default function LoginPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [mode, setMode] = useState<'login' | 'register'>('login');
    const [email, setEmail] = useState('demo@tripwise.app');
    const [password, setPassword] = useState('TripWise@123');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setMode(searchParams.get('mode') === 'register' ? 'register' : 'login');
    }, [searchParams]);

    function isValidEmail(value: string) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value.trim());
    }

    async function submit(event: FormEvent) {
        event.preventDefault();
        setError('');
        if (!isValidEmail(email)) {
            setError('Please enter a valid email address.');
            return;
        }
        setLoading(true);
        try {
            const data = await api(mode === 'login' ? '/auth/login' : '/auth/register', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            });
            saveToken(data.token);
            router.replace('/planner');
        } catch (requestError) {
            setError(requestError instanceof Error ? requestError.message : 'Authentication failed.');
        } finally {
            setLoading(false);
        }
    }

    function switchMode(nextMode: 'login' | 'register') {
        setMode(nextMode);
        setError('');
        router.replace(`/login?mode=${nextMode}`);
    }

    return (
        <main className="auth-page">
            <div className="card auth-card">
                <p className="eyebrow">TRIPWISE ACCOUNT</p>
                <h1>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h1>
                <p>{mode === 'login' ? 'Sign in to access your saved trips and planner.' : 'Create your account to keep your trips private and saved.'}</p>

                <div className="auth-switcher">
                    <button type="button" className={mode === 'login' ? 'auth-switch active' : 'auth-switch'} onClick={() => switchMode('login')}>Sign in</button>
                    <button type="button" className={mode === 'register' ? 'auth-switch active' : 'auth-switch'} onClick={() => switchMode('register')}>Create account</button>
                </div>

                <form className="form" onSubmit={submit}>
                    <label>
                        Email
                        <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" inputMode="email" />
                    </label>
                    <label>
                        Password
                        <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={6} required autoComplete={mode === 'login' ? 'current-password' : 'new-password'} />
                    </label>
                    {error && <p className="error">{error}</p>}
                    <button className="button" disabled={loading} type="submit">{loading ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}</button>
                </form>

                {mode === 'login' && (
                    <div className="demo-box">
                        <strong>Demo credentials</strong>
                        <span>Email: demo@tripwise.app</span>
                        <span>Password: TripWise@123</span>
                    </div>
                )}
            </div>
        </main>
    );
}
