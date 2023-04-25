{% if grains['fqdn'] == 'worker-1' %}
test: worker-1
role_id: MASTER
vir_id: 3
pri_id: 200
{% elif grains['fqdn'] == 'worker-2' %}
test: worker-2
role_id: BACKUP
vir_id: 4
pri_id: 100
{% endif %}
