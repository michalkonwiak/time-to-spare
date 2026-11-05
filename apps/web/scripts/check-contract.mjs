import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
const path = 'src/api/schema.d.ts';
const before = readFileSync(path, 'utf8');
try {
    execFileSync('npm', ['run', 'generate'], { stdio: 'inherit' });
    if (readFileSync(path, 'utf8') !== before) {
        throw new Error(
            'Generated API types drifted. Run npm run generate and commit the result.',
        );
    }
} finally {
    writeFileSync(path, before);
}
