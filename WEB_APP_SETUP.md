# DataFactZ HR Policy Assistant - Web App Setup Guide

Complete guide to setting up and running the DataFactZ React web application for the RAG chatbot.

## Quick Start

```bash
cd web-app
npm install
npm start
```

The app will open at `http://localhost:3000`

---

## Project Structure

```
web-app/
├── public/
│   └── index.html                 # HTML template
├── src/
│   ├── components/
│   │   ├── Button.jsx             # Reusable button component
│   │   ├── Card.jsx               # Card components (Card, CardHeader, CardBody, CardFooter)
│   │   ├── Input.jsx              # Form input component
│   │   ├── Badge.jsx              # Badge/pill component
│   │   ├── Layout.jsx             # Main layout wrapper with sidebar
│   │   ├── Sidebar.jsx            # Navigation sidebar
│   │   └── index.js               # Component exports
│   ├── pages/
│   │   ├── ChatPage.jsx           # Main chat interface
│   │   ├── DocumentsPage.jsx      # Document management
│   │   └── SettingsPage.jsx       # Application settings
│   ├── App.jsx                    # Router and main app
│   ├── index.js                   # React entry point
│   └── index.css                  # Global styles and Tailwind directives
├── package.json                   # Dependencies
├── tailwind.config.js             # Tailwind CSS configuration
├── postcss.config.js              # PostCSS configuration
└── .env.example                   # Environment variables template
```

---

## Installation

### Prerequisites
- Node.js 16+ (download from nodejs.org)
- npm 8+

### Step 1: Install Dependencies

```bash
cd web-app
npm install
```

This installs:
- React 18
- React Router v6
- Tailwind CSS 3
- Lucide React (icons)
- Axios (API client)
- clsx (class utilities)

### Step 2: Environment Configuration

Create `.env` file in `web-app/` directory:

```bash
cp .env.example .env
```

Update the API URL if your backend is running on a different port:

```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development
```

---

## Running the Application

### Development Mode

```bash
npm start
```

- Opens automatically at `http://localhost:3000`
- Hot reload on file changes
- React DevTools compatible

### Production Build

```bash
npm run build
```

Creates optimized build in `build/` folder, ready for deployment.

---

## Design System & Brand Standards

### Brand Colors (DataFactZ)

```
Primary Gradient: #F4AD0B (yellow) → #FC7900 (orange) → #E3434A (red)
Primary Action: #FC7900 (orange)
Dark Chrome: #182127 (navy)
Background: #0F1419 (dark)
```

### Component Architecture

#### Button Component
```jsx
import { Button } from './components';

<Button variant="primary" size="base" icon={Send}>
  Send
</Button>
```

Variants: `primary`, `secondary`, `tertiary`, `danger`, `ghost`
Sizes: `sm`, `base`, `lg`

#### Card Component
```jsx
import { Card, CardHeader, CardBody, CardFooter } from './components';

<Card interactive>
  <CardHeader>Title</CardHeader>
  <CardBody>Content</CardBody>
  <CardFooter>Actions</CardFooter>
</Card>
```

#### Input Component
```jsx
import { Input } from './components';

<Input
  label="Question"
  placeholder="Ask about policies..."
  error={errors.query}
  helpText="Be specific for better results"
/>
```

#### Badge Component
```jsx
import { Badge } from './components';

<Badge variant="success">HIGH confidence</Badge>
```

Variants: `primary`, `success`, `error`, `warning`, `gray`

### Icon Library

Uses Lucide React exclusively. Install with:

```bash
npm install lucide-react
```

Usage:
```jsx
import { Send, FileText, MessageSquare } from 'lucide-react';

<Send size={20} className="text-datafacz-orange" />
```

### Typography

- Font: Inter (all weights)
- Large headings: tight tracking (-0.03em)
- Buttons/nav: sentence case
- Page titles: Title Case

CSS classes available:
- `.heading-1` (48px, bold, tight tracking)
- `.heading-2` (32px, bold, tight tracking)
- `.heading-3` (24px, bold, tight tracking)
- `.body-text` (16px, relaxed line-height)
- `.text-muted` (gray 400)

---

## Pages Overview

### 1. Chat Page (/)

Main conversation interface with RAG chatbot.

**Features:**
- Real-time message display
- Source citations with relevance scores
- Confidence indicators (HIGH/MEDIUM/LOW)
- Message copying
- Animated message appearance
- Error handling
- Loading states

**API Integration:**
```
POST /api/query
{
  "query": "How much vacation time do I get?",
  "conversation_history": [...]
}

Response:
{
  "answer": "Based on our policies...",
  "citations": [...],
  "confidence": "HIGH"
}
```

