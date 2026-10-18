from invoke import task


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
