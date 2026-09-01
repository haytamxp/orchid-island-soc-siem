import React, { useState } from 'react';

import {
  ShieldAlert,
  User,
  Lock,
  Eye,
  EyeOff,
  RefreshCw,
  KeyRound,
} from 'lucide-react';

import { API_BASE_URL } from '../config';
import { saveAuthSession } from '../services/auth';

interface AdminLoginProps {
  onLoginSuccess: () => void;
}

export const AdminLogin: React.FC<
  AdminLoginProps
> = ({ onLoginSuccess }) => {
  const [operatorId, setOperatorId] =
    useState('');

  const [password, setPassword] =
    useState('');

  const [mfaToken, setMfaToken] =
    useState('');

  const [showPassword, setShowPassword] =
    useState(false);

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  const [errorMessage, setErrorMessage] =
    useState('');

  const handleSubmit = async (
    event: React.FormEvent,
  ) => {
    event.preventDefault();
    setErrorMessage('');

    if (
      !operatorId.trim() ||
      !password.trim() ||
      !mfaToken.trim()
    ) {
      setErrorMessage(
        'Veuillez remplir tous les champs de sécurité.',
      );
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/auth/login`,
        {
          method: 'POST',
          headers: {
            'Content-Type':
              'application/json',
            Accept: 'application/json',
          },
          body: JSON.stringify({
            username:
              operatorId.trim(),
            password: password.trim(),
            mfa_token:
              mfaToken.trim(),
          }),
        },
      );

      const data = await response.json();

      if (
        response.ok &&
        data.status === 'authenticated'
      ) {
        saveAuthSession(data);
        onLoginSuccess();
        return;
      }

      setErrorMessage(
        data.error ||
          "ÉCHEC D'AUTHENTIFICATION : identifiants ou code MFA invalides.",
      );
    } catch (error) {
      console.error(
        '[AUTH] Backend authentication failed:',
        error,
      );

      setErrorMessage(
        'Impossible de joindre le serveur d’authentification.',
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      style={{
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
          radial-gradient(
            circle at 50% 50%,
            rgba(6, 182, 212, 0.08) 0%,
            transparent 60%
          ),
          radial-gradient(
            circle at 20% 80%,
            rgba(139, 92, 246, 0.05) 0%,
            transparent 40%
          )
        `,
        fontFamily: 'var(--font-sans)',
        zIndex: 9999,
        padding: '20px',
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '420px',
          padding: '32px 28px',
          borderRadius: '16px',
          border:
            '1px solid rgba(6,182,212,0.2)',
          boxShadow:
            '0 20px 50px rgba(0,0,0,0.6)',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexDirection:
              'column',
            alignItems: 'center',
          }}
        >
          <div
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              display: 'flex',
              alignItems:
                'center',
              justifyContent:
                'center',
              background:
                'rgba(6,182,212,0.1)',
              border:
                '1px solid rgba(6,182,212,0.3)',
              color: 'var(--cyan)',
              marginBottom: '20px',
            }}
          >
            <ShieldAlert size={30} />
          </div>

          <h2
            style={{
              fontSize: '1.4rem',
              fontWeight: 700,
              textAlign:
                'center',
              margin: 0,
            }}
          >
            ADMIN PORTAL ACCESS
          </h2>

          <p
            style={{
              fontSize: '0.72rem',
              color:
                'var(--text-secondary)',
              textAlign:
                'center',
              margin:
                '5px 0 24px',
            }}
          >
            ORCHID ISLAND SOC
            SECURE TERMINAL
          </p>

          {errorMessage && (
            <div
              style={{
                width: '100%',
                boxSizing:
                  'border-box',
                padding:
                  '10px 12px',
                marginBottom:
                  '16px',
                borderRadius:
                  '8px',
                background:
                  'rgba(239,68,68,0.1)',
                border:
                  '1px solid rgba(239,68,68,0.3)',
                color:
                  'var(--red)',
                fontSize:
                  '0.75rem',
                textAlign:
                  'center',
              }}
            >
              {errorMessage}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            autoComplete="off"
            style={{
              width: '100%',
              display: 'flex',
              flexDirection:
                'column',
              gap: '16px',
            }}
          >
            <label
              style={{
                display:
                  'flex',
                flexDirection:
                  'column',
                gap: '6px',
              }}
            >
              <span
                style={{
                  fontSize:
                    '0.7rem',
                  fontWeight: 600,
                  color:
                    'var(--text-secondary)',
                }}
              >
                OPERATOR ID
              </span>

              <div
                style={{
                  position:
                    'relative',
                }}
              >
                <User
                  size={16}
                  style={{
                    position:
                      'absolute',
                    left: '12px',
                    top: '50%',
                    transform:
                      'translateY(-50%)',
                    color:
                      'var(--text-muted)',
                  }}
                />

                <input
                  type="text"
                  autoComplete="username"
                  value={operatorId}
                  disabled={
                    isSubmitting
                  }
                  onChange={(e) =>
                    setOperatorId(
                      e.target.value,
                    )
                  }
                  placeholder="admin"
                  style={{
                    width: '100%',
                    boxSizing:
                      'border-box',
                    background:
                      'rgba(15,23,42,0.6)',
                    border:
                      '1px solid var(--border-primary)',
                    borderRadius:
                      '8px',
                    padding:
                      '10px 12px 10px 38px',
                    color: '#fff',
                    outline:
                      'none',
                  }}
                />
              </div>
            </label>

            <label
              style={{
                display:
                  'flex',
                flexDirection:
                  'column',
                gap: '6px',
              }}
            >
              <span
                style={{
                  fontSize:
                    '0.7rem',
                  fontWeight: 600,
                  color:
                    'var(--text-secondary)',
                }}
              >
                ACCESS PASSWORD
              </span>

              <div
                style={{
                  position:
                    'relative',
                }}
              >
                <Lock
                  size={16}
                  style={{
                    position:
                      'absolute',
                    left: '12px',
                    top: '50%',
                    transform:
                      'translateY(-50%)',
                    color:
                      'var(--text-muted)',
                  }}
                />

                <input
                  type={
                    showPassword
                      ? 'text'
                      : 'password'
                  }
                  autoComplete="current-password"
                  value={password}
                  disabled={
                    isSubmitting
                  }
                  onChange={(e) =>
                    setPassword(
                      e.target.value,
                    )
                  }
                  placeholder="••••••••"
                  style={{
                    width: '100%',
                    boxSizing:
                      'border-box',
                    background:
                      'rgba(15,23,42,0.6)',
                    border:
                      '1px solid var(--border-primary)',
                    borderRadius:
                      '8px',
                    padding:
                      '10px 42px 10px 38px',
                    color: '#fff',
                    outline:
                      'none',
                  }}
                />

                <button
                  type="button"
                  disabled={
                    isSubmitting
                  }
                  onClick={() =>
                    setShowPassword(
                      (value) =>
                        !value,
                    )
                  }
                  style={{
                    position:
                      'absolute',
                    right: '10px',
                    top: '50%',
                    transform:
                      'translateY(-50%)',
                    background:
                      'none',
                    border: 'none',
                    color:
                      'var(--text-muted)',
                    cursor:
                      'pointer',
                  }}
                >
                  {showPassword ? (
                    <EyeOff
                      size={16}
                    />
                  ) : (
                    <Eye size={16} />
                  )}
                </button>
              </div>
            </label>

            <label
              style={{
                display:
                  'flex',
                flexDirection:
                  'column',
                gap: '6px',
              }}
            >
              <span
                style={{
                  fontSize:
                    '0.7rem',
                  fontWeight: 600,
                  color:
                    'var(--text-secondary)',
                }}
              >
                MFA TOKEN
              </span>

              <div
                style={{
                  position:
                    'relative',
                }}
              >
                <KeyRound
                  size={16}
                  style={{
                    position:
                      'absolute',
                    left: '12px',
                    top: '50%',
                    transform:
                      'translateY(-50%)',
                    color:
                      'var(--text-muted)',
                  }}
                />

                <input
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  value={mfaToken}
                  disabled={
                    isSubmitting
                  }
                  onChange={(e) =>
                    setMfaToken(
                      e.target.value
                        .replace(
                          /\D/g,
                          '',
                        ),
                    )
                  }
                  placeholder="000000"
                  style={{
                    width: '100%',
                    boxSizing:
                      'border-box',
                    background:
                      'rgba(15,23,42,0.6)',
                    border:
                      '1px solid var(--border-primary)',
                    borderRadius:
                      '8px',
                    padding:
                      '10px 12px 10px 38px',
                    color: '#fff',
                    fontSize:
                      '1.1rem',
                    fontFamily:
                      'var(--font-mono)',
                    letterSpacing:
                      '0.35em',
                    outline:
                      'none',
                  }}
                />
              </div>
            </label>

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-primary"
              style={{
                width: '100%',
                height: '44px',
                justifyContent:
                  'center',
                display: 'flex',
                alignItems:
                  'center',
                gap: '8px',
                marginTop: '6px',
              }}
            >
              {isSubmitting ? (
                <>
                  <RefreshCw
                    size={15}
                    className="animate-spin"
                  />
                  AUTHENTICATING...
                </>
              ) : (
                'SIGN IN TO SOC NODE'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
