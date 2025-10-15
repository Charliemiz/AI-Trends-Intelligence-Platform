import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { StackServerApp } from '@stackframe/js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load from frontend/.env.local (and fallback to .env)
dotenv.config({
    path: [
        path.resolve(__dirname, '../.env.local'),
        path.resolve(__dirname, '../.env'),
    ],
});


export const stackServerApp = new StackServerApp({
    projectId: process.env.STACK_PROJECT_ID,
    publishableClientKey: process.env.STACK_PUBLISHABLE_CLIENT_KEY,
    secretServerKey: process.env.STACK_SECRET_SERVER_KEY,
    tokenStore: 'memory',
});
