import { stackServerApp } from '../server/server.js';

async function main() {
    const userId = process.argv[2];           // pass USER_ID on the command line
    if (!userId) throw new Error('Usage: node src/test.js <USER_ID>');
    const user = await stackServerApp.getUser(userId);
    console.log(user);
}

main().catch((e) => {
    console.error(e);
    process.exit(1);
});
