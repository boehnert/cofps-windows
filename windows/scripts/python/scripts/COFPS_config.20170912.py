#!/usr/bin/env python
#
# Configuration file for CO-FPS system
#

from os import environ
from os.path import join
import platform

#
#
# Top-level directory to CO-FPS data. If env variable is not set, create
# a platform-specific default.
#
try:
    Cofps_root_dir = environ["COFPS_ROOT"]
except:
    if platform.system() == "Windows":
        Cofps_root_dir = "E:\cofireop"
    else:
        Cofps_root_dir = join("/data", "cofireop")

#
# Path names for main directories
#
Config_dir = join(Cofps_root_dir, "config")
Lock_dir = join(Cofps_root_dir, "lock")
Log_dir = join(Cofps_root_dir, "log")
Ncep_model_dir = join(Cofps_root_dir, "ncep_model")
Wps_dir = join(Cofps_root_dir, "wps")
Sim_dir = join(Cofps_root_dir, "sim")
Tmp_dir = join(Cofps_root_dir, "tmp")
Hrrr_dir = join(Cofps_root_dir, "hrrr")

#
# Subdirectory and file string patterns
#
Cawfe_base = "cawfe"
Config_vars_fname = "config_vars.txt"
Dt_pattern = "%Y-%m-%d_%H:%M:%S"
Fire_geometry_fname = "init.geo.json"
Gis_base = "gisdata"
Geo_grid_d01_fname = "geo_em.d01.nc"
Geo_grid_d02_fname = "geo_em.d02.nc"
Wps_base = "WPS"
Wrf_run_base = "run"
Wrf_out_fname = "wrfout_met_d01_"
Wrf_dt_pattern = "%s%s" % (Wrf_out_fname, Dt_pattern)

#
# Simulation management
#
Sim_mgr_pid_file = join(Lock_dir, "sim_mgr.pid")
Prod_mgr_pid_file = join(Lock_dir, "prod_mgr.pid")
Max_simulations = 3
Sim_update_interval = 5 # seconds
#Output_frequency = 15 # minutes
Output_frequency = 60 # minutes

#
# DB information
#
db_host = "cofps-int1"
db_port = 27017
db_name = "cofps"
db_user = "cofpsApp"
db_pwd = "T0rch1t!"
db_uri = "mongodb://%s:%s@%s:%d/%s" % (db_user, db_pwd, db_host, db_port, db_name)
#db_uri = "mongodb://cofps-int1:27017/"
db_simulations = "simulation"
db_pendingq = "pendingq"
db_runningq = "runningq"
db_polling_interval = 5 # seconds

#
# Data base token names
#
Dbt_alerts = "alerts"
Dbt_burnArea = "burnedAreaGeometries"
Dbt_byUser = "requestedByUser"
Dbt_complete = "completedOn"
Dbt_enqueued = "enqueueDate"
Dbt_fcstHrs = "fcstHours"
Dbt_fname = "name"
Dbt_heatArea = "activeHeatGeometries"
Dbt_domainCenter = "domainCenter"
Dbt_inner = "innerDomain"
Dbt_outer = "outerDomain"
Dbt_pausedBy = "pausedByUser"
Dbt_pausedOn = "pausedOn"
Dbt_percent = "percentComplete"
Dbt_prods = "products"
Dbt_requested = "requestedOn"
Dbt_simId  = "simulationId"
Dbt_status = "status"
Dbt_start = "startDateTime"
#
# Values used for status
#
Status_aborted   = "aborted"
Status_completed = "completed"
Status_failed    = "failed"
Status_running   = "running"
Status_paused    = "paused"
Status_resumed   = "resumed"
Status_waiting   = "waiting"
#
# ArcGIS Server names
#
Ags_usr = "admin"
Ags_pwd = "cofps-fire"
Ags_host = "cofps-web1.rap.ucar.edu"
Ags_host2 = "cofps-web2.rap.ucar.edu"
#Ags_mgt_port = 6080
Ags_mgt_port = 6443
