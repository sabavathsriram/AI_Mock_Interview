# Frontend - AI-Powered Mock Interview System

React frontend for the AI-powered mock interview platform.

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/         # Page components (routes)
├── services/      # API service modules
├── utils/         # Utility functions
├── hooks/         # Custom React hooks
├── contexts/      # React context providers
├── assets/        # Static assets (images, fonts, etc.)
├── styles/        # CSS styles and themes
├── App.tsx        # Main application component
└── main.tsx       # Application entry point
```

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Variables

Create a `.env` file in the frontend directory:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME="AI Mock Interview System"
VITE_APP_VERSION=0.1.0
```

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at:
- http://localhost:3000

### 4. Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Features

- **React 18** with TypeScript
- **Vite** for fast development and building
- **React Router** for client-side routing
- **Axios** for HTTP requests
- **ESLint** for code quality
- **Path aliases** for cleaner imports

## Development Notes

### Path Aliases

Use these aliases for cleaner imports:

```typescript
import { Component } from '@/components/Component'
import { apiService } from '@services/api'
import { useCustomHook } from '@hooks/useCustomHook'
```

### API Proxy

During development, API requests to `/api` are proxied to the backend server (http://localhost:8000) to avoid CORS issues.

### Component Structure

- **Components**: Reusable UI elements (buttons, forms, modals, etc.)
- **Pages**: Route-level components that compose multiple components
- **Services**: API communication and business logic
- **Hooks**: Custom React hooks for shared logic
- **Contexts**: Global state management

## Future Implementation Areas

1. **Interview Interface**: Real-time interview session UI
2. **User Authentication**: Login, registration, and profile management
3. **Real-time Communication**: WebSocket integration for live interviews
4. **Analytics Dashboard**: Performance tracking and visualization
5. **Theme System**: Light/dark mode and customization
6. **Accessibility**: Full WCAG compliance
7. **Internationalization**: Multi-language support