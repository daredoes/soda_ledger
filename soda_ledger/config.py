from soda_ledger import *

config = parse_config(__file__)
c.include_plugin_config(config)

c.ACCESS.update(c.SODA_ACCESS_LEVELS)
c.ACCESS_OPTS.extend(c.SODA_ACCESS_LEVEL_OPTS)
c.ACCESS_VARS.extend(c.SODA_ACCESS_LEVEL_VARS)
