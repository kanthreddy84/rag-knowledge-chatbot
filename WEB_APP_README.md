# DataFactZ HR Policy Assistant - Web App

Production-ready React web application for the RAG chatbot system. Enterprise-grade interface with DataFactZ branding, built with React 18, Tailwind CSS, and Lucide icons.

## Features

✅ **Real-time Chat Interface**
- Natural language query input
- Streaming message display with animations
- Citation extraction with relevance scores
- Confidence indicators (HIGH/MEDIUM/LOW)
- Message history and context awareness

✅ **Document Management**
- Visual document list with statistics
- Chunk and token counts
- One-click reindexing
- Document upload functionality
- Delete documents

✅ **Intelligent Settings**
- LLM configuration (FREE/HYBRID/CLOUD)
- Temperature tuning
- Confidence thresholds
- Retrieval settings
- System status dashboard

✅ **DataFactZ Design System**
- Gradient brand colors (yellow → orange → red)
- Dark mode by default
- Smooth animations and hover effects
- Enterprise typography
- Lucide icon library

✅ **Responsive Layout**
- Desktop-optimized interface
- Mobile sidebar collapse
- Gesture support
- Touch-friendly controls

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           React Web App (Port 3000)                 │
│  ┌──────────────────────────────────────────────┐   │
│  │  Chat Page    │ Documents  │ Settings        │   │
│  │  • Messages   │ • List     │ • Model Config  │   │
│  │  • Citations  │ • Reindex  │ • Parameters    │   │
│  │  • Input      │ • Upload   │ • Status        │   │
│  └──────────────────────────────────────────────┘   │
│           ↓ Axios HTTP Requests                     │
├─────────────────────────────────────────────────────┤
│    FastAPI Backend (Port 8000) - api_server.py      │
│  • Query processing                                 │
│  • Document management                              │
│  • Embedding integration                            │
│  • Reindexing                                       │
├─────────────────────────────────────────────────────┤
│         RAG System Components                       │
│  • Document Chunker                                 │
│  • Embedding Model (sentence-transformers)         │
│  • Vector Database (FAISS/Pinecone)                │
│  • LLM (Ollama/Claude/Together AI)                 │
└─────────────────────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites
- Node.js 16+ and npm 8+
- Python 3.10+ (for backend)
- 2GB RAM minimum

### Step 1: Install Frontend Dependencies

```bash
cd web-app
npm install
```

Takes ~2-3 minutes. Installs React, Tailwind, Lucide, Axios, and routing libraries.

### Step 2: Configure Environment

```bash
cp .env.example .env
```

Default configuration:
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development
```

### Step 3: Install Backend Dependencies (if not already done)

```bash
cd ..  # Go to project root
pip install -r requirements.txt
```

Ensure you have:
- `document_chunking.py`
- `sentence_transformers`
- `fastapi`
- `uvicorn`
- `sklearn`

### Step 4: Start Backend Server

```bash
python api_server.py
```

Output:
```
Starting DataFactZ RAG API Server...
Available at http://localhost:8000
Indexing sample documents...
✓ 6 documents indexed
✓ Ready to accept queries
```

### Step 5: Start Frontend (New Terminal)

```bash
cd web-app
npm start
```

Browser opens automatically to `http://localhost:3000`

---

## Component Library

### Button

```jsx
import { Button } from './components';

// Variants: primary, secondary, tertiary, danger, ghost
<Button variant="primary" size="base" icon={Send}>
  Send Query
</Button>

// All sizes
<Button size="sm">Small</Button>
<Button size="base">Base</Button>
<Button size="lg">Large</Button>

// Loading state
<Button loading>Processing...</Button>

// Full width
<Button fullWidth>Take full space</Button>
```

### Card

```jsx
import { Card, CardHeader, CardBody, CardFooter } from './components';

<Card interactive>  {/* Lifts on hover */}
  <CardHeader>
    <h2 className="heading-2">Policy Title</h2>
  </CardHeader>
  <CardBody>
    Main content goes here
  </CardBody>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Input

```jsx
import { Input } from './components';
import { Search } from 'lucide-react';

<Input
  label="Policy search"
  placeholder="What do you want to know?"
  icon={Search}
  error={error}
  helpText="Tip: Be specific"
/>
```

### Badge

```jsx
import { Badge } from './components';

<Badge variant="success">HIGH confidence</Badge>
<Badge variant="primary">12 documents</Badge>
<Badge variant="error">Error</Badge>
```

### Layout (Sidebar + Header)

```jsx
import { Layout } from './components';
import Sidebar from './components/Sidebar';

