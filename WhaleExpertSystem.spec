# WhaleExpertSystem.spec
# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

a = Analysis(
    [os.path.join('app', 'main.py')],
    pathex=['app'],                      
    binaries=[],
    datas=[],
    hiddenimports=[
        'sqlalchemy.dialects.sqlite',
        'models',
        'models.base',
        'models.entities',
        'models.seed',
        'controllers',
        'controllers.species',
        'controllers.property',
        'controllers.value',
        'controllers.description',
        'controllers.assignment',
        'controllers.completeness',
        'controllers.solver',
        'views',
        'views.role_selector',
        'views.editor',
        'views.editor.editor',
        'views.editor.species',
        'views.editor.properties',
        'views.editor.values',
        'views.editor.description',
        'views.editor.assignment',
        'views.editor.completeness',
        'views.solver',
        'views.solver.solver',
        'controllers.ml_classifier',
        'sklearn',
        'sklearn.ensemble',
        'sklearn.ensemble._forest',
        'sklearn.tree',
        'sklearn.tree._classes',
        'sklearn.preprocessing',
        'sklearn.utils',
        'sklearn.utils._cython_blas',
        'sklearn.utils._typedefs',
        'sklearn.neighbors._typedefs',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='WhaleExpertSystem',
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    icon=None,
)