import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { 
  User,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  updateProfile,
  sendPasswordResetEmail,
  onAuthStateChanged
} from 'firebase/auth';
import { 
  doc, 
  setDoc, 
  getDoc, 
  updateDoc
} from 'firebase/firestore';

import { auth, db } from '../../services/firebase';

// =============================================================================
// INTERFACES & TYPES
// =============================================================================

interface UserProfile {
  uid: string;
  email: string;
  displayName: string;
  phoneNumber?: string;
  panNumber?: string;
  dateOfBirth?: string;
  profession?: string;
  annualIncome?: number;
  preferredTaxRegime?: 'old' | 'new';
  createdAt: string;
  updatedAt: string;
}

interface TaxData {
  incomeSources: any[];
  deductions: any[];
  calculations: any[];
  records: any[];
  lastSyncAt: string;
}

interface AuthContextType {
  user: User | null;
  userProfile: UserProfile | null;
  taxData: TaxData | null;
  loading: boolean;
  error: string | null;
  
  // Auth methods
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, profile: Partial<UserProfile>) => Promise<void>;
  logout: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  
  // Profile methods
  updateUserProfile: (updates: Partial<UserProfile>) => Promise<void>;
  
  // Data methods
  syncTaxData: (data: Partial<TaxData>) => Promise<void>;
  loadTaxData: () => Promise<TaxData | null>;
}

// =============================================================================
// CONTEXT CREATION
// =============================================================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// =============================================================================
// AUTH PROVIDER COMPONENT
// =============================================================================

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [taxData, setTaxData] = useState<TaxData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // =============================================================================
  // FIREBASE AUTH STATE LISTENER
  // =============================================================================

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setUser(user);
        await loadUserProfile(user.uid);
        await loadUserTaxData(user.uid);
      } else {
        setUser(null);
        setUserProfile(null);
        setTaxData(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // =============================================================================
  // HELPER FUNCTIONS
  // =============================================================================

  const clearError = () => setError(null);

  const handleError = (error: any) => {
    console.error('Auth error:', error);
    setError(error.message || 'An unexpected error occurred');
  };

  const loadUserProfile = async (uid: string) => {
    try {
      const docRef = doc(db, 'userProfiles', uid);
      const docSnap = await getDoc(docRef);
      
      if (docSnap.exists()) {
        setUserProfile(docSnap.data() as UserProfile);
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
    }
  };

  const loadUserTaxData = async (uid: string) => {
    try {
      const docRef = doc(db, 'taxData', uid);
      const docSnap = await getDoc(docRef);
      
      if (docSnap.exists()) {
        setTaxData(docSnap.data() as TaxData);
      } else {
        // Initialize empty tax data
        const emptyTaxData: TaxData = {
          incomeSources: [],
          deductions: [],
          calculations: [],
          records: [],
          lastSyncAt: new Date().toISOString()
        };
        setTaxData(emptyTaxData);
      }
    } catch (error) {
      console.error('Error loading tax data:', error);
    }
  };

  // =============================================================================
  // AUTHENTICATION METHODS
  // =============================================================================

  const signIn = async (email: string, password: string) => {
    try {
      clearError();
      setLoading(true);
      await signInWithEmailAndPassword(auth, email, password);
    } catch (error) {
      handleError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (email: string, password: string, profile: Partial<UserProfile>) => {
    try {
      clearError();
      setLoading(true);
      
      // Create user account
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // Update display name
      if (profile.displayName) {
        await updateProfile(user, { displayName: profile.displayName });
      }
      
      // Create user profile document
      const userProfile: UserProfile = {
        uid: user.uid,
        email: user.email!,
        displayName: profile.displayName || '',
        ...(profile.phoneNumber && { phoneNumber: profile.phoneNumber }),
        ...(profile.panNumber && { panNumber: profile.panNumber }),
        ...(profile.dateOfBirth && { dateOfBirth: profile.dateOfBirth }),
        ...(profile.profession && { profession: profile.profession }),
        ...(profile.annualIncome && { annualIncome: profile.annualIncome }),
        preferredTaxRegime: profile.preferredTaxRegime || 'new',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      await setDoc(doc(db, 'userProfiles', user.uid), userProfile);
      
      // Initialize empty tax data
      const initialTaxData: TaxData = {
        incomeSources: [],
        deductions: [],
        calculations: [],
        records: [],
        lastSyncAt: new Date().toISOString()
      };
      
      await setDoc(doc(db, 'taxData', user.uid), initialTaxData);
      
    } catch (error) {
      handleError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      clearError();
      await signOut(auth);
    } catch (error) {
      handleError(error);
      throw error;
    }
  };

  const resetPassword = async (email: string) => {
    try {
      clearError();
      await sendPasswordResetEmail(auth, email);
    } catch (error) {
      handleError(error);
      throw error;
    }
  };

  // =============================================================================
  // PROFILE METHODS
  // =============================================================================

  const updateUserProfile = async (updates: Partial<UserProfile>) => {
    try {
      if (!user || !userProfile) {
        throw new Error('No user logged in');
      }
      
      clearError();
      
      const updatedProfile = {
        ...userProfile,
        ...updates,
        updatedAt: new Date().toISOString()
      };
      
      await updateDoc(doc(db, 'userProfiles', user.uid), updatedProfile);
      setUserProfile(updatedProfile);
      
      // Update Firebase Auth profile if display name changed
      if (updates.displayName && updates.displayName !== user.displayName) {
        await updateProfile(user, { displayName: updates.displayName });
      }
      
    } catch (error) {
      handleError(error);
      throw error;
    }
  };

  // =============================================================================
  // DATA SYNC METHODS
  // =============================================================================

  const syncTaxData = async (data: Partial<TaxData>) => {
    try {
      if (!user) {
        throw new Error('No user logged in');
      }
      
      clearError();
      
      const updatedTaxData = {
        ...taxData,
        ...data,
        lastSyncAt: new Date().toISOString()
      };
      
      await updateDoc(doc(db, 'taxData', user.uid), updatedTaxData);
      setTaxData(updatedTaxData as TaxData);
      
    } catch (error) {
      handleError(error);
      throw error;
    }
  };

  const loadTaxData = async (): Promise<TaxData | null> => {
    try {
      if (!user) {
        throw new Error('No user logged in');
      }
      
      clearError();
      
      const docRef = doc(db, 'taxData', user.uid);
      const docSnap = await getDoc(docRef);
      
      if (docSnap.exists()) {
        const data = docSnap.data() as TaxData;
        setTaxData(data);
        return data;
      }
      
      return null;
    } catch (error) {
      handleError(error);
      throw error;
    }
  };

  // =============================================================================
  // CONTEXT VALUE
  // =============================================================================

  const value: AuthContextType = {
    user,
    userProfile,
    taxData,
    loading,
    error,
    signIn,
    signUp,
    logout,
    resetPassword,
    updateUserProfile,
    syncTaxData,
    loadTaxData
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider; 