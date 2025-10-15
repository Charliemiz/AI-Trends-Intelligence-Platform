import { stackServerApp } from './server.js';

(async () => {
    try {
        const userId = process.argv[2];
        if (!userId) throw new Error('❌ Missing user ID. Usage: node server/gentoken.js <USER_ID>');

        const user = await stackServerApp.getUser(userId);
        if (!user) throw new Error('❌ No user found with that ID.');

        const session = await user.createSession();
        if (!session || !session.token) throw new Error('❌ Failed to create session token.');

        console.log('✅ Your JWT token:\n');
        console.log(session.token);
    } catch (err) {
        console.error('Error generating token:', err.message);
    }
})();
