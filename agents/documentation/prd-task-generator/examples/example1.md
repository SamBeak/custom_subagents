# Example 1: Basic Usage - User Profile Editing Feature

## Scenario
The product team has created a PRD for a user profile editing feature. A junior developer needs a clear implementation plan.

## Input
```
Task with subagent_type: prd-task-generator
Prompt: "Generate implementation tasks from /docs/prd-user-profile-editing.md"
```

## PRD Summary (Simplified)
The PRD requests:
- User profile editing page
- Form with name, email, bio fields
- Profile picture upload
- Save and cancel buttons
- Validation and error handling
- Integration with existing user API

## Agent Process

### Step 1: Initial Analysis
Agent reads the PRD and scans the codebase:
```
Reading: /docs/prd-user-profile-editing.md
Scanning codebase...
Found: src/lib/api/userApi.ts (existing user API)
Found: src/components/common/Button.tsx (reusable button)
Found: src/components/common/Input.tsx (reusable input)
```

### Step 2: Parent Tasks Generation
Agent presents high-level tasks:
```
I have generated the high-level tasks based on the PRD:

- [ ] 1.0 Create user profile data model and API integration
- [ ] 2.0 Build profile editing form component
- [ ] 3.0 Implement image upload functionality
- [ ] 4.0 Add form validation and error handling
- [ ] 5.0 Write tests and documentation

Ready to generate the sub-tasks? Respond with 'Go' to proceed.
```

### Step 3: User Confirmation
```
User: Go
```

### Step 4: Detailed Sub-Tasks Generation
Agent generates complete task list and saves to file.

## Output
File created: `/tasks/tasks-prd-user-profile-editing.md`

```markdown
## Relevant Files

- `src/components/profile/ProfileEditForm.tsx` - Main profile editing form component
- `src/components/profile/ProfileEditForm.test.tsx` - Unit tests for ProfileEditForm
- `src/components/profile/ProfileImageUpload.tsx` - Profile image upload component
- `src/components/profile/ProfileImageUpload.test.tsx` - Tests for image upload
- `src/lib/api/userApi.ts` - Existing user API (will be extended)
- `src/lib/api/userApi.test.ts` - Tests for user API
- `src/lib/validation/profileValidation.ts` - Profile form validation logic
- `src/lib/validation/profileValidation.test.ts` - Validation tests
- `src/app/profile/edit/page.tsx` - Profile edit page route
- `src/types/user.ts` - User type definitions (will be extended)

### Notes

- Unit tests should be placed alongside code files
- Run tests with: `npx jest [optional/path/to/test/file]`
- Reuse existing Button and Input components from src/components/common
- Follow existing form patterns in the codebase
- Use the existing userApi for backend communication

## Tasks

- [ ] 1.0 Create user profile data model and API integration
  - [ ] 1.1 Extend User type in src/types/user.ts with profile fields (bio, profileImageUrl)
  - [ ] 1.2 Add updateUserProfile method to src/lib/api/userApi.ts
  - [ ] 1.3 Add uploadProfileImage method to src/lib/api/userApi.ts
  - [ ] 1.4 Write tests for new API methods

- [ ] 2.0 Build profile editing form component
  - [ ] 2.1 Create ProfileEditForm.tsx with name, email, bio input fields
  - [ ] 2.2 Use existing Input component from src/components/common
  - [ ] 2.3 Add ProfileImageUpload component integration
  - [ ] 2.4 Implement save and cancel button handlers
  - [ ] 2.5 Add loading and success/error states
  - [ ] 2.6 Write component tests for ProfileEditForm

- [ ] 3.0 Implement image upload functionality
  - [ ] 3.1 Create ProfileImageUpload component with file selection
  - [ ] 3.2 Add image preview before upload
  - [ ] 3.3 Implement image upload with progress indicator
  - [ ] 3.4 Add image size and type validation (max 5MB, jpg/png only)
  - [ ] 3.5 Handle upload errors gracefully
  - [ ] 3.6 Write tests for ProfileImageUpload component

- [ ] 4.0 Add form validation and error handling
  - [ ] 4.1 Create profileValidation.ts with validation rules
  - [ ] 4.2 Validate name (required, min 2 chars, max 50 chars)
  - [ ] 4.3 Validate email (required, valid email format)
  - [ ] 4.4 Validate bio (optional, max 500 chars)
  - [ ] 4.5 Display inline error messages for invalid fields
  - [ ] 4.6 Prevent form submission if validation fails
  - [ ] 4.7 Write tests for validation logic

- [ ] 5.0 Write tests and documentation
  - [ ] 5.1 Write integration test for complete profile edit flow
  - [ ] 5.2 Test API integration with mock responses
  - [ ] 5.3 Test error scenarios (network failure, invalid data)
  - [ ] 5.4 Add JSDoc comments to public functions
  - [ ] 5.5 Update README with profile editing feature documentation
```

## How Developer Uses This

1. **Reads task list** - Understands the full scope
2. **Starts with Task 1.0** - Works through parent tasks in order
3. **Checks off sub-tasks** - As each is completed
4. **References relevant files** - Knows exactly what files to create/modify
5. **Follows notes** - Uses existing components, runs tests

## Benefits

✅ **Clarity**: Junior developer knows exactly what to do
✅ **Order**: Logical sequence (data model → UI → validation → tests)
✅ **Context**: Identifies existing components to reuse
✅ **Testing**: Includes test tasks throughout
✅ **Documentation**: Notes provide helpful guidance

## Time Saved

- **Without agent**: 1-2 hours planning, possible missing items
- **With agent**: 5 minutes to generate comprehensive plan
- **Quality**: Consistent structure, nothing forgotten