<Layout
  sidebar={<Sidebar />}
  header={<HeaderContent />}
>
  {/* Page content */}
</Layout>
```

---

## Page Documentation

### Chat Page (`/`)

Main conversational interface for querying policies.

**Key Components:**
- Message list with auto-scroll
- Input form with submit
- Citation display
- Confidence badges
- Copy message button
- Error handling
- Loading indicators

**Example Response:**
```
Q: How much vacation time do I get?

A: Based on our Leave and Time Off Policy, annual paid time off is allocated based on tenure:
   - 0-2 years: 15 days
   - 3-5 years: 20 days
   - 6+ years: 25 days

Sources:
  • Leave_and_Time_Off_Policy - 1.1 PTO Allocation (92% match)
  • Code_of_Conduct - 2.3 Attendance and Punctuality (45% match)

Confidence: HIGH
```

### Documents Page (`/documents`)

Manage indexed policy documents.

**Functions:**
1. **View Documents** - See all indexed files with stats
2. **Reindex** - Force re-processing of sample_data folder
3. **Delete** - Remove document from index
4. **Upload** - Add new PDF/DOCX/TXT files

**Statistics Shown:**
- Chunk count (usually 5-50 per document)
- Token count (for cost tracking)
- Indexed date
- Document status

### Settings Page (`/settings`)

Configure chatbot behavior and system parameters.

**Sections:**

1. **LLM Configuration**
   - FREE: Ollama (local, no API costs)
   - HYBRID: Claude 3.5 Sonnet ($3-5/month)
   - CLOUD: Together AI ($40-50/month)
   - Temperature: 0.0 (focused) → 1.0 (creative)

2. **Retrieval Settings**
   - Confidence threshold: 0.5-1.0
   - Max chunks: 1-20 documents to pass to LLM
   - These directly impact answer quality

3. **System Status**
   - Backend API connection
   - Vector database readiness
   - Embedding model status
   - Document count

---

## API Integration

Backend must expose these endpoints:

### POST /api/query

```javascript
// Request
{
  query: "How do I request remote work?",
  conversation_history: [
    {
      type: "user",
      content: "Previous message",
      timestamp: "2026-08-14T10:00:00Z"
    }
  ]
}

// Response
{
  answer: "Based on the Remote Work Policy...",
  citations: [
    {
      document_title: "Remote_Work_Policy",
      section_path: "2 > 2.1 > Remote Work Eligibility",
      excerpt: "Full-time employees with 6 months tenure...",
      relevance_score: 0.92
    }
  ],
  confidence: "HIGH",
  generation_time_seconds: 1.23
}
```

### GET /api/documents

```javascript
{
  documents: [
    {
      id: "leave_policy",
      filename: "Leave_and_Time_Off_Policy.txt",
      title: "Leave and Time Off Policy",
      description: "Comprehensive PTO and leave guidelines",
      chunk_count: 42,
      token_count: 12500,
      indexed_at: "2026-08-14T10:00:00Z",
      status: "indexed"
    }
  ]
}
```

### POST /api/reindex

Triggers re-processing of `sample_data/` folder. Returns progress updates.

### DELETE /api/documents/{id}

Removes document from index and vector store.

### POST /api/documents/upload

Accepts multipart file upload, processes, and indexes document.

---

## Design System Details

### Color Palette

```css
Primary Gradient: 
  #F4AD0B (yellow) → #FC7900 (orange) → #E3434A (red)

