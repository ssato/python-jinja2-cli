simple variable expansions:

* {{ a }}
* {{ b.b0 }}
* {{ c.c0.c1 }}

for loop:

{% for x in xs %}* {{ x.y.z }}
{% endfor %}


{% if include_tmpl is defined %}
if statement:

* {% if bool_x %}bool_x == True{% else %}bool_x == False{% endif %}

include statement:

{% include "a.includee.t" %}

macro: {% macro hello(world='world') %}"Hello, {{ world }}!"{% endmacro %}

* hello(): {{ hello() }}
* hello('foobar'): {{ hello('foobar') }}

{% endif %}

{% if include_renamed_tmpl is defined %}{% include "b.includee.t" %}{% endif %}
