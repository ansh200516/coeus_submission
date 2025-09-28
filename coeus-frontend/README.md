This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Voice Interface Components

This project includes several voice interface components that can be used to visualize speech activity:

### Main Voice Interface Component

- **VoiceInterface**: A complete voice interface component that uses the PrismaticVoiceIndicator for beautiful visual effects. This is the recommended component for production use.

### Voice Indicator Components

- **SimpleVoiceIndicator**: A minimal circle that changes color and size based on voice state
- **VoiceIndicator**: A circle with ripple effects that visualize speech activity
- **PrismaticVoiceIndicator**: An advanced visualization with prismatic effects

All components work with the `useVoiceStream` hook to visualize different voice states:
- **idle**: Default state when no voice activity is detected
- **listening**: When the user is speaking
- **speaking**: When the AI is speaking
- **processing**: When the system is processing input

### Demo

Check out these demos to see the components in action:
- `/voice-interface` - Main VoiceInterface component with customization options
- `/voice-indicator-demo` - All voice indicator components

## Getting Started

First, run the development server:

```bash
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
