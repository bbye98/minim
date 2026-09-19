{{ objname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :inherited-members:
   :undoc-members:
   :show-inheritance:

   {% set public_methods = [] %}
   {% for item in methods %}
      {% if not item.startswith('_') %}
         {% set _ = public_methods.append(item) %}
      {% endif %}
   {% endfor %}

   {% if public_methods %}
   .. rubric:: {{ _('Methods') }}

   .. autosummary::
      :nosignatures:
   {% for item in public_methods %}
      ~{{ name }}.{{ item }}
   {% endfor %}
   {% endif %}

   {% set public_attributes = [] %}
   {% for item in attributes %}
      {% if not item.startswith('_') %}
         {% set _ = public_attributes.append(item) %}
      {% endif %}
   {% endfor %}

   {% if public_attributes %}
   .. rubric:: {{ _('Attributes') }}

   .. autosummary::
      :nosignatures:
      :template: autosummary/class.rst
   {% for item in public_attributes %}
      ~{{ name }}.{{ item }}
   {% endfor %}
   {% endif %}