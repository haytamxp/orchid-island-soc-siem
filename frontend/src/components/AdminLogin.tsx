import React, { useState } from 'react';
import { ShieldAlert, User, Lock, Eye, EyeOff, RefreshCw, KeyRound } from 'lucide-react';

import { BACKEND_URL } from '../config';

interface AdminLoginProps {
  onLoginSuccess: () => void;
}

export const AdminLogin: React.FC<AdminLoginProps> = ({ onLoginSuccess }) => {
  const [operatorId, setOperatorId] = useState('');
  const [password, setPassword] = useState('');
  const [mfaToken, setMfaToken] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  // Submission & Validation States
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    
    // Validate inputs locally first
    if (!operatorId.trim() || !password.trim() || !mfaToken.trim()) {
      setErrorMessage("Veuillez remplir tous les champs de sécurité.");
      return;
    }

    setIsSubmitting(true);

    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: operatorId.trim(),
          password: password.trim(),
          mfa_token: mfaToken.trim()
        })
      });

      const data = await res.json();

      if (res.ok && data.status === 'authenticated') {
        localStorage.setItem('siem_session', data.session_token || 'authenticated_admin_token_active');
        setIsSubmitting(false);
        onLoginSuccess();
      } else {
        setIsSubmitting(false);
        setErrorMessage(data.error || "ÉCHEC D'AUTHENTIFICATION : Identifiants ou code MFA invalides.");
      }
    } catch (err) {
      console.warn("Backend auth failed, checking credentials:", err);
      // Fallback check if backend unreachable
      if (operatorId.trim() === 'admin' && password === 'admin123' && mfaToken.trim() === '123456') {
        localStorage.setItem('siem_session', 'authenticated_admin_token_active');
        setIsSubmitting(false);
        onLoginSuccess();
      } else {
        setIsSubmitting(false);
        setErrorMessage("ÉCHEC D'AUTHENTIFICATION : Identifiants ou code MFA invalides.");
      }
    }
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      width: '100vw',
      position: 'fixed',
      top: 0,
      left: 0,
      background: '#070a13',
      backgroundImage: `
        radial-gradient(circle at 50% 50%, rgba(6, 182, 212, 0.08) 0%, transparent 60%),
        radial-gradient(circle at 20% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 40%),
        linear-gradient(rgba(255, 255, 255, 0.003) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.003) 1px, transparent 1px)
      `,
      backgroundSize: '100% 100%, 100% 100%, 32px 32px, 32px 32px',
      fontFamily: 'var(--font-sans)',
      zIndex: 9999,
      padding: '20px'
    }}>
      
      {/* Centered Glassmorphism Card */}
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '420px',
        padding: '32px 28px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(6, 182, 212, 0.05)',
        border: '1px solid rgba(6, 182, 212, 0.2)',
        borderRadius: '16px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        
        {/* Pulsing scanning bar when submitting */}
        {isSubmitting && <div className="scanning-line" />}

        {/* Pulsing Security Shield Icon */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          background: 'rgba(6, 182, 212, 0.1)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          color: 'var(--cyan)',
          marginBottom: '20px',
          boxShadow: '0 0 15px rgba(6, 182, 212, 0.2)'
        }}>
          <ShieldAlert size={32} className="pulse-red" style={{ width: '28px', height: '28px' }} />
        </div>

        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, textAlign: 'center', marginBottom: '4px', letterSpacing: '0.5px' }}>
          ADMIN PORTAL ACCESS
        </h2>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textAlign: 'center', marginBottom: '24px' }}>
          SOC-AI ENCRYPTED TERMINAL NODE
        </p>

        {/* Error alert banner */}
        {errorMessage && (
          <div style={{
            width: '100%',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            padding: '10px 14px',
            color: 'var(--red)',
            fontSize: '0.8rem',
            fontWeight: 600,
            marginBottom: '20px',
            textAlign: 'center',
            boxShadow: '0 0 10px rgba(239, 68, 68, 0.15)'
          }}>
            {errorMessage}
          </div>
        )}

        {/* Credentials Form */}
        <form onSubmit={handleSubmit} autoComplete="off" style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '18px' }}>
          
          {/* Operator ID Field */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>OPERATOR ID</label>
            <div style={{ position: 'relative' }}>
              <User size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                autoComplete="username"
                disabled={isSubmitting}
                value={operatorId}
                onChange={(e) => setOperatorId(e.target.value)}
                placeholder="e.g. admin"
                className="glow-border-cyan"
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '8px',
                  padding: '10px 12px 10px 38px',
                  color: '#ffffff',
                  fontSize: '0.85rem',
                  outline: 'none',
                  transition: 'var(--transition-smooth)'
                }}
              />
            </div>
          </div>

          {/* Access Password Field */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>ACCESS PASSWORD</label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                disabled={isSubmitting}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="glow-border-cyan"
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '8px',
                  padding: '10px 42px 10px 38px',
                  color: '#ffffff',
                  fontSize: '0.85rem',
                  outline: 'none',
                  transition: 'var(--transition-smooth)'
                }}
              />
              <button
                type="button"
                disabled={isSubmitting}
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* MFA TOTP Token Field */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>MFA TOKEN</label>
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>(Default: 123456)</span>
            </div>
            <div style={{ position: 'relative' }}>
              <KeyRound size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                autoComplete="one-time-code"
                disabled={isSubmitting}
                maxLength={6}
                value={mfaToken}
                onChange={(e) => setMfaToken(e.target.value.replace(/\D/g, ''))}
                placeholder="0 0 0 0 0 0"
                className="glow-border-cyan"
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '8px',
                  padding: '10px 12px 10px 38px',
                  color: '#ffffff',
                  fontSize: '1.2rem',
                  fontWeight: 700,
                  fontFamily: 'var(--font-mono)',
                  letterSpacing: '0.5em',
                  outline: 'none',
                  transition: 'var(--transition-smooth)'
                }}
              />
            </div>
          </div>

          {/* Submit Action */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary"
            style={{
              width: '100%',
              height: '44px',
              justifyContent: 'center',
              fontSize: '0.9rem',
              marginTop: '10px',
              letterSpacing: '0.5px'
            }}
          >
            {isSubmitting ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', fontWeight: 700 }}>
                <RefreshCw size={14} className="animate-spin" /> AUTHORIZING SECURE SESSION...
              </span>
            ) : (
              <span>SIGN IN TO SOC NODE</span>
            )}
          </button>

        </form>

      </div>
    </div>
  );
};
