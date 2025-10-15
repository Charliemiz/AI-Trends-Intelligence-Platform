import { StackClientApp } from '@stackframe/js';

export const stack = new StackClientApp({
    projectId: import.meta.env.VITE_STACK_PROJECT_ID,
    publishableClientKey: import.meta.env.VITE_STACK_PUBLISHABLE_CLIENT_KEY,
});

// Fastest way to get a valid JWT
export async function signInAndGetJwt(email, password) {
    const result = await stack.signInWithCredential({
        email,
        password,
        noRedirect: true
    });

    if (result?.status === 'error') {
        throw new Error(result.error?.message || 'Sign-in failed');
    }

    const user = await stack.getUser();
    if (!user) throw new Error('User not found after sign-in');

    const { accessToken } = await user.getAuthJson();
    return accessToken;
}
