import { spawn } from 'child_process';

const py = spawn('python3', ['backend/manage.py', 'runserver', '0.0.0.0:3000'], {
  stdio: 'inherit'
});

py.on('exit', (code) => {
  process.exit(code || 0);
});
