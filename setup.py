from setuptools import setup, find_packages

setup(
    name='self-healing-agent',
    version='1.0.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    description='An AI agent for autonomous machine monitoring and self-remediation.',
    author='Diego Nogueira',
    author_email='diego@example.com',
    install_requires=[
        'psutil',
        'PyYAML',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-mock',
        ]
    }
) 