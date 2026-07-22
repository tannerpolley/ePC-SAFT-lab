# Cython HELD2 experiment

This isolated lab analysis probes whether CPython 3.13 can build and import a
Cython wheel using pinned `cppad_py` and `cyipopt` against the host CppAD and
Ipopt installations. It is experimental evidence only. It is not provider or
equilibrium runtime authority.

The first checkpoint exposes only `dependency_probe()`. It records a CppAD tape
for `x^2`, evaluates the tape and its Jacobian at 3, and imports `cyipopt`. A
failed upstream dependency build is an accepted terminal result and must not be
bypassed with a fork, patch, alternate Python interpreter, or substitute
AD/optimizer.

Build and install the wheel in an isolated environment:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install build pytest swig==4.4.1 \
  'setuptools>=80,<81' 'wheel>=0.45,<0.46' 'Cython>=3.1,<3.2'

# cppad_py 2024.8.15 expects CppAD under $HOME/prefix/cppad_py. The
# successful receipt used an isolated HOME whose include and library entries
# were symlinks to the system-owned /usr/include/cppad and libcppad_lib.so.
mkdir -p .build-home/prefix/cppad_py/include \
  .build-home/prefix/cppad_py/lib
ln -s /usr/include/cppad \
  .build-home/prefix/cppad_py/include/cppad
ln -s /usr/lib/x86_64-linux-gnu/libcppad_lib.so \
  .build-home/prefix/cppad_py/lib/libcppad_lib.so
PATH="$PWD/.venv/bin:$PATH" HOME="$PWD/.build-home" \
  .venv/bin/python -m pip install --no-build-isolation \
  'cppad_py @ git+https://github.com/bradbell/cppad_py.git@76331e8690ae5f3af88a9e3f25971b0f476e4518'
PKG_CONFIG_PATH=/usr/lib/pkgconfig .venv/bin/python -m pip install \
  'cyipopt @ git+https://github.com/mechmotum/cyipopt.git@86ba79ef5efc59386f4a371924312bc10df54c0c'

.venv/bin/python -m build --wheel
.venv/bin/python -m pip install --force-reinstall --no-deps \
  dist/cython_held2_experiment-0.0.1-cp313-cp313-linux_x86_64.whl
.venv/bin/python -m pytest -q tests/test_build_smoke.py
```

`--no-build-isolation` applies only to the pinned upstream `cppad_py` build so
its SWIG subprocess can use the venv-installed executable. It does not make the
experiment editable, patch the dependency, or compile against a local checkout.
The experiment wheel itself is built in an isolated PEP 517 environment.
