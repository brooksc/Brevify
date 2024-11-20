# UI/UX Specification

## Design Philosophy

Brevify's UI/UX is built on FastHTML principles:
- Server-side rendering for performance
- Progressive enhancement with HTMX
- Minimal JavaScript
- Responsive design

## User Journey

### 1. Load Website
- Clean, minimal landing page
- Clear purpose statement
- Prominent channel URL input
- Simple instructions

### 2. Enter Channel URL
- Large, focused input field
- Placeholder text with URL example
- Real-time validation feedback
- Support for all URL formats

### 3. Click Fetch Button
- Clear, prominent "Fetch Videos" button
- Visual loading indicator
- Error messages if needed
- Success feedback

### 4. View Video List
- Responsive grid layout
- Clean video cards
- AI tool buttons
- Smooth transitions

## Component Structure

### 1. Main Layout
```python
class MainLayout(Component):
    def render(self):
        return Div(
            Header(),
            MainContent(),
            Footer()
        )
```

### 2. Core Components

#### URL Input
- Clean, prominent input field
- Real-time validation
- Clear error feedback
- Loading indicators

#### Video Display
- Thumbnail preview
- Title and metadata
- Transcript preview
- AI service options

#### Settings Panel
- Theme toggle
- AI service selection
- Prompt template editor
- Preference controls

## Component Design

### Layout Structure
```
+----------------------------------+
|           Header Bar             |
+----------------------------------+
|         URL Input Area           |
+----------------------------------+
|         Video List Area          |
+----------------------------------+
```

### Component Details

#### Header Bar
- Height: 64px
- Background: Primary color
- Contents:
  - Logo/App Name (left, 24px height)
  - Theme Toggle (right, 32px)

#### URL Input Area
- Height: Auto (min 120px)
- Padding: 24px
- Background: Subtle contrast
- URL Input Field:
  - Width: 100% (max 800px)
  - Height: 48px
  - Border: 2px solid accent
  - Border-radius: 8px
  - Font: 16px

#### Video Card
- Width: 100% (max 800px)
- Margin: 16px auto
- Border-radius: 12px
- Box-shadow: Subtle elevation
- Sections:
  - Thumbnail (240x135px)
  - Info (title, channel, duration)
  - AI Tool Buttons

### 1. Header
```python
class Header(Component):
    def render(self):
        return Div(
            H1("Brevify", cls="text-4xl font-bold text-blue-600"),
            P("Transform YouTube channels into interactive learning experiences",
              cls="text-xl text-gray-600")
        )
```

### 2. URL Input
```python
class URLInput(Component):
    def render(self):
        return Form(
            Label("YouTube Channel URL"),
            Input(
                type="text",
                placeholder="https://youtube.com/c/...",
                cls="w-full p-2 border rounded"
            ),
            Button(
                "Fetch Videos",
                cls="bg-blue-600 text-white px-4 py-2 rounded"
            )
        )
```

### 3. Video Card
```python
class VideoCard(Component):
    def render(self):
        return Div(
            Img(src=self.video.thumbnail_url),
            H3(self.video.title),
            P(self.video.description),
            Div(
                Button("Open in ChatGPT"),
                Button("Open in Claude")
            )
        )
```

## Visual Design

### Typography
- Font Family: Inter, system-ui
- Font Sizes:
  - Title: 18px/16px (desktop/mobile)
  - Body: 14px/12px
  - Button: 14px
  - Metadata: 12px/10px

### Color Scheme

#### Light Mode
- Background: #FFFFFF
- Card Background: #F9FAFB
- Primary Text: #111827
- Secondary Text: #6B7280
- Border: #E5E7EB
- Accent: #2563EB

#### Dark Mode
- Background: #111827
- Card Background: #1F2937
- Primary Text: #F9FAFB
- Secondary Text: #9CA3AF
- Border: #374151
- Accent: #3B82F6

### AI Tool Colors
- ChatGPT: #10A37F
- Claude: #7C3AED

## Interactions

### Animations
- Color transitions: 200ms ease
- Scale transitions: 150ms ease-in-out
- Loading spinner: 1s linear infinite
- Skeleton pulse: 2s ease-in-out infinite

### States
- Hover: Slight scale (1.02)
- Active: Scale down (0.98)
- Focus: High contrast ring
- Loading: Pulse animation
- Error: Shake animation

## Responsive Design

### Desktop (>1024px)
- Max width: 800px
- Full features
- 3-column grid

### Tablet (768px-1024px)
- Max width: 90%
- 2-column grid
- Maintained layout

### Mobile (<768px)
- Full width
- Single column
- Stacked components
- Adjusted font sizes

## Accessibility

### Standards
- WCAG AA compliance
- Keyboard navigation
- Screen reader support
- High contrast mode

### Implementation
- ARIA labels
- Focus management
- Skip links
- Color contrast 4.5:1

## Performance Considerations

### 1. Loading
- Progressive enhancement
- Lazy loading
- Resource optimization
- Caching strategy

### 2. Interaction
- Instant feedback
- Minimal latency
- Smooth animations
- Error prevention

## Implementation Guidelines

### 1. Components
```python
# Example component structure
class VideoCard(Component):
    def render(self):
        return Article(
            VideoThumbnail(),
            VideoMetadata(),
            ActionButtons()
        )
```

### 2. Styling
- TailwindCSS integration
- Component-scoped styles
- Theme variables
- Utility classes

### 3. Interactivity
- HTMX attributes
- Event delegation
- State management
- Error boundaries

## Testing Requirements

### 1. Visual Testing
- Component rendering
- Responsive behavior
- Theme switching
- Loading states

### 2. Interaction Testing
- User flows
- Error handling
- Accessibility
- Performance metrics

## Documentation

### 1. Component Library
- Usage examples
- Props documentation
- Styling guidelines
- Best practices

### 2. Style Guide
- Color palette
- Typography scale
- Spacing system
- Component patterns
