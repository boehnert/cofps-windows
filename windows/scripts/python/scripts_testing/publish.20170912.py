#!/usr/bin/env python
"""
This is a driver script to run Jennifer's publishing script.
"""


import os
import sys
import shutil
import time
import datetime
import glob
import fileinput
import traceback
import cPickle
from stat import *
from optparse import OptionParser
from pymongo import MongoClient
from pymongo import errors as mongoerrors


def productListIsOk(flist, lp):
    """ ensures the files in flist exist and are not currently being written to"""
    if not os.path.exists(flist):
        return 0
    curtime = time.time()
    with open(flist) as fd:
        plist = fd.read().splitlines()
    for p in plist:
        # each entry has: timestep,date/time,file
        if len(p) != 3: # ignore entries with no date/time field
            continue
        f = p.split(',')[-1]
        if not os.path.exists(f):
            log(lp, "%s does not exist" % (f))
            return 0
        if os.stat(f).st_mtime >= curtime:
            log(lp, "%s not finished, curtime %d, mtime %d" % (f, curtime, os.stat(f).st_mtime))
            return 0
    return 1


def get_full_log_path(base):
    """get path of log file"""
    if base == None:
        return None
    
    dt = datetime.datetime.utcnow()
    d = dt.strftime("%Y%m%d")
    path = "%s.%s.log" % (base, d)
    return path


def log(base, string):
    """write string to a dated log file starting with base"""
    logpath = get_full_log_path(base)
    dt = datetime.datetime.utcnow()
    t = dt.strftime("%H:%M:%S")
    if logpath == None:
        print "%s %s" % (t, string)
    else:
        f = open(logpath, 'a')
        f.write("%s %s\n" % (t, string))
        f.close()


def isRecent(dt_str, secs):
    """determines if input time string is within sec seconds of current time"""
    if dt_str == None:
        return 0
    dt = datetime.datetime.strptime(dt_str[:19],"%Y-%m-%dT%H:%M:%S")
    dt_now = datetime.datetime.utcnow()
    diff = int((dt_now-dt).total_seconds())
    if diff > secs:
        return 0
    else:
        return 1


def make_iso8601(dt):
    """converts YYYY-MM-DD HH:MM:SS string into iso8601 format"""
    return "%sT%s.000Z" % (dt[:10], dt[11:19])


