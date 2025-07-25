# PMSSRC Unified Monorepo

A unified monorepo containing the PMSSRC (Project Management System) web and mobile applications.

## Project Structure

```
pmssrc-unified/
├── backend/                    # FastAPI backend (existing)
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/        # API endpoints
│   │   │   └── controllers/   # Request handlers
│   │   ├── domain/            # Business entities
│   │   ├── application/       # Use cases and DTOs
│   │   └── infrastructure/    # Database and external services
│   └── requirements.txt
├── apps/
│   ├── web/                   # React web application (existing)
│   │   ├── src/
│   │   │   ├── components/    # React components
│   │   │   ├── pages/         # Page components
│   │   │   └── shared/        # Shared utilities
│   │   └── package.json
│   └── mobile/                # React Native mobile app (new)
│       ├── app/               # Expo Router routes
│       ├── src/
│       │   ├── modules/       # Feature modules
│       │   └── shared/        # Shared components
│       └── package.json
└── packages/
    ├── shared-types/          # Shared TypeScript types
    ├── api-client/            # API client for all platforms
    └── business-logic/        # Shared business logic
```

## Features

### Backend (FastAPI)
- **Authentication**: JWT-based authentication with biometric support
- **Attendance Management**: Real-time location tracking and geofencing
- **Leave Management**: Comprehensive leave application and approval system
- **Reimbursement**: Expense tracking and approval workflow
- **Taxation**: Tax calculation and reporting
- **Reporting**: Analytics and dashboard data
- **User Management**: Multi-organization user management

### Web Application (React)
- **Dashboard**: Real-time analytics and reporting
- **Attendance**: Check-in/out with location tracking
- **Leave Management**: Apply and approve leaves
- **Reimbursement**: Submit and approve expenses
- **Taxation**: Tax calculation and planning
- **User Management**: Admin panel for user management

### Mobile Application (React Native + Expo)
- **Biometric Authentication**: Fingerprint/Face ID login
- **Real-time Location Tracking**: GPS-based attendance
- **Geofencing**: Office location detection
- **Offline Support**: Internet connectivity validation
- **Push Notifications**: Real-time updates
- **Hybrid UI/UX**: Consistent design across platforms

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- Expo CLI
- MongoDB

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pmssrc-unified
   ```

2. **Install dependencies**
   ```bash
   # Install root dependencies
   npm install
   
   # Install all workspace dependencies
   npm run install:all
   ```

3. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   
   # Web app
   cp apps/web/.env.example apps/web/.env
   
   # Mobile app
   cp apps/mobile/.env.example apps/mobile/.env
   ```

### Development

1. **Start backend server**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start web application**
   ```bash
   npm run dev:web
   ```

3. **Start mobile application**
   ```bash
   npm run dev:mobile
   ```

### Building

1. **Build web application**
   ```bash
   npm run build:web
   ```

2. **Build mobile application**
   ```bash
   npm run build:mobile
   ```

### Testing

1. **Run backend tests**
   ```bash
   npm run test:backend
   ```

2. **Run web tests**
   ```bash
   npm run test:web
   ```

3. **Run mobile tests**
   ```bash
   npm run test:mobile
   ```

## Shared Packages

### @pmssrc/shared-types
Contains TypeScript interfaces and types shared across all applications.

```typescript
import { User, AttendanceRecord, LeaveRecord } from '@pmssrc/shared-types';
```

### @pmssrc/api-client
Provides a unified API client for all platforms.

```typescript
import { apiClient } from '@pmssrc/api-client';

// Usage
const user = await apiClient.getUserById('user-123');
const attendance = await apiClient.checkIn({
  userId: 'user-123',
  location: { latitude: 40.7128, longitude: -74.0060 }
});
```

### @pmssrc/business-logic
Contains shared business logic and calculations.

```typescript
import { AttendanceCalculator, TaxCalculator } from '@pmssrc/business-logic';

// Usage
const workingHours = AttendanceCalculator.calculateWorkingHours(attendanceRecords);
const taxLiability = TaxCalculator.calculateBasicTax(taxableIncome);
```

## Architecture

### Clean Architecture (Backend)
- **Domain Layer**: Business entities and value objects
- **Application Layer**: Use cases and DTOs
- **Infrastructure Layer**: Database and external services
- **API Layer**: Controllers and routes

### Feature-Based Structure (Frontend)
- **Modules**: Feature-based organization
- **Shared Components**: Reusable UI components
- **API Integration**: Centralized API client
- **State Management**: Context-based state management

## Key Features

### Authentication
- JWT-based authentication
- Biometric authentication (mobile)
- Role-based access control
- Session management

### Location Services
- Real-time GPS tracking
- Geofencing for office locations
- Location accuracy validation
- Offline location caching

### Data Synchronization
- Internet connectivity validation
- Real-time data updates
- Conflict resolution
- Offline queue management

### UI/UX
- Hybrid design approach
- Responsive layouts
- Consistent theming
- Mobile-optimized components

## Deployment

### Backend Deployment
```bash
# Production
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Web Application Deployment
```bash
# Build for production
npm run build:web

# Deploy to hosting service (e.g., Vercel, Netlify)
```

### Mobile Application Deployment
```bash
# Build for app stores
cd apps/mobile
eas build --platform all --profile production
```

## Contributing

1. Follow the existing code structure
2. Use shared packages for common functionality
3. Write tests for new features
4. Update documentation as needed
5. Follow the commit message convention

## License

[Your License Here]

## Support

For support and questions, please contact [your-email@example.com] 