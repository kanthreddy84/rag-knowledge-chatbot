# Clickable Citations Feature - Implementation Guide

## Overview
The RAG chatbot now includes an interactive document viewer that allows users to click on source citations and view the original documents with the cited passages highlighted.

## Features

### 1. **Clickable Citations**
- All source citations in the answer panel are now clickable
- Hover over a citation to see "Click to view source" prompt
- Click any citation to open the document viewer panel

### 2. **Document Viewer Panel**
- Opens on the right side of the chat interface
- Displays full document content
- Auto-scrolls to and highlights the cited passage
- Smooth transitions when opening/closing

### 3. **Document Viewer Controls**
- **Close Button (X):** Close the viewer and return to full chat view
- **Copy Button:** Copy entire document text to clipboard
- **Download Button:** Download the document as a .txt file
- **Loading State:** Shows spinner while document is being fetched

### 4. **Smart Highlighting**
- Automatically finds and highlights the exact passage cited
- Uses browser's native text selection for highlighting
- Scrolls cited passage into view automatically
- Works across multiple lines and paragraphs

## Architecture

### Backend Changes (api_server.py)

#### New Storage
```python
full_documents = {}  # Stores full document text
```

#### Updated Citation Model
```python
class Citation(BaseModel):
    document_title: str
    section_path: str
    excerpt: str
    relevance_score: float
    chunk_index: Optional[int] = None  # For future use
```

#### New API Endpoints

**1. Get Full Document Content**
```
GET /api/documents/{doc_id}/content
Response:
{
  "document_id": "Code_of_Conduct",
  "content": "Full document text here...",
  "title": "Code Of Conduct"
}
```

**2. Get Specific Chunk**
```
GET /api/chunks/{chunk_index}
Response:
{
  "chunk_index": 5,
  "document_title": "Code_of_Conduct",
  "section_path": "7.1 Dress Code Standards",
  "text": "Chunk text here...",
  "context_before": "Previous chunk text...",
  "context_after": "Next chunk text...",
  "chunk_number": 6,
  "token_count": 400
}
```

### Frontend Components

#### DocumentViewer Component (new)
**Location:** `web-app/src/components/DocumentViewer.jsx`

**Props:**
- `citation`: Citation object with document info
- `onClose`: Callback function when viewer is closed

**Features:**
- Fetches full document from backend
- Displays document in scrollable panel
- Highlights cited passages
- Provides copy/download functionality
- Responsive loading and error states

#### ChatPage Updates
**Location:** `web-app/src/pages/ChatPage.jsx`

**Changes:**
1. Added `selectedCitation` state
2. Made citations clickable with `onClick` handlers
3. Updated layout to show 50/50 split when viewer is open
4. Integrated DocumentViewer component

**Layout Behavior:**
- Default: Chat takes full width
- With Viewer: Chat takes 50%, Document Viewer takes 50%
- Smooth transitions using Tailwind CSS classes

## User Workflow

1. **Ask Question**
   - User sends a query about HR policies
   - Assistant provides answer with source citations

2. **Click Citation**
   - User clicks on any source citation
   - Document viewer panel opens on the right
   - Document loads from backend
   - Cited passage auto-highlights

3. **View Document**
   - User reads the full document context
   - Can scroll through entire document
   - Citation passage remains highlighted
   - Can copy or download document

4. **Close Viewer**
   - Click the X button to close viewer
   - Chat panel expands to full width
   - View remains expandable for multiple citations

## Technical Implementation Details

### Highlighting Algorithm
```javascript
1. Get full document content
2. Find citation text in document
3. Create TreeWalker to traverse DOM nodes
4. Calculate character positions for start/end
5. Create Range and set start/end nodes
6. Apply selection to highlight text
7. Scroll range into view with smooth behavior
```

### API Integration
- All requests go to `http://localhost:8000`
- Uses Axios for HTTP requests
- Error handling for missing documents
- Loading states during fetch

### State Management
- `selectedCitation`: Controls visibility of document viewer
- Citation state persists until user closes viewer
- Multiple citations can be clicked sequentially

## File Changes Summary

### Backend
- **Modified:** `api_server.py`
  - Added `full_documents` storage
  - Updated `Citation` model
  - Added document reindexing logic
  - Created 2 new API endpoints

### Frontend
- **Created:** `web-app/src/components/DocumentViewer.jsx` (new component)
- **Modified:** `web-app/src/pages/ChatPage.jsx`
  - Added document viewer integration
  - Made citations interactive
  - Updated layout structure

## Testing Checklist

- [ ] Ask a question about any HR policy
- [ ] Click on a source citation
- [ ] Verify document viewer opens on right side
- [ ] Verify cited passage is highlighted
- [ ] Verify viewer can be closed with X button
- [ ] Click another citation while viewer is open
- [ ] Verify document changes to new selection
- [ ] Test copy button functionality
- [ ] Test download button functionality
- [ ] Test on mobile (should stack vertically)
- [ ] Test error handling for missing documents
- [ ] Verify smooth transitions and animations

## Future Enhancements

1. **Multiple Viewer Modes**
   - Side-by-side comparison of multiple citations
   - Tabbed document viewer

2. **Search Functionality**
   - Search within document
   - Jump to next/previous occurrence

3. **Annotation System**
   - Bookmark important passages
   - Add personal notes to passages
   - Export annotations

4. **Advanced Highlighting**
   - Color-code different sections
   - Customizable highlight colors
   - Smart section detection

5. **Document Context**
   - Show section hierarchy
   - Navigate by sections
   - Quick navigation sidebar

## Performance Considerations

- Documents are loaded on demand (lazy loading)
- Full document text stored in memory for fast access
- Highlighting algorithm uses efficient DOM traversal
- Smooth scrolling using native browser APIs

## Browser Compatibility

- Works in all modern browsers (Chrome, Firefox, Safari, Edge)
- Uses standard DOM APIs (TreeWalker, Range, Selection)
- Responsive design works on desktop and tablet
- Mobile: Document viewer stacks below chat

## Accessibility

- Keyboard navigation support (Escape to close viewer)
- ARIA labels for screen readers
- High contrast highlighting for visibility
- Clear visual feedback for interactions
