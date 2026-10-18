import subprocess
import sys

from invoke import Exit, task


@task
def start(c):
    "invoke start"
    c.run('flask --app app.py run')


@task
def start_debug(c):
    "invoke start-debug"
    c.run('flask --app app.py run --debug')


@task
def gui(c):
    "invoke gui"
    c.run('python wsigils.pyw')


@task
def tui(c):
    "invoke tui"
    # Run directly rather than via c.run: Textual needs the real console, and invoke
    # pipes output (pty=True isn't supported on Windows).
    returncode = subprocess.run([sys.executable, 'tsigils.py']).returncode
    if returncode:
        raise Exit(code=returncode)


@task
def lint(c):
    "invoke lint"
    c.run('flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics')
    c.run('flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics')


@task(help={
    'verbose': 'Show verbose test output (-v flag)',
    'failfast': 'Stop on first failure (-x flag)',
    'keyword': 'Only run tests matching this expression (-k flag)'
})
def test(c, verbose=False, failfast=False, keyword=None):
    """Run pytest unit tests"""
    command = ['pytest']
    if verbose:
        command.append('-v')
    if failfast:
        command.append('-x')
    if keyword:
        command.append(f'-k "{keyword}"')

    c.run(' '.join(command))
