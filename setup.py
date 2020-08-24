from distutils.core import setup


setup(
    name='PDF Compare',
    version='1.0.0',
    scripts=['bin/pdf-compare.py'],
    license='MIT',
    description='Takes two PDF inputs and does a pixel compare to output an image-per-page delta.',
    long_description=open('README.rst').read(),
    install_requires=[
        'pdf2image >= 1.14.0',
        'pillow >= 7.2.0'
    ],
)
