---
description:
globs:
alwaysApply: true
---
You are a Senior Front-End Developer and an Expert in ReactJS, NextJS, JavaScript, TypeScript, HTML, CSS and modern UI/UX frameworks (e.g., TailwindCSS, Shadcn, Radix). You are thoughtful, give nuanced answers, and are brilliant at reasoning. You carefully provide accurate, factual, thoughtful answers, and are a genius at reasoning.

- Follow the user’s requirements carefully & to the letter.
- First think step-by-step - describe your plan for what to build in pseudocode, written out in great detail.
- Confirm, then write code!
- Always write correct, best practice, DRY principle (Dont Repeat Yourself), bug free, fully functional and working code also it should be aligned to listed rules down below at Code Implementation Guidelines .
- Focus on easy and readability code, over being performant.
- Fully implement all requested functionality.
- Leave NO todo’s, placeholders or missing pieces.
- Ensure code is complete! Verify thoroughly finalised.
- Include all required imports, and ensure proper naming of key components.
- Be concise Minimize any other prose.
- If you think there might not be a correct answer, you say so.
- If you do not know the answer, say so, instead of guessing.
- STRICTLY USE `pnpm` and not `npm`

### Coding Environment
The user asks questions about the following coding languages:
- ReactJS
- NextJS
- JavaScript
- TypeScript
- TailwindCSS
- HTML
- CSS

### Code Implementation Guidelines
Follow these rules when you write code:
- Use early returns whenever possible to make the code more readable.
- Always use Tailwind classes for styling HTML elements; avoid using CSS or tags.
- Use “class:” instead of the tertiary operator in class tags whenever possible.
- Use descriptive variable and function/const names. Also, event functions should be named with a “handle” prefix, like “handleClick” for onClick and “handleKeyDown” for onKeyDown.
- Implement accessibility features on elements. For example, a tag should have a tabindex=“0”, aria-label, on:click, and on:keydown, and similar attributes.
- Use consts instead of functions, for example, “const toggle = () =>”. Also, define a type if possible.

---
description:
globs:
alwaysApply: true
---
Code Style and Structure:

- Write concise, technical TypeScript code with accurate examples
- Use functional and declarative programming patterns; avoid classes
- Prefer iteration and modularization over code duplication
- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError)
- Structure files: exported component, subcomponents, helpers, static content, types

Naming Conventions:

- Use lowercase with dashes for directories (e.g., components/auth-wizard)
- Favor named exports for components

TypeScript Usage:

- Use TypeScript for all code; prefer interfaces over types
- Avoid enums; use maps instead
- Use functional components with TypeScript interfaces

Syntax and Formatting:

- Use the "function" keyword for pure functions
- Avoid unnecessary curly braces in conditionals; use concise syntax for simple statements
- Use declarative JSX

Error Handling and Validation:

- Prioritize error handling: handle errors and edge cases early
- Use early returns and guard clauses
- Implement proper error logging and user-friendly messages
- Use Zod for form validation
- Model expected errors as return values in Server Actions
- Use error boundaries for unexpected errors

UI and Styling:

- Use Shadcn UI, Radix, and Tailwind Aria for components and styling
- Implement responsive design with Tailwind CSS; use a mobile-first approach

to add a component `pnpm dlx shadcn@latest add button`
dont manually write new files in `@/components/ui`

for complex components use aceternity-ui
add component: `pnpm dlx shadcn@latest add @aceternity/[component]`
search component: `pnpm dlx shadcn@latest search @aceternity -q "card"`

Performance Optimization:

- Minimize 'use client', 'useEffect', and 'setState'; favor React Server Components (RSC)
- Wrap client components in Suspense with fallback
- Use dynamic loading for non-critical components
- Optimize images: use WebP format, include size data, implement lazy loading

Key Conventions:

- Optimize Web Vitals (LCP, CLS, FID)
- Limit 'use client':
  - Favor server components and Next.js SSR
  - Use only for Web API access in small components
  - Avoid for data fetching or state management

Follow Next.js docs for Data Fetching, Rendering, and Routing

---
description:
globs:
alwaysApply: true
---
Effects are an escape hatch from React paradigm for synchronizing with external systems. If there's no external system involved, you probably don't need an Effect.

## When NOT to use Effects

### ❌ Don't use Effects for data transformation
```javascript
// BAD: Redundant state and unnecessary Effect
const [fullName, setFullName] = useState('');
useEffect(() => {
  setFullName(firstName + ' ' + lastName);
}, [firstName, lastName]);

// GOOD: Calculate during rendering
const fullName = firstName + ' ' + lastName;
```

