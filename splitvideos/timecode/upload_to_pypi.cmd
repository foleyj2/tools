del *.pyc /S
..\Scripts\python setup.py clean --all
# ..\Scripts\python setup.py sdist upload
..\Scripts\python setup.py sdist bdist_wheel upload
