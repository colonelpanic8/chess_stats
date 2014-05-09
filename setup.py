from distutils.core import setup

setup(
    name='ChessStats',
    version='0.1.0',
    author='Ivan Malison',
    author_email='IvanMalison@gmail.com',
    packages=['chess_stats'],
    license='LICENSE.txt',
    description='Website that interfaces with chess.com to provide satatistics.',
    long_description=open('README.txt').read(),
    install_requires=[],
)
