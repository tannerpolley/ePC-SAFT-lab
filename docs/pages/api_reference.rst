API Reference
=============

The reset provider API is intentionally small. Import these names from
``epcsaft``:

- ``Mixture``
- ``State``
- ``ParameterSet``
- ``ModelOptions``
- ``create_input_template``
- ``provider_native_sdk``

Import equilibrium workflows from ``epcsaft_equilibrium`` and regression
workflows from ``epcsaft_regression``. Native bridge modules are internal
implementation details.

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

.. autoclass:: epcsaft_equilibrium.Equilibrium
   :members:
   :undoc-members:
   :no-index:

The trusted public neutral two-phase proof set is
``Equilibrium(mixture, route=..., ...).solve()`` with route specs
``bubble_pressure``, ``dew_pressure``, and scoped nonassociating hydrocarbon
``single_component_vle`` with native Ipopt and exact Hessian callbacks. Neutral
LLE remains internal because its sampled-candidate Stage II audit is not a
global HELD proof. The VLE ``x`` and ``y`` conveniences remain limited to
liquid/vapor routes.

Regression
----------

.. autoclass:: epcsaft_regression.Regression
   :members:
   :undoc-members:
   :no-index:

The trusted public regression proof is
``Regression(mixture, ...).fit_pure_neutral(...)`` from ``epcsaft_regression``
for the hydrocarbon
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

.. autofunction:: epcsaft.provider_native_sdk

.. autofunction:: epcsaft.capabilities
