hosts_init:
  file.managed:
    - name: /tmp/hosts
    - source: salt://files/hosts
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    
    {% if grains['fqdn'] == 'worker-1' %}
    - role: master
    {% elif grains['fqdn'] == 'worker-2' %}
    - role: backup
    {% endif %}
