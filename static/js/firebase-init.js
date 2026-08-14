// Import Firebase SDK functions using ESM CDN for browser compatibility
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAnalytics, isSupported } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-analytics.js";

// Firebase configuration for dermai-skincare-app
const firebaseConfig = {
  apiKey: "AIzaSyB935OMajoR4PFgSejKkGQUuvdxD3fvKDI",
  authDomain: "dermai-skincare-app.firebaseapp.com",
  projectId: "dermai-skincare-app",
  storageBucket: "dermai-skincare-app.firebasestorage.app",
  messagingSenderId: "459908211039",
  appId: "1:459908211039:web:75ff0fca98dd4618c496ea",
  measurementId: "G-9WE24B5JKP"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

let analytics = null;
isSupported().then(supported => {
  if (supported) {
    analytics = getAnalytics(app);
    window.firebaseAnalytics = analytics;
    console.log("Firebase Analytics initialized successfully");
  }
}).catch(err => {
  console.warn("Firebase Analytics not supported in current environment:", err);
});

// Attach to window for global availability if needed
window.firebaseApp = app;

export { app, analytics };
