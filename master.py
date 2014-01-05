#
# The real configuration goes in this file
#
print("** loading", __file__, "as", __name__)

from builders import get_builders
from schedulers import get_schedulers
from slaves import get_slaves
from status import status_targets

slave_list = get_slaves()

builder_list, builder_names = get_builders()

scheduler_list = get_schedulers(builder_names)

slave_list = get_slaves()

BuildmasterConfig = {
    "schedulers": scheduler_list,

    "builders": builder_list,

    "status": status_targets,

    "slavePortnum": 9989,
    "slaves": slave_list,
    
    "title": "MultiMC",
    "titleURL": "http://multimc.org/",
    "buildbotURL": "http://ci.multimc.org/",
    "db": { "db_url" : "sqlite:///state.sqlite" }
}

