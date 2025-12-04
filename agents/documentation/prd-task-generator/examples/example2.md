# Example 2: Advanced Usage - Dashboard with Existing Design System

## Scenario
Product team requests a new analytics dashboard. The project has an established design system and component library. The agent should identify reusable components to minimize new code.

## Input
```
Task with subagent_type: prd-task-generator
Prompt: "Generate implementation tasks from /docs/prd-analytics-dashboard.md.
Focus on identifying reusable components from our existing design system in src/components/ui/"
```

## PRD Summary (Simplified)
The PRD requests:
- Analytics dashboard page
- Chart displaying user metrics over time
- Data table with sortable columns
- Filter controls (date range, metric type)
- Export to CSV functionality
- Real-time data updates

## Agent Process

### Step 1: Enhanced Codebase Assessment
Agent performs thorough scan with focus on design system:
```
Reading: /docs/prd-analytics-dashboard.md
Scanning for existing components in src/components/ui/...

Found reusable components:
✓ src/components/ui/Card.tsx (can contain dashboard sections)
✓ src/components/ui/DataTable.tsx (existing sortable table)
✓ src/components/ui/DateRangePicker.tsx (for date filtering)
✓ src/components/ui/Select.tsx (for metric selection)
✓ src/components/ui/Button.tsx (for export action)

Found utilities:
✓ src/lib/utils/csvExport.ts (CSV export functionality)
✓ src/lib/hooks/useWebSocket.ts (real-time updates)

Missing:
✗ Chart component (need to add)
```

### Step 2: Parent Tasks with Context
Agent presents tasks highlighting what's reused vs. new:
```
I have generated the high-level tasks based on the PRD:

Analysis: Found extensive design system components that can be reused.
- DataTable, DateRangePicker, Select, Button, Card all exist
- CSV export utility exists
- WebSocket hook exists for real-time updates
- Only need to add: Chart component, API integration, dashboard layout

- [ ] 1.0 Set up analytics data API integration
- [ ] 2.0 Create chart visualization component (NEW - not in design system)
- [ ] 3.0 Build dashboard layout using existing UI components
- [ ] 4.0 Implement filtering and export features using existing utilities
- [ ] 5.0 Add real-time data updates using existing WebSocket hook
- [ ] 6.0 Write tests and documentation

Ready to generate the sub-tasks? Respond with 'Go' to proceed.
```

### Step 3: User Reviews and Confirms
```
User: Looks great! We can use Recharts for the chart component. Go.
```

### Step 4: Detailed Tasks with Reuse Focus
Agent generates tasks emphasizing component reuse.

## Output
File created: `/tasks/tasks-prd-analytics-dashboard.md`

