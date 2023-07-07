from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

cloud_config= {
  'secure_connect_bundle': "D:\class\Intern\ASTRA DB\secure-connect-ineuron.zip"
}
auth_provider = PlainTextAuthProvider('lRPtUZIivZvyTucximZIBTHb', 'GBh2+7DYia3FCv3u0txpmsjeIE_x3uM7DMFtzZ4pQU,UUp1k2RMx,oFS.Z0IdH3.9oRuIh0KZZFnc6+qStgHKGoPW-jqhd+liiPemRZXumG0+,DxSI1Ncm_.i1ynwQ8F')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

row = session.execute("select release_version from system.local").one()
if row:
  print(row[0])
else:
  print("An error occurred.")