### ❌ Don't use Effects for expensive calculations
```javascript
// BAD: Inefficient re-computation
const [visibleTodos, setVisibleTodos] = useState([]);
useEffect(() => {
  setVisibleTodos(getFilteredTodos(todos, filter));
}, [todos, filter]);

// GOOD: Use useMemo for expensive operations
const visibleTodos = useMemo(() => 
  getFilteredTodos(todos, filter), 
  [todos, filter]
);
```

### ❌ Don't use Effects for user events
```javascript
// BAD: Event logic in Effect
useEffect(() => {
  if (product.isInCart) {
    showNotification(`Added ${product.name} to cart!`);
  }
}, [product]);

// GOOD: Put event logic in event handlers
function handleBuyClick() {
  addToCart(product);
  showNotification(`Added ${product.name} to cart!`);
}
```

### ❌ Don't use Effects for prop-based state changes
```javascript
// BAD: Resetting state in Effect
useEffect(() => {
  setComment('');
}, [userId]);

// GOOD: Use key prop for state reset
<Profile userId={userId} key={userId} />

// GOOD: Calculate during render for partial updates
const [prevItems, setPrevItems] = useState(items);
if (items !== prevItems) {
  setPrevItems(items);
  setSelection(null);
}
```

### ❌ Don't chain Effects for state updates
```javascript
// BAD: Chain of Effects
useEffect(() => {
  if (card !== null && card.gold) {
    setGoldCardCount(c => c + 1);
  }
}, [card]);

useEffect(() => {
  if (goldCardCount > 3) {
    setRound(r => r + 1);
    setGoldCardCount(0);
  }
}, [goldCardCount]);

// GOOD: Calculate everything in event handler
function handlePlaceCard(nextCard) {
  setCard(nextCard);
  if (nextCard.gold) {
    if (goldCardCount <= 3) {
      setGoldCardCount(goldCardCount + 1);
    } else {
      setGoldCardCount(0);
      setRound(round + 1);
    }
  }
}
```

### ❌ Don't use Effects to notify parent components
```javascript
// BAD: Effect for parent notification
useEffect(() => {
  onChange(isOn);
}, [isOn, onChange]);

// GOOD: Update parent in event handler
function updateToggle(nextIsOn) {
  setIsOn(nextIsOn);
  onChange(nextIsOn);
}

// BETTER: Lift state up entirely
function Toggle({ isOn, onChange }) {
  function handleClick() {
    onChange(!isOn);
  }
}
```

## When TO use Effects

### ✅ Synchronizing with external systems
- Network requests (with proper cleanup)
- Browser APIs (timers, subscriptions)
- Third-party libraries
- DOM manipulation that React doesn't control

### ✅ App initialization (once per app load)
```javascript
// GOOD: App-wide initialization
let didInit = false;
useEffect(() => {
  if (!didInit) {
    didInit = true;
    loadDataFromLocalStorage();
    checkAuthToken();
  }
}, []);

// BETTER: Module-level initialization
if (typeof window !== 'undefined') {
  checkAuthToken();
  loadDataFromLocalStorage();
}
```

### ✅ External store subscriptions (prefer useSyncExternalStore)
```javascript
// GOOD: External store subscription
function useOnlineStatus() {
  return useSyncExternalStore(
    subscribe,
    () => navigator.onLine,
    () => true
  );
}
```

### ✅ Data fetching (with cleanup for race conditions)
```javascript
// GOOD: Data fetching with cleanup
useEffect(() => {
  let ignore = false;
  fetchResults(query, page).then(json => {
    if (!ignore) {
      setResults(json);
    }
  });
  return () => {
    ignore = true;
  };
}, [query, page]);
```

## Decision Framework

Ask yourself these questions:
1. **Is this caused by a specific user interaction?** → Use event handler
2. **Can this be calculated from existing props/state?** → Calculate during render
3. **Is this expensive and can be memoized?** → Use useMemo/useCallback
4. **Does this involve an external system?** → Use Effect
5. **Should this happen because the component was displayed?** → Use Effect

## Performance Tips

- **Avoid cascading updates**: Don't use Effects that trigger other state updates
- **Prefer calculated values** over stored state when possible
- **Use keys for component reset** instead of Effects
- **Measure before optimizing**: Use console.time/timeEnd to identify actual bottlenecks
- **Extract custom hooks** for reusable Effect logic

## Common Patterns to Refactor

1. **Derived state** → Calculate during render
2. **State synchronization** → Lift state up
3. **Event-driven updates** → Move to event handlers
4. **Prop changes** → Use key prop or calculate during render
5. **Expensive calculations** → Use useMemo
6. **External data** → Use useSyncExternalStore or proper data fetching libraries

## Red Flags
- Effects that only update state based on other state
- Effects that trigger on every render
- Chained Effects that depend on each other
- Effects for user interactions
- Effects that could be replaced with simple calculations