```markdown
## Relevant Files

### New Files
- `src/components/analytics/AnalyticsChart.tsx` - Chart component using Recharts
- `src/components/analytics/AnalyticsChart.test.tsx` - Chart tests
- `src/components/analytics/AnalyticsDashboard.tsx` - Main dashboard layout
- `src/components/analytics/AnalyticsDashboard.test.tsx` - Dashboard tests
- `src/lib/api/analyticsApi.ts` - Analytics data API client
- `src/lib/api/analyticsApi.test.ts` - API tests
- `src/app/dashboard/analytics/page.tsx` - Analytics page route

### Modified Files
- `src/types/analytics.ts` - Add analytics data types
- `package.json` - Add recharts dependency

### Existing Files (Reused)
- `src/components/ui/Card.tsx` - For dashboard sections
- `src/components/ui/DataTable.tsx` - For metrics table
- `src/components/ui/DateRangePicker.tsx` - For date filtering
- `src/components/ui/Select.tsx` - For metric selection
- `src/components/ui/Button.tsx` - For export button
- `src/lib/utils/csvExport.ts` - For CSV export functionality
- `src/lib/hooks/useWebSocket.ts` - For real-time updates

### Notes

- Run tests with: `npx jest [optional/path/to/test/file]`
- Install Recharts: `npm install recharts`
- Reuse ALL existing UI components - do not recreate
- Follow existing dashboard patterns in src/app/dashboard/
- Use existing design tokens from src/styles/tokens.ts
- WebSocket connection URL: ws://api.example.com/analytics (from .env)

## Tasks

- [ ] 1.0 Set up analytics data API integration
  - [ ] 1.1 Define analytics data types in src/types/analytics.ts
  - [ ] 1.2 Create analyticsApi.ts with getMetrics, getChartData methods
  - [ ] 1.3 Add error handling and retry logic to API calls
  - [ ] 1.4 Write tests for API methods with mock data

- [ ] 2.0 Create chart visualization component (NEW)
  - [ ] 2.1 Install recharts: `npm install recharts`
  - [ ] 2.2 Create AnalyticsChart.tsx with line chart using Recharts
  - [ ] 2.3 Accept data, metricType, and dateRange as props
  - [ ] 2.4 Style chart to match design system colors (use tokens.ts)
  - [ ] 2.5 Add responsive sizing and tooltips
  - [ ] 2.6 Write tests for AnalyticsChart component

- [ ] 3.0 Build dashboard layout using existing UI components
  - [ ] 3.1 Create AnalyticsDashboard.tsx main component
  - [ ] 3.2 Use Card component to contain chart section
  - [ ] 3.3 Use Card component to contain data table section
  - [ ] 3.4 Import and use AnalyticsChart in chart Card
  - [ ] 3.5 Import and use DataTable (from ui/) in table Card
  - [ ] 3.6 Apply responsive grid layout (chart top, table bottom)
  - [ ] 3.7 Write tests for dashboard layout

- [ ] 4.0 Implement filtering and export using existing components
  - [ ] 4.1 Add DateRangePicker component for date filtering
  - [ ] 4.2 Add Select component for metric type selection
  - [ ] 4.3 Wire filter changes to update chart and table data
  - [ ] 4.4 Add Button component with "Export CSV" label
  - [ ] 4.5 Wire export button to existing csvExport.ts utility
  - [ ] 4.6 Format data correctly before passing to csvExport
  - [ ] 4.7 Write tests for filtering logic
  - [ ] 4.8 Write tests for export functionality

- [ ] 5.0 Add real-time data updates using existing WebSocket hook
  - [ ] 5.1 Import useWebSocket hook from lib/hooks/
  - [ ] 5.2 Connect to analytics WebSocket endpoint (from .env)
  - [ ] 5.3 Handle incoming real-time metric updates
  - [ ] 5.4 Update chart and table when new data arrives
  - [ ] 5.5 Add connection status indicator (connected/disconnected)
  - [ ] 5.6 Handle reconnection on connection loss
  - [ ] 5.7 Write tests for WebSocket integration

- [ ] 6.0 Write tests and documentation
  - [ ] 6.1 Write integration test for complete dashboard flow
  - [ ] 6.2 Test filtering changes chart and table data
  - [ ] 6.3 Test CSV export produces correct output
  - [ ] 6.4 Test real-time updates with mock WebSocket
  - [ ] 6.5 Test responsive layout on different screen sizes
  - [ ] 6.6 Add JSDoc comments to public functions
  - [ ] 6.7 Update README with analytics dashboard documentation
  - [ ] 6.8 Document design system component usage patterns
```

## How This Example Shows Advanced Features

### 1. Thorough Codebase Assessment
```
Agent scanned design system and found:
- 5 existing UI components to reuse
- 1 existing utility function
- 1 existing custom hook
```

### 2. Smart Task Planning
```
Instead of creating new components, tasks say:
❌ "Create button component"
✅ "Import and use Button component (from ui/)"

❌ "Build date picker"
✅ "Add DateRangePicker component for date filtering"
```

### 3. User Guidance
```
Notes section includes:
- Specific reuse instructions: "Reuse ALL existing UI components"
- Setup commands: "npm install recharts"
- Environment config: "WebSocket URL from .env"
- Pattern references: "Follow existing dashboard patterns"
```

### 4. Clear File Organization
```
Separates files into:
- New Files (need to create)
- Modified Files (need to update)
- Existing Files (just use as-is)
```

## Benefits in This Scenario

✅ **Reduced Development Time**: Reusing 8 existing components/utilities
✅ **Consistency**: Uses established design system
✅ **Less Code**: Only creating what's truly new (chart component)
✅ **Lower Maintenance**: Fewer components to maintain
✅ **Best Practices**: Follows existing patterns

## Comparison: With vs Without Agent

### Without Agent (Manual Planning)
```
Developer might:
- Miss existing DateRangePicker → Build new one (2-3 hours wasted)
- Not know about csvExport utility → Rebuild CSV logic (1-2 hours)
- Forget WebSocket hook exists → Use different approach (inconsistent)
- Not align with design system → Need rework after code review

Result: 20-25 hours, inconsistent code, potential rework
```

### With Agent (Generated Plan)
```
Agent identifies:
✓ All reusable components
✓ Existing utilities
✓ Established patterns
✓ Design system tokens

Result: 10-12 hours, consistent code, no rework
```

## Time and Quality Impact

| Metric | Without Agent | With Agent | Improvement |
|--------|--------------|------------|-------------|
| Planning Time | 2-3 hours | 5 minutes | 96% faster |
| Implementation | 20-25 hours | 10-12 hours | 50% faster |
| Code Consistency | Variable | High | Consistent |
| Rework Needed | Likely | Minimal | 80% less |
| Components Created | 12-15 new | 2 new, 8 reused | 80% reuse |

## Key Takeaway

The agent's codebase assessment is especially valuable when:
- Existing design system or component library exists
- Multiple developers working on codebase (pattern consistency)
- Large codebase (hard to remember all utilities)
- Junior developers (may not know what exists)