### 2. Documents Page (/documents)

Manage indexed HR policy documents.

**Features:**
- Document list with chunk/token counts
- Reindex functionality
- Delete documents
- Upload new documents
- Document statistics

**API Integration:**
```
GET /api/documents
POST /api/reindex
DELETE /api/documents/{id}
POST /api/documents/upload
```

### 3. Settings Page (/settings)

Configure chatbot behavior and system settings.

**Options:**
- LLM Type: FREE (Ollama), HYBRID (Claude), CLOUD (Together AI)
- Temperature control (0.0 - 1.0)
- Confidence threshold
- Max chunks to retrieve
- System status monitoring

---

## Backend API Integration

The web app expects a FastAPI backend running on `http://localhost:8000`

### Required Endpoints

#### Chat Query
```
POST /api/query
Content-Type: application/json

{
  "query": "string",
  "conversation_history": [
    {
      "role": "user|assistant",
      "content": "string",
      "timestamp": "ISO8601"
    }
  ]
}

Response 200:
{
  "answer": "string",
  "citations": [
    {
      "document_title": "string",
      "section_path": "string",
      "excerpt": "string",
      "relevance_score": 0.85
    }
  ],
  "confidence": "HIGH|MEDIUM|LOW",
  "generation_time_seconds": 2.34
}
```

#### Get Documents
```
GET /api/documents

Response 200:
{
  "documents": [
    {
      "id": "string",
      "filename": "string",
      "title": "string",
      "description": "string",
      "chunk_count": 42,
      "token_count": 12500,
      "indexed_at": "ISO8601",
      "status": "indexed|processing"
    }
  ]
}
```

#### Reindex Documents
```
POST /api/reindex

Response 200:
{
  "status": "reindexing",
  "progress": 0.5,
  "documents_processed": 6
}
```

---

## Customization Guide

### Changing Brand Colors

Edit `tailwind.config.js`:

```js
colors: {
  datafacz: {
    yellow: '#F4AD0B',
    orange: '#FC7900',
    red: '#E3434A',
    navy: '#182127',
  }
}
```

Update CSS variables in `src/index.css`:

```css
:root {
  --color-yellow: #F4AD0B;
  --color-orange: #FC7900;
  --color-red: #E3434A;
  --color-navy: #182127;
}
```

### Adding New Pages

1. Create component in `src/pages/NewPage.jsx`
2. Add route to `src/App.jsx`:
```jsx
<Route path="/new-page" element={<NewPage />} />
```
3. Add navigation in `src/components/Sidebar.jsx`:
```jsx
{ icon: NewIcon, label: 'New Page', href: '/new-page', id: 'new' }
```

### Modifying Components

All reusable components are in `src/components/`. Follow naming conventions:
- Component files: PascalCase (`Button.jsx`)
- Exported components: PascalCase (`Button`)
- Props use camelCase

---

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy automatically on push

### Docker

Create `Dockerfile`:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables for Production

```
REACT_APP_API_URL=https://api.datafacz.com
REACT_APP_ENVIRONMENT=production
```

---

## Troubleshooting

### Port 3000 Already in Use
```bash
# Kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:3000 | xargs kill -9
```

### API Connection Error
- Verify backend is running: `http://localhost:8000/docs`
- Check `REACT_APP_API_URL` in `.env`
- Check CORS headers in backend FastAPI app

### Styling Not Applied
1. Rebuild Tailwind CSS: `npm run build`
2. Clear browser cache (Ctrl+Shift+Delete)
3. Check console for CSS errors

### Hot Reload Not Working
- Delete `node_modules` and `.package-lock.json`
- Run `npm install` again
- Restart dev server

---

## Development Workflow

1. Create feature branch: `git checkout -b feature/chat-improvements`
2. Make changes to components/pages
3. Test in browser (http://localhost:3000)
4. Verify API integration with backend
5. Commit with clear message: `git commit -m "feat: add message search"`
6. Push and create pull request

---

## Performance Tips

- Use React DevTools Profiler to identify slow renders
- Lazy load pages with React.lazy():
```jsx
const ChatPage = React.lazy(() => import('./pages/ChatPage'));
```

- Memoize expensive components:
```jsx
export default React.memo(MessageList);
```

- Optimize images and use WebP format

---

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Support & Documentation

- React: https://react.dev
- Tailwind: https://tailwindcss.com/docs
- Lucide Icons: https://lucide.dev
- React Router: https://reactrouter.com

For issues with DataFactZ app, contact: support@datafacz.com

---

**Last Updated:** August 2026
**Version:** 1.0.0
