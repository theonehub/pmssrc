import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

// =============================================================================
// FIREBASE CONFIGURATION
// =============================================================================

const firebaseConfig = {
  // Replace with your Firebase config
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "demo-api-key",
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "tax-calculator-demo.firebaseapp.com",
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || "tax-calculator-demo",
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "tax-calculator-demo.appspot.com",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || "123456789",
  appId: process.env.REACT_APP_FIREBASE_APP_ID || "1:123456789:web:abcdef123456"
};

// =============================================================================
// FIREBASE INITIALIZATION
// =============================================================================

const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

export default app; 