API Reference
=============

The reset public API is intentionally small. Import these names from
``epcsaft``:

- ``Mixture``
- ``State``
- ``Equilibrium``
- ``Regression``
- ``ParameterSet``
- ``ModelOptions``
- ``create_input_template``

Legacy root exports such as ``ePCSAFTMixture``, ``ePCSAFTState``,
``bubble_p``, ``dew_p``, and free regression helpers are no longer public API.
Internal native bridge modules may still use those names while the remaining
native routes are ported behind the reset frontend.

Mixture
-------

.. autoclass:: epcsaft.Mixture
   :members:
   :undoc-members:
   :no-index:

State
-----

.. autoclass:: epcsaft.State
   :members:
   :undoc-members:
   :no-index:

``State`` owns temperature, pressure or density closure, composition, and phase.
It exposes common property names such as ``z()``, ``ares()``, ``hres()``,
``sres()``, ``gres()``, and residual Helmholtz contribution helpers.

Equilibrium
-----------

.. autoclass:: epcsaft.Equilibrium
   :members:
   :undoc-members:
   :no-index:

The trusted public neutral VLE proof set is
``Equilibrium(mixture, ...).solve(route=..., ...)`` with route specs
``bubble_pressure``, ``bubble_temperature``, ``dew_pressure``,
``dew_temperature``, and certified two-phase ``flash`` with native Ipopt and
exact Hessian callbacks.

Regression
----------

.. autoclass:: epcsaft.Regression
   :members:
   :undoc-members:
   :no-index:

The trusted public regression proof is
``Regression(mixture, ...).fit_pure_neutral(...)`` for the hydrocarbon
Gross/Sadowski anchor.

Parameters And Model Options
----------------------------

.. autoclass:: epcsaft.ParameterSet
   :members:
   :undoc-members:
   :no-index:

.. autoclass:: epcsaft.ModelOptions
   :members:
   :undoc-members:
   :no-index:

``ParameterSet`` stores ePC-SAFT parameter data. ``ModelOptions`` belongs to
``Mixture`` and selects formulation choices such as the relative-permittivity
mixture rule and Born-family variants.

Input Templates
---------------

.. autofunction:: epcsaft.create_input_template

Runtime Metadata
----------------

.. autofunction:: epcsaft.runtime_build_info

.. autofunction:: epcsaft.capabilities