def run(cf, lp):
    """Function that watches the database and runs the publishing script"""
    log(lp, "Starting...")

    # prod_list_fn = file containing list of products from the simulation.
    # Created externally by Kevin's product generation script(s).
    prod_list_fn = "product_list.txt"

    # pub_prods_fn - file containing list of products to publish, created
    # here and used by Jenn's publishing script.
    prods_to_pub_fn = "products_to_publish.txt"

    # pub_prod_list_fn = file containing list of published products. This is
    # a copy of prod_list_fn created here when publishing is successful.
    pub_prod_list_fn = "published_product_list.txt"

    # publish_list_fn - pickle file containing products that were published.
    # Created by Jenn's publishing script.
    publish_list_fn = "publish_list.pkl"

    # how far back (seconds) to look for publishable products
    lookback_secs = 604800

    log(lp, "connecting to mongo_db")
    sim_db = MongoClient(cf.db_uri,connect=False)[cf.db_name][cf.db_simulations]

    while (1):

        try:
            docs = sim_db.find()
        except mongoerrors.PyMongoError:
            log(lp, "error getting documents from database")
            docs = []

        for d in docs:
            try:
                sim_id = d[cf.Dbt_simId]
                fire_name = d[cf.Dbt_fname]
                status = d[cf.Dbt_status]
                completed_on = d[cf.Dbt_complete]
                pct_complete = d[cf.Dbt_percent]
                fcst_hours = d[cf.Dbt_fcstHrs]
                prod_expected_secs = int(round(pct_complete/100. * fcst_hours)) * 3600
                product_list = d[cf.Dbt_prods]
                if len(product_list) > 0:
                    # use last field's lead time - the first field (Fire Boundary) has a bad lead time
                    prod_complete_secs = product_list[-1]['leadTimeInSeconds']
                else:
                    prod_complete_secs = 0
            except:
                log(lp, "error getting document entries")
                log(lp, "(for sim_id %s)" % (sim_id))
                continue


            #log(lp, 'sim_id %s:' % sim_id)
            #log(lp, '    status %s, fcst hrs %d, sim pct complete %.2f, prod expected %d, prod complete %d' % \
            #        (status, fcst_hours, pct_complete, prod_expected_secs, prod_complete_secs))
           

            # process actively running or completed simulations with incomplete products
            if status == cf.Status_running:
                pass
            elif status == cf.Status_completed and prod_complete_secs < prod_expected_secs:
                pass
            else:
                continue

            log(lp, "checking for new products for simulation %s" % (sim_id))

            # process products if:
            # 1) there is no published list file, or
            # 2) product list file is larger than the existing published file
            
            sim_dir = os.path.join(cf.Sim_dir, cf.Gis_base, fire_name, sim_id)
            pl_path = os.path.join(sim_dir, prod_list_fn)
            pub_pl_path = os.path.join(sim_dir, pub_prod_list_fn)

            if (os.path.exists(pl_path) and os.path.getsize(pl_path) > 0 and not os.path.exists(pub_pl_path)) \
                or (os.path.exists(pl_path) and os.path.exists(pub_pl_path) and \
                os.path.getsize(pl_path) > os.path.getsize(pub_pl_path)):

                # Ensure the products are ready (synced)
                if not productListIsOk(pl_path, lp):
                    log(lp, "products not yet complete in %s" % (pl_path))
                    continue

                # make a copy of the product list file to use during publishing
                #shutil.copy(pl_path, pub_pl_path)
                prods_to_pub_path = os.path.join(sim_dir, prods_to_pub_fn)
                log(lp, "executing: cp %s %s" % (pl_path, prods_to_pub_path))
                shutil.copy(pl_path, prods_to_pub_path)

                # remove any existing pkl file
                pub_out_path = os.path.join(sim_dir, publish_list_fn)
                if os.path.exists(pub_out_path):
                    os.remove(pub_out_path)

                # run the publishing script and update the database with results
                cmdout = os.path.join(sim_dir, "readFile.log")
                cmd = "python readFile.py %s >> %s 2>&1" % (prods_to_pub_path, cmdout)
                log(lp, "executing: %s" % (cmd))
                ret = os.system(cmd)
                if ret != 0:
                    log(lp, "error running command")
                    continue
                elif not os.path.exists(pub_out_path):
                    log(lp, "error - no output pkl file produced")
                    continue

                log(lp, "loading product list from %s" % (pub_out_path))
                try:
                    f = open(pub_out_path)
                    products = cPickle.load(f)
                    f.close()
                    # change startDateTime to the ISO 8601 format.
                    for i in xrange(len(products)):
                        dt = make_iso8601(products[i]['startDateTime'])
                        products[i]['startDateTime'] = dt
                except:
                    log(lp, "error loading pickled product list")
                    continue

                log(lp, "updating products in database for %s %s" % (fire_name, sim_id))
                try:
                    sim_db.update({cf.Dbt_simId: sim_id}, {"$set": {cf.Dbt_prods: products}},w=0)
                except mongoerrors.PyMongoError:
                    log(lp, "error updating products in the database")
                    continue

                # Successful! Copy published products file
                log(lp, "executing: cp %s %s" % (prods_to_pub_path, pub_pl_path))
                shutil.copy(prods_to_pub_path, pub_pl_path)


        #log(lp, "finished checking simulations, sleeping...")
        sys.stdout.flush()
        time.sleep(cf.db_polling_interval)

    log(lp, "Ending.")


def main():
    usage_str = "%prog config"
    parser = OptionParser(usage = usage_str)
    parser.add_option("-l", "--log", dest="log", help="write log messages to specified file")
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(2)

    try:
        cf = __import__(args[0], globals(), locals(), [])
    except:
        print "Error importing config file. Perhaps omit '.py' part of file?"
        sys.exit(2)


    while(1):
        try:
            run(cf, options.log)
        except:
            log(options.log, "Error: unexpected failure in run() method, traceback follows:")
            logpath = get_full_log_path(options.log)
            if logpath == None:
                traceback.print_exc(file=sys.stdout)
            else:
                fp = open(logpath, 'a')
                traceback.print_exc(file=fp)
                fp.close()
            

    sys.exit(0)



if __name__ == "__main__":

    main()
