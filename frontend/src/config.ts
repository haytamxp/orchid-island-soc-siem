// Configuration de la connexion réseau avec la VM Ubuntu / Machine hôte
export const BACKEND_IP = (import.meta.env.VITE_BACKEND_IP as string) || window.location.hostname || 'localhost';

export const BACKEND_URL = `http://${BACKEND_IP}:5000`;
export const WEBSOCKET_URL = `ws://${BACKEND_IP}:5000`;

console.log(`[CONFIG] Connexion au backend configurée vers : REST=${BACKEND_URL}, WS=${WEBSOCKET_URL}`);
