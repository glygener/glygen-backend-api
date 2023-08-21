srv="prd"
#srv="beta"
srv="tst"

#mod=substructure
#mod="mongo"
mod="api"

sudo systemctl stop docker-glygen-$mod-$srv.service
python3 create_"$mod"_container.py -s $srv
sudo systemctl start docker-glygen-$mod-$srv.service