Core Colors:
  Orange (#FC7900) - Primary actions, links, accents
  Navy (#182127) - Headings, dark chrome
  Dark (#0F1419) - Backgrounds
  Gray: 50/100/200/300/400/500/600/700/800/900

Used in:
  - Buttons (gradient)
  - Links and hovers
  - Badges and status
  - Focus rings
  - Border accents
```

### Typography Scale

```
Heading 1: 48px, bold, tracking -0.03em
Heading 2: 32px, bold, tracking -0.02em
Heading 3: 24px, bold, tracking -0.02em
Body: 16px, regular, line-height 1.5
Label: 14px, medium, sentence case
Caption: 12px, regular

Font Family: Inter (all weights)
```

### Spacing

```
xs: 4px (1 unit)
sm: 8px (2 units)
md: 16px (4 units)
lg: 24px (6 units)
xl: 32px (8 units)
2xl: 48px (12 units)
```

### Component Styles

```
Cards:
  - rounded-xl (12px)
  - hover: shadow-lg + translateY(-5px)
  - border: 1px solid gray-800
  - background: gray-900

Buttons:
  - rounded-md (6px)
  - focus: ring-2 ring-orange
  - active: scale-95

Pills/Badges:
  - rounded-full
  - padding: px-2.5 py-1
```

---

## Customization Guide

### Change Brand Colors

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

Update component button gradients in `src/components/Button.jsx`:
```jsx
'bg-gradient-to-r from-datafacz-yellow via-datafacz-orange to-datafacz-red'
```

### Add New Page

1. Create `src/pages/NewPage.jsx`
2. Add route in `App.jsx`
3. Add nav item in `Sidebar.jsx`

```jsx
// Sidebar.jsx
const navItems = [
  // existing items...
  { icon: FileText, label: 'New Page', href: '/new', id: 'new' },
];
```

### Modify Chat Page

Key files:
- `src/pages/ChatPage.jsx` - Main chat interface
- `src/components/Sidebar.jsx` - Navigation
- `src/index.css` - Tailwind styles

Common changes:
- Adjust message animation in `animate-in` class
- Change input placeholder text
- Modify citation display format
- Adjust confidence badge colors

### Add Dark/Light Mode Toggle

```jsx
// In Sidebar.jsx
const [darkMode, setDarkMode] = useState(true);

useEffect(() => {
  if (darkMode) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}, [darkMode]);
```

---

## Production Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Connect repo to Vercel
3. Environment variables in dashboard:
   ```
   REACT_APP_API_URL=https://api.yourdomain.com
   REACT_APP_ENVIRONMENT=production
   ```
4. Auto-deploy on push

### Docker Deployment

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/build ./build
EXPOSE 3000
CMD ["serve", "-s", "build"]
```

### AWS/Azure/GCP

Use provided Docker setup above, deploy to:
- AWS Amplify / ECS
- Azure App Service
- Google Cloud Run

---

## Performance Optimization

```javascript
// Lazy load pages
const ChatPage = React.lazy(() => import('./pages/ChatPage'));

// Memoize components
export default React.memo(MessageList);

// Virtualize long lists
import { FixedSizeList } from 'react-window';

// Code splitting
const [showSettings, setShowSettings] = useState(false);
const Settings = React.lazy(() => import('./pages/SettingsPage'));

{showSettings && <Suspense><Settings /></Suspense>}
```

---

## Browser Support

| Browser | Version | Support |
|---------|---------|---------|
| Chrome | 90+ | ✅ Full |
| Firefox | 88+ | ✅ Full |
| Safari | 14+ | ✅ Full |
| Edge | 90+ | ✅ Full |
| Mobile Chrome | Latest | ✅ Full |
| Mobile Safari | 14+ | ✅ Full |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 3000 in use | `lsof -ti:3000 \| xargs kill -9` |
| API not connecting | Check `REACT_APP_API_URL` in `.env` |
| Styles not loading | `rm -rf node_modules && npm install` |
| Hot reload not working | Restart dev server |
| Module not found | `npm install` missing dependency |

---

## File Structure Overview

```
src/
├── components/          # Reusable UI components
│   ├── Button.jsx       # Button with variants
│   ├── Card.jsx         # Card container
│   ├── Input.jsx        # Form input
│   ├── Badge.jsx        # Status badge
│   ├── Layout.jsx       # Main layout wrapper
│   ├── Sidebar.jsx      # Navigation sidebar
│   └── index.js         # Exports
├── pages/               # Page components
│   ├── ChatPage.jsx     # Chat interface
│   ├── DocumentsPage.jsx # Document management
│   └── SettingsPage.jsx # Settings
├── App.jsx              # Router and app setup
├── index.js             # Entry point
└── index.css            # Global styles + Tailwind

public/
└── index.html           # HTML template

.env                    # Environment configuration
package.json            # Dependencies
tailwind.config.js      # Tailwind theme
postcss.config.js       # CSS processing
```

---

## Support

- **Issues**: Report in project GitHub issues
- **Docs**: See WEB_APP_SETUP.md for detailed guide
- **API**: Run `python api_server.py` and visit http://localhost:8000/docs
- **Contact**: support@datafacz.com

---

**DataFactZ HR Policy Assistant v1.0.0**

Built with React 18, Tailwind CSS, Lucide Icons
Enterprise-grade UI for RAG chatbot systems

© 2026 DataFactZ. All rights reserved.
