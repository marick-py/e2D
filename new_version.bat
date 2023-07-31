python new_version.py
python -m build
python -m twine upload -u ma.rick --skip-existing --repository pypi dist/*
pause