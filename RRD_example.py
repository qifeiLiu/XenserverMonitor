#!/usr/bin/env python

import time
import XenAPI
import parse_rrd

def print_latest_host_data(rrd_updates):
    host_uuid = rrd_updates.get_host_uuid()
    print("**********************************************************")
    print("Got values for Host: "+host_uuid)
    print ("**********************************************************")

    for param in rrd_updates.get_host_param_list():
        if param != "":
            max_time=0
            data=""
            for row in range(rrd_updates.get_nrows()):
                 epoch = rrd_updates.get_row_time(row)
                 dv = str(rrd_updates.get_host_data(param,row))
                 if epoch > max_time:
                     max_time = epoch
                     data = dv
            nt = time.strftime("%H:%M:%S", time.localtime(max_time))
            print("%-30s             (%s , %s)" % (param, nt, data))


def print_latest_vm_data(rrd_updates, uuid):
    print("**********************************************************")
    print ("Got values for VM: "+uuid)
    print ("**********************************************************")
    for param in rrd_updates.get_vm_param_list(uuid):
        if param != "":
            max_time=0
            data=""
            for row in range(rrd_updates.get_nrows()):
                epoch = rrd_updates.get_row_time(row)
                dv = str(rrd_updates.get_vm_data(uuid,param,row))
                if epoch > max_time:
                    max_time = epoch
                    data = dv
            nt = time.strftime("%H:%M:%S", time.localtime(max_time))
            print("%-30s             (%s , %s)" % (param, nt, data))

def build_vm_graph_data(rrd_updates, vm_uuid, param):
    time_now = int(time.time())
    for param_name in rrd_updates.get_vm_param_list(vm_uuid):
        if param_name == param:
            data = "#%s  Seconds Ago" % param
            for row in range(rrd_updates.get_nrows()):
                epoch = rrd_updates.get_row_time(row)
                data = str(rrd_updates.get_vm_data(vm_uuid, param_name, row))
                data += "\n%-14s %s" % (data, time_now - epoch)
            return data

def main():
    url = "http://10.108.8.93"
    session = XenAPI.Session(url)
    session.xenapi.login_with_password('root','VVTLiuztTP3F')

    rrd_updates = parse_rrd.RRDUpdates()
    params = {}
    params['cf'] = "AVERAGE"
    params['start'] = int(time.time()) - 10
    params['interval'] = 5
    params['host'] = "true"
    rrd_updates.refresh(session.handle, params, url)

    if params['host'] == 'true':
        print_latest_host_data(rrd_updates)

    for uuid in rrd_updates.get_vm_list():
        print_latest_vm_data(rrd_updates, uuid)
        param = 'cpu0'
        data = build_vm_graph_data(rrd_updates, uuid, param)
        fh = open("%s-%s.dat" % (uuid, param), 'w')
        fh.write(data)
        fh.close()

main